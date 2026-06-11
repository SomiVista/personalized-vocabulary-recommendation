# VocabAI Recommender

**An Experimental Evaluation of Personalized Recommender Systems for Vocabulary Learning in AI-Driven Language Education Platforms**

> Master's Research · Vilnius Gediminas Technical University  
> Somayeh Roohani · Supervisor: Prof. Dr. Irina Vinogradova-Zinkevič

---

## Overview

A full-stack research prototype that compares four recommendation algorithms for personalized English vocabulary learning. Users are profiled by CEFR level (A1–C2), and the system recommends the five most appropriate words to study next based on their interaction history.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI · scikit-learn · PyTorch |
| Frontend | Vue 3 (Composition API) · Vite · Vanilla CSS |
| Communication | REST/JSON (`/api/*`) proxied by Vite dev server |

---

## Project Structure

```
personalized-vocabulary-recommendation/
├── backend/
│   ├── data_simulator.py   # Generates 105 users, 300 words, sparse rating matrix
│   ├── recommenders.py     # 4 engines: CBF · SVD · Autoencoder · Hybrid
│   ├── main.py             # FastAPI server — trains all models on startup
│   └── requirements.txt
└── frontend/
    ├── vite.config.js
    └── src/
        ├── App.vue                     # Root layout, state, API calls, word drawer
        ├── style.css                   # Global design tokens & utilities
        └── components/
            ├── UserSelector.vue        # Searchable learner profile picker
            ├── AlgorithmSelector.vue   # CBF / SVD / Autoencoder / Hybrid tabs
            ├── MetricsCard.vue         # RMSE, Precision@5, Coverage display
            ├── ChartsPanel.vue         # Radar, bar, and score distribution charts
            ├── RecommendationTable.vue # Top-5 table with session mastery counter
            └── WordInteractionRow.vue  # Per-word row: flashcard, XAI tooltip,
                                        # audio settings, confetti on mastery
```

---

## Quick Start

**Prerequisites:** Python 3.10+ and Node.js 18+

### Terminal 1 — Backend

```bash
cd personalized-vocabulary-recommendation

python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r backend/requirements.txt

uvicorn backend.main:app --reload --port 8000
```

> ✅ Ready when the console prints: `[startup] Ready – 105 users, 300 words`  
> 📖 Interactive API docs: <http://localhost:8000/docs>

### Terminal 2 — Frontend

```bash
cd personalized-vocabulary-recommendation/frontend

npm install
npm run dev
```

> ✅ Open <http://localhost:5173> in your browser.

---

## Dataset

| Property | Value |
|---|---|
| Active users | 100 (CEFR A1–C2, weighted toward B1/B2) |
| Cold-start users | 5 (IDs 101–105, no interaction history) |
| Vocabulary | 300 English words · 50 per CEFR level |
| Rating matrix | 100 × 300 sparse · ~8% density · ratings 1–5 |

---

## Recommendation Engines

| # | Method | Cold-Start | Weight / Config |
|---|---|---|---|
| 1 | **Content-Based Filtering (CBF)** | ✅ Native | TF-IDF cosine similarity on CEFR + POS features |
| 2 | **SVD Collaborative Filtering** | ⚠ CBF fallback | 20 latent factors (TruncatedSVD) |
| 3 | **Deep Autoencoder** | ⚠ CBF fallback | 300 → 64 → 32 → 64 → 300 (PyTorch CPU) |
| 4 | **Hybrid (proposed)** | ✅ Via CBF | `0.40 × CBF + 0.35 × SVD + 0.25 × AE` (min-max normalized) |

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/users` | GET | All 105 user profiles |
| `/api/words` | GET | Full 300-word dictionary |
| `/api/recommend?user_id=1&method=hybrid` | GET | Top-5 recommendations + evaluation metrics |
| `/api/interact` | POST | Record interaction `{ user_id, word_id, rating }` |

```bash
# Hybrid recommendations for user 1
curl "http://localhost:8000/api/recommend?user_id=1&method=hybrid" | python3 -m json.tool

# Cold-start user (auto-falls back to CBF)
curl "http://localhost:8000/api/recommend?user_id=101&method=svd" | python3 -m json.tool

# Record a mastered rating
curl -X POST http://localhost:8000/api/interact \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "word_id": 5, "rating": 5}'
```

---

## Dashboard Features

| Feature | Description |
|---|---|
| **XAI Score Tooltip** | Hover the Engine Score bar to see the Hybrid model's 40/35/25% weight breakdown |
| **3D Flashcard Flip** | Click a word to flip and reveal its synonym for active recall practice |
| **Word Details Drawer** | Click ℹ to open a side panel with etymology, definition, example, derivative forms |
| **Audio Settings** | Choose 🇺🇸 US / 🇬🇧 UK accent and 1.0× / 0.75× playback speed per word |
| **Confetti + Counter** | Clicking ✓ Mastered fires a particle burst and increments the session counter |
| **Algorithm Comparison** | Charts panel shows RMSE, Precision@5, and Coverage across all four methods |
| **Interaction Log** | Real-time per-user log of all rated words in the current session |

---

## Evaluation Metrics

| Metric | Formula |
|---|---|
| **RMSE** | `√( Σ(predicted − actual)² / n )` — lower is better |
| **Precision@5** | Fraction of top-5 recommendations rated ≥ 4 by the user |
| **Coverage** | Fraction of the 300-word catalog the model can recommend |

---

## License

MIT — see [LICENSE](LICENSE).