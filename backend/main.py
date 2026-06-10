"""
main.py
=======
MRW2 Prototype – FastAPI REST Server (port 8000)

Startup:
    uvicorn backend.main:app --reload --port 8000

Endpoints:
    GET  /api/users
    GET  /api/words
    GET  /api/recommend?user_id=<id>&method=<content|svd|autoencoder|hybrid>
    POST /api/interact  Body: {user_id, word_id, rating}
"""

from __future__ import annotations
import os
import sys
import numpy as np

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── allow running from repo root as `uvicorn backend.main:app` ──
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_simulator import generate_dataset, CEFR_INDEX
from backend.recommenders   import build_all_recommenders

# ─────────────────────────────────────────────
# Application setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="MRW2 – Personalized Vocabulary Recommender API",
    description=(
        "Experimental prototype for evaluating Content-Based, SVD, "
        "Autoencoder, and Hybrid recommender systems for vocabulary learning."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# In-memory state – populated on startup
# ─────────────────────────────────────────────
_state: dict = {}


@app.on_event("startup")
async def _startup() -> None:
    """Build dataset and train all models once at server start."""
    print("[startup] Generating dataset …")
    users, words, rating_matrix = generate_dataset()

    print("[startup] Training recommender engines …")
    rec_bundle = build_all_recommenders(users, words, rating_matrix)

    _state["users"]         = users
    _state["words"]         = words
    _state["rating_matrix"] = rating_matrix   # mutable; updated on POST /interact
    _state["engines"]       = rec_bundle["engines"]
    _state["metrics"]       = rec_bundle["metrics"]
    _state["word_index"]    = {w["word_id"]: i for i, w in enumerate(words)}
    _state["user_index"]    = {u["user_id"]: i for i, u in enumerate(users)}

    # Pre-populate custom interactions from the rating matrix for active users
    custom_interactions = {}
    for u in users:
        u_id = u["user_id"]
        custom_interactions[u_id] = []
        u_idx = _state["user_index"].get(u_id)
        if not u["is_cold_start"] and u_idx < rating_matrix.shape[0]:
            rated_indices = np.where(rating_matrix[u_idx] > 0)[0]
            for w_idx in rated_indices:
                custom_interactions[u_id].append({
                    "word": {
                        "word_id": words[w_idx]["word_id"],
                        "word": words[w_idx]["word"],
                        "cefr_difficulty": words[w_idx]["cefr_difficulty"],
                        "part_of_speech": words[w_idx]["part_of_speech"]
                    },
                    "rating": int(rating_matrix[u_idx, w_idx]),
                    "time": "Prior Session"
                })
    _state["custom_interactions"] = custom_interactions

    print(f"[startup] Ready – {len(users)} users, {len(words)} words")


# ─────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────
class InteractRequest(BaseModel):
    user_id: int  = Field(..., ge=1, le=105, description="User ID (1-100 active, 101-105 cold-start)")
    word_id: int  = Field(..., ge=1, le=300, description="Word ID (1-300)")
    rating:  float = Field(..., ge=1.0, le=5.0, description="Rating 1 (unknown) to 5 (mastered)")


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "MRW2 Vocabulary Recommender API is running",
        "docs":    "http://localhost:8000/docs",
    }


@app.get("/api/users")
async def get_users():
    """
    Returns all 105 mock users.
    Each record includes: user_id, name, cefr_level, is_cold_start.
    Cold-start users (101-105) have cefr_level=null.
    """
    return {"users": _state["users"]}


@app.get("/api/words")
async def get_words():
    """
    Returns the full 300-word vocabulary dictionary.
    Each record: word_id, word, cefr_difficulty, part_of_speech.
    """
    return {"words": _state["words"]}


@app.get("/api/recommend")
async def get_recommendations(
    user_id: int   = Query(..., ge=1, le=105, description="User ID"),
    method:  str   = Query("hybrid", description="content | svd | autoencoder | hybrid"),
    top_n:   int   = Query(5, ge=1, le=20, description="Number of results"),
):
    """
    Returns top-N recommended vocabulary items for the given user using the
    selected algorithm, plus the algorithm's evaluation metrics.

    Already-rated words are excluded from results.
    Cold-start users (101-105) automatically use Content-Based fallback for
    SVD, Autoencoder, and Hybrid methods.
    """
    valid_methods = {"content", "svd", "autoencoder", "hybrid"}
    if method not in valid_methods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid method '{method}'. Choose from: {sorted(valid_methods)}",
        )

    user_idx = _state["user_index"].get(user_id)
    if user_idx is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")

    engine      = _state["engines"][method]
    matrix      = _state["rating_matrix"]
    users       = _state["users"]

    # For cold-start users (no row in rating matrix), pass a zero row
    if users[user_idx]["is_cold_start"]:
        # Temporarily extend or use a zero vector
        recs = engine.recommend(user_idx, matrix, users, top_n=top_n)
    else:
        recs = engine.recommend(user_idx, matrix, users, top_n=top_n)

    metrics = _state["metrics"].get(method, {})

    # Build user interaction log history
    interaction_log = _state["custom_interactions"].get(user_id, [])
    rated_count = len(interaction_log)

    return {
        "user_id":     user_id,
        "method":      method,
        "is_cold_start": users[user_idx]["is_cold_start"],
        "rated_words": rated_count,
        "metrics":     metrics,
        "recommendations": recs,
        "interaction_log": interaction_log,
    }


@app.post("/api/interact")
async def post_interact(body: InteractRequest):
    """
    Records or updates a user's rating for a word.
    Updates the in-memory rating matrix so subsequent recommendations reflect
    the new interaction (simulates real-time profile update).

    Returns the updated interaction count for the user.
    """
    user_idx = _state["user_index"].get(body.user_id)
    word_idx = _state["word_index"].get(body.word_id)

    if user_idx is None:
        raise HTTPException(status_code=404, detail=f"User {body.user_id} not found.")
    if word_idx is None:
        raise HTTPException(status_code=404, detail=f"Word {body.word_id} not found.")

    user = _state["users"][user_idx]
    word = _state["words"][word_idx]

    from datetime import datetime
    time_str = datetime.now().strftime("%I:%M:%S %p")

    # Update or append in custom_interactions
    user_id = body.user_id
    if user_id not in _state["custom_interactions"]:
        _state["custom_interactions"][user_id] = []

    existing_interaction = None
    for interaction in _state["custom_interactions"][user_id]:
        if interaction["word"]["word_id"] == body.word_id:
            existing_interaction = interaction
            break

    if existing_interaction:
        existing_interaction["rating"] = int(body.rating)
        existing_interaction["time"] = time_str
    else:
        _state["custom_interactions"][user_id].append({
            "word": {
                "word_id": word["word_id"],
                "word": word["word"],
                "cefr_difficulty": word["cefr_difficulty"],
                "part_of_speech": word["part_of_speech"]
            },
            "rating": int(body.rating),
            "time": time_str
        })

    # Cold-start users don't have a row in the rating matrix.
    # On first interaction, they get activated as an active user by
    # assigning a default CEFR level inferred from the rated word.
    if user["is_cold_start"]:
        # Infer a starting CEFR from the word being rated
        word_cefr = word["cefr_difficulty"]
        cefr_idx  = CEFR_INDEX[word_cefr]
        # Set user CEFR to the word's level (or lower if just rating=1)
        inferred_cefr = ["A1", "A1", "A2", "B1", "B2", "C1"][min(5, max(0, cefr_idx - 1 if body.rating <= 2 else cefr_idx))]
        _state["users"][user_idx]["cefr_level"] = inferred_cefr
        return {
            "status":   "interaction recorded (cold-start user – profile inferred)",
            "user_id":  body.user_id,
            "word_id":  body.word_id,
            "rating":   body.rating,
            "inferred_cefr": inferred_cefr,
            "rated_words": len(_state["custom_interactions"][user_id]),
        }

    # Active user – update matrix directly
    _state["rating_matrix"][user_idx, word_idx] = body.rating

    return {
        "status":   "interaction recorded",
        "user_id":  body.user_id,
        "word_id":  body.word_id,
        "rating":   body.rating,
        "rated_words": len(_state["custom_interactions"][user_id]),
    }
