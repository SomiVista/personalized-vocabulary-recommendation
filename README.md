# VocabAI Recommender — MRW2 Research Prototype

**AN EXPERIMENTAL EVALUATION OF PERSONALIZED RECOMMENDER SYSTEMS FOR VOCABULARY LEARNING IN AI-DRIVEN LANGUAGE EDUCATION PLATFORMS**

> Vilnius Gediminas Technical University · Somayeh Roohani · Supervisor: Prof. Dr. Irina Vinogradova-Zinkevič

---

## Architecture

```
personalized-vocabulary-recommendation/
├── backend/
│   ├── data_simulator.py   # Generates 105 users, 300 words, sparse rating matrix
│   ├── recommenders.py     # 4 engines: CBF · SVD · Autoencoder · Hybrid
│   ├── main.py             # FastAPI REST server (port 8000)
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── main.js
        ├── style.css
        ├── App.vue
        └── components/
            ├── UserSelector.vue
            ├── AlgorithmSelector.vue
            ├── MetricsCard.vue
            ├── RecommendationTable.vue
            └── WordInteractionRow.vue
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Terminal 1 – Backend

```bash
# From the project root
cd personalized-vocabulary-recommendation

# Create and activate virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows

# Install Python dependencies
pip install -r backend/requirements.txt

# Start FastAPI server (startup trains all models – takes ~15–30 seconds)
uvicorn backend.main:app --reload --port 8000
```

> ✅ Backend ready when you see: `[startup] Ready – 105 users, 300 words`

### Terminal 2 – Frontend

```bash
cd personalized-vocabulary-recommendation/frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```

> ✅ Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Dataset

| Component | Details |
|-----------|---------|
| Active Users | 100, CEFR A1–C2 (weighted toward B1/B2) |
| Cold-Start Users | 5 (IDs 101–105, zero interaction history) |
| Vocabulary | 300 English words, 50 per CEFR level |
| Interaction Matrix | 100 × 300 sparse, ~8% density, ratings 1–5 |

---

## Recommendation Engines

| # | Method | Library | Cold-Start | Key Metric |
|---|--------|---------|-----------|-----------|
| 1 | Content-Based Filtering | scikit-learn | ✅ Native | CEFR cosine sim |
| 2 | SVD Collaborative Filtering | scikit-learn TruncatedSVD | ⚠ CBF fallback | k=20 latent factors |
| 3 | Deep Autoencoder | PyTorch CPU | ⚠ CBF fallback | 300→64→32→64→300 |
| 4 | Hybrid (Proposed) | All above | ✅ Via CBF | 0.4 CBF + 0.35 SVD + 0.25 AE |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/users` | GET | All 105 users |
| `GET /api/words` | GET | Full 300-word dictionary |
| `GET /api/recommend?user_id=1&method=hybrid` | GET | Top-5 recommendations + metrics |
| `POST /api/interact` | POST | `{user_id, word_id, rating}` |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Verification Commands

```bash
# Check users list
curl http://localhost:8000/api/users | python3 -m json.tool | head -30

# Active user recommendations (hybrid)
curl "http://localhost:8000/api/recommend?user_id=1&method=hybrid" | python3 -m json.tool

# Cold-start user (auto-falls back to CBF)
curl "http://localhost:8000/api/recommend?user_id=101&method=svd" | python3 -m json.tool

# Record an interaction
curl -X POST http://localhost:8000/api/interact \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "word_id": 5, "rating": 5}'
```