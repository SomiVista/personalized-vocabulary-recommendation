"""
recommenders.py
===============
MRW2 Prototype – Four Recommendation Engines + Evaluation Module

Engines
-------
1. ContentBasedRecommender  – Cosine similarity on CEFR/POS feature vectors
2. SVDRecommender           – Truncated SVD via scikit-learn (k=20 factors)
3. AutoencoderRecommender   – PyTorch CPU autoencoder (300→64→32→64→300)
4. HybridRecommender        – CBF for cold-start; weighted ensemble for active users

All engines expose a common interface:
    recommend(user_idx, rating_matrix, top_n=5) → list[dict]

Each dict contains: word_id, word, cefr_difficulty, part_of_speech, score

Evaluation
----------
evaluate(rating_matrix, words) → dict with RMSE, MAE, Precision@5
"""

from __future__ import annotations
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import torch
import torch.nn as nn

# ─────────────────────────────────────────────
# Shared constants
# ─────────────────────────────────────────────
CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
CEFR_INDEX  = {lvl: i for i, lvl in enumerate(CEFR_LEVELS)}
POS_TAGS    = ["Noun", "Verb", "Adjective", "Adverb"]
POS_INDEX   = {pos: i for i, pos in enumerate(POS_TAGS)}

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)


# ══════════════════════════════════════════════════════════════
# Helper: build word feature matrix (300 × 10)
# Each row = [cefr_onehot(6) | pos_onehot(4)]
# ══════════════════════════════════════════════════════════════
def _build_word_features(words: list[dict]) -> np.ndarray:
    """
    Returns a (num_words × 10) float32 matrix.
    Columns 0-5: one-hot CEFR difficulty
    Columns 6-9: one-hot Part-of-Speech
    """
    n = len(words)
    feat = np.zeros((n, 10), dtype=np.float32)
    for i, w in enumerate(words):
        feat[i, CEFR_INDEX[w["cefr_difficulty"]]] = 1.0
        feat[i, 6 + POS_INDEX[w["part_of_speech"]]] = 1.0
    return feat


def _build_user_cefr_vector(cefr_level: str) -> np.ndarray:
    """
    Returns a (10,) float32 vector for the user's CEFR profile.
    The CEFR component uses the user's level PLUS one-above (Zone of Proximal Development boost).
    The POS component is uniform (user has no inherent POS preference from CEFR alone).
    """
    vec = np.zeros(10, dtype=np.float32)
    idx = CEFR_INDEX[cefr_level]
    vec[idx] = 1.0
    # ZPD boost: lightly activate the next CEFR level if it exists
    if idx + 1 < len(CEFR_LEVELS):
        vec[idx + 1] = 0.5
    # Uniform POS preference
    vec[6:] = 0.25
    return vec


def _get_unrated_mask(user_row: np.ndarray) -> np.ndarray:
    """Returns boolean mask where True = word NOT yet rated by the user."""
    return user_row == 0


def _top_n_items(scores: np.ndarray, unrated_mask: np.ndarray,
                 words: list[dict], top_n: int) -> list[dict]:
    """
    Filter to unrated items, sort by score descending, return top_n dicts.
    """
    candidate_scores = np.where(unrated_mask, scores, -np.inf)
    top_indices = np.argsort(candidate_scores)[::-1][:top_n]
    results = []
    for idx in top_indices:
        if candidate_scores[idx] == -np.inf:
            break
        results.append({
            "word_id":         words[idx]["word_id"],
            "word":            words[idx]["word"],
            "cefr_difficulty": words[idx]["cefr_difficulty"],
            "part_of_speech":  words[idx]["part_of_speech"],
            "score":           round(float(candidate_scores[idx]), 4),
        })
    return results


# ══════════════════════════════════════════════════════════════
# Method 1 – Content-Based Filtering
# ══════════════════════════════════════════════════════════════
class ContentBasedRecommender:
    """
    Recommends words by computing cosine similarity between a user's CEFR
    profile vector and each word's feature vector.
    ZPD boost ensures words one level above are preferred.
    Works perfectly for cold-start users (requires only their CEFR level).
    For cold-start with unknown CEFR, defaults to A1 profile.
    """

    _name = "content"

    def __init__(self, words: list[dict]):
        self.words = words
        # Pre-compute word feature matrix (300 × 10)
        self.word_features = _build_word_features(words)

    def recommend(
        self,
        user_idx: int,
        rating_matrix: np.ndarray,
        users: list[dict],
        top_n: int = 5,
    ) -> list[dict]:
        user = users[user_idx]
        cefr = user["cefr_level"] or "A1"          # cold-start default
        user_vec = _build_user_cefr_vector(cefr).reshape(1, -1)

        # Cosine similarity: (1 × 10) · (300 × 10)^T → (1 × 300)
        scores = cosine_similarity(user_vec, self.word_features).flatten()

        # For active users, mask already-rated words
        if user_idx < rating_matrix.shape[0]:
            unrated = _get_unrated_mask(rating_matrix[user_idx])
        else:
            unrated = np.ones(len(self.words), dtype=bool)

        return _top_n_items(scores, unrated, self.words, top_n)


# ══════════════════════════════════════════════════════════════
# Method 2 – Collaborative Filtering via Truncated SVD
# ══════════════════════════════════════════════════════════════
class SVDRecommender:
    """
    Uses scikit-learn TruncatedSVD (k=20) to decompose and reconstruct the
    100×300 interaction matrix, predicting preference scores for unrated items.

    Training reconstructs the full matrix once at init time.
    Cold-start users fall back to ContentBasedRecommender.
    """

    _name = "svd"

    def __init__(self, words: list[dict], rating_matrix: np.ndarray,
                 users: list[dict], n_components: int = 20):
        self.words = words
        self.users = users
        self.cbf   = ContentBasedRecommender(words)

        # Fit SVD on the training matrix
        self.svd = TruncatedSVD(n_components=n_components, random_state=RANDOM_SEED)
        self.svd.fit(rating_matrix)

        # Reconstruct the full matrix: R̂ = U · Σ · Vᵀ
        U_sigma = self.svd.transform(rating_matrix)           # (100 × k)
        self.reconstructed = U_sigma @ self.svd.components_   # (100 × 300)

        # Scale reconstructed scores to [1, 5] for interpretability
        rmin, rmax = self.reconstructed.min(), self.reconstructed.max()
        if rmax > rmin:
            self.reconstructed = 1 + 4 * (self.reconstructed - rmin) / (rmax - rmin)

    def recommend(
        self,
        user_idx: int,
        rating_matrix: np.ndarray,
        users: list[dict],
        top_n: int = 5,
    ) -> list[dict]:
        user = users[user_idx]
        # Cold-start fall-back
        if user["is_cold_start"]:
            return self.cbf.recommend(user_idx, rating_matrix, users, top_n)

        scores    = self.reconstructed[user_idx]               # (300,)
        unrated   = _get_unrated_mask(rating_matrix[user_idx])
        return _top_n_items(scores, unrated, self.words, top_n)

    def get_scores(self, user_idx: int) -> np.ndarray:
        """Raw reconstructed score vector for ensemble use."""
        return self.reconstructed[user_idx]


# ══════════════════════════════════════════════════════════════
# Method 3 – Deep Autoencoder (PyTorch CPU)
# ══════════════════════════════════════════════════════════════
class _Autoencoder(nn.Module):
    """
    Architecture: 300 → 64 → 32 → 64 → 300
    Activation:   ReLU on hidden layers, linear output.
    """
    def __init__(self, input_dim: int = 300):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, input_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encoder(x))


class AutoencoderRecommender:
    """
    Trains a PyTorch autoencoder on the rating matrix.
    Reconstruction of a user's rating vector fills in predicted scores for
    unrated words.  Trained on only the non-zero (observed) entries to avoid
    pushing the model to predict zeros for unseen items.

    Cold-start users fall back to ContentBasedRecommender.
    """

    _name = "autoencoder"

    def __init__(self, words: list[dict], rating_matrix: np.ndarray,
                 users: list[dict], epochs: int = 60, lr: float = 1e-3):
        self.words  = words
        self.users  = users
        self.cbf    = ContentBasedRecommender(words)
        self.device = torch.device("cpu")

        # ── Training ──────────────────────────────────────────
        self.model = _Autoencoder(input_dim=len(words)).to(self.device)
        optimizer  = torch.optim.Adam(self.model.parameters(), lr=lr, weight_decay=1e-5)
        loss_fn    = nn.MSELoss(reduction="none")

        # Normalise ratings to [0, 1] for training stability
        X = torch.tensor(rating_matrix / 5.0, dtype=torch.float32, device=self.device)
        mask = (X > 0).float()      # only penalise observed ratings

        self.model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            X_hat = self.model(X)
            # Masked MSE – only compute loss on non-zero entries
            loss = (loss_fn(X_hat, X) * mask).sum() / mask.sum()
            loss.backward()
            optimizer.step()

        # ── Pre-compute reconstructions ────────────────────────
        self.model.eval()
        with torch.no_grad():
            recon_norm = self.model(X).cpu().numpy()   # (100 × 300), [0–1] range

        # Scale back to [1, 5] rating range
        self.reconstructed = 1 + 4 * np.clip(recon_norm, 0, 1)

    def recommend(
        self,
        user_idx: int,
        rating_matrix: np.ndarray,
        users: list[dict],
        top_n: int = 5,
    ) -> list[dict]:
        user = users[user_idx]
        if user["is_cold_start"]:
            return self.cbf.recommend(user_idx, rating_matrix, users, top_n)

        scores  = self.reconstructed[user_idx]
        unrated = _get_unrated_mask(rating_matrix[user_idx])
        return _top_n_items(scores, unrated, self.words, top_n)

    def get_scores(self, user_idx: int) -> np.ndarray:
        """Raw reconstructed score vector for ensemble use."""
        return self.reconstructed[user_idx]


# ══════════════════════════════════════════════════════════════
# Method 4 – Hybrid Recommender
# ══════════════════════════════════════════════════════════════
class HybridRecommender:
    """
    Cold-Start path  → 100 % Content-Based Filtering
    Active user path → 0.40 × CBF + 0.35 × SVD + 0.25 × Autoencoder

    All three component scores are normalised to [0, 1] before blending
    so that different score ranges don't dominate the ensemble.
    """

    _name = "hybrid"

    def __init__(
        self,
        words: list[dict],
        rating_matrix: np.ndarray,
        users: list[dict],
        cbf: ContentBasedRecommender,
        svd: SVDRecommender,
        ae:  AutoencoderRecommender,
    ):
        self.words  = words
        self.users  = users
        self.cbf    = cbf
        self.svd    = svd
        self.ae     = ae

        # Pre-compute normalised CBF scores for each active user
        word_features = _build_word_features(words)
        self._cbf_matrix = np.zeros((len(users), len(words)), dtype=np.float32)
        for i, u in enumerate(users):
            if not u["is_cold_start"]:
                cefr = u["cefr_level"] or "A1"
                uv   = _build_user_cefr_vector(cefr).reshape(1, -1)
                self._cbf_matrix[i] = cosine_similarity(uv, word_features).flatten()

    @staticmethod
    def _normalise(arr: np.ndarray) -> np.ndarray:
        mn, mx = arr.min(), arr.max()
        if mx > mn:
            return (arr - mn) / (mx - mn)
        return np.zeros_like(arr)

    def recommend(
        self,
        user_idx: int,
        rating_matrix: np.ndarray,
        users: list[dict],
        top_n: int = 5,
    ) -> list[dict]:
        user = users[user_idx]

        if user["is_cold_start"]:
            # Pure CBF for cold-start
            return self.cbf.recommend(user_idx, rating_matrix, users, top_n)

        # Weighted ensemble
        cbf_scores = self._normalise(self._cbf_matrix[user_idx])
        svd_scores = self._normalise(self.svd.get_scores(user_idx))
        ae_scores  = self._normalise(self.ae.get_scores(user_idx))

        blended = 0.40 * cbf_scores + 0.35 * svd_scores + 0.25 * ae_scores

        unrated = _get_unrated_mask(rating_matrix[user_idx])
        return _top_n_items(blended, unrated, self.words, top_n)


# ══════════════════════════════════════════════════════════════
# Evaluation Module
# ══════════════════════════════════════════════════════════════
def evaluate_method(
    method_name: str,
    rating_matrix: np.ndarray,
    reconstructed: np.ndarray | None = None,
    cbf_features: np.ndarray | None = None,
    words: list[dict] | None = None,
    users: list[dict] | None = None,
    test_fraction: float = 0.20,
) -> dict:
    """
    Simulated evaluation on a held-out 20 % test split.

    For rating-based methods (svd, autoencoder, hybrid):
      - Holds out 20 % of the non-zero entries.
      - Computes RMSE and MAE on the held-out entries.
      - Precision@5: fraction of top-5 recommendations that were in the
        relevant (rating ≥ 4) held-out set.

    For content-based:
      - Uses the same held-out set but compares CBF scores to true ratings.

    Returns: {"rmse": float, "mae": float, "precision_at_5": float}
    """
    np.random.seed(RANDOM_SEED + 1)

    n_users, n_words = rating_matrix.shape
    rmse_vals, mae_vals, prec_vals = [], [], []

    for u in range(n_users):
        nonzero_idx = np.where(rating_matrix[u] > 0)[0]
        if len(nonzero_idx) < 5:
            continue

        # Hold out 20 %
        n_test  = max(1, int(len(nonzero_idx) * test_fraction))
        test_idx = np.random.choice(nonzero_idx, size=n_test, replace=False)
        true_ratings = rating_matrix[u, test_idx]

        if reconstructed is not None:
            pred_ratings = reconstructed[u, test_idx]
        elif cbf_features is not None and words is not None and users is not None:
            # CBF scores are cosine similarities in [0,1]; scale to [1,5]
            cefr = (users[u].get("cefr_level") or "A1")
            uvec = _build_user_cefr_vector(cefr).reshape(1, -1)
            sims = cosine_similarity(uvec, cbf_features).flatten()
            pred_ratings = 1 + 4 * sims[test_idx]
        else:
            continue

        rmse_vals.append(np.sqrt(np.mean((pred_ratings - true_ratings) ** 2)))
        mae_vals.append(np.mean(np.abs(pred_ratings - true_ratings)))

        # Precision@5: among top-5 predicted, how many are "relevant" (rating≥4)?
        all_unrated_mask = rating_matrix[u] == 0
        # temporarily also un-rate the test set for fair evaluation
        temp_mask = np.ones(n_words, dtype=bool)
        temp_mask[nonzero_idx] = False
        temp_mask[test_idx] = True  # test items are candidates

        relevant_test = set(test_idx[true_ratings >= 4])
        if reconstructed is not None:
            cand_scores = np.where(temp_mask, reconstructed[u], -np.inf)
        elif cbf_features is not None and words is not None and users is not None:
            cefr  = (users[u].get("cefr_level") or "A1")
            uvec  = _build_user_cefr_vector(cefr).reshape(1, -1)
            sims  = cosine_similarity(uvec, cbf_features).flatten()
            cand_scores = np.where(temp_mask, sims, -np.inf)
        else:
            continue

        top5 = set(np.argsort(cand_scores)[::-1][:5])
        hits = len(top5 & relevant_test)
        prec_vals.append(hits / 5.0)

    # Aggregate
    if not rmse_vals:
        return {"rmse": 0.0, "mae": 0.0, "precision_at_5": 0.0}

    return {
        "rmse":           round(float(np.mean(rmse_vals)), 4),
        "mae":            round(float(np.mean(mae_vals)),  4),
        "precision_at_5": round(float(np.mean(prec_vals)), 4),
    }


# ══════════════════════════════════════════════════════════════
# Factory – build all four engines once at server startup
# ══════════════════════════════════════════════════════════════
def build_all_recommenders(
    users: list[dict],
    words: list[dict],
    rating_matrix: np.ndarray,
) -> dict:
    """
    Trains / initialises all four recommenders and pre-computes evaluation
    metrics.  Returns a dict keyed by method name.
    """
    print("[recommenders] Building Content-Based engine …")
    cbf = ContentBasedRecommender(words)

    print("[recommenders] Building SVD engine …")
    svd = SVDRecommender(words, rating_matrix, users, n_components=20)

    print("[recommenders] Training Autoencoder (PyTorch CPU) …")
    ae  = AutoencoderRecommender(words, rating_matrix, users, epochs=60)

    print("[recommenders] Building Hybrid engine …")
    hyb = HybridRecommender(words, rating_matrix, users, cbf, svd, ae)

    word_features = _build_word_features(words)

    print("[recommenders] Computing evaluation metrics …")
    metrics = {
        "content": evaluate_method(
            "content",
            rating_matrix,
            cbf_features=word_features,
            words=words,
            users=users[:len(rating_matrix)],
        ),
        "svd": evaluate_method(
            "svd",
            rating_matrix,
            reconstructed=svd.reconstructed,
        ),
        "autoencoder": evaluate_method(
            "autoencoder",
            rating_matrix,
            reconstructed=ae.reconstructed,
        ),
        "hybrid": evaluate_method(
            "hybrid",
            rating_matrix,
            reconstructed=(0.35 * svd.reconstructed + 0.25 * ae.reconstructed),
        ),
    }

    print("[recommenders] All engines ready.")
    return {
        "engines": {
            "content":     cbf,
            "svd":         svd,
            "autoencoder": ae,
            "hybrid":      hyb,
        },
        "metrics": metrics,
    }
