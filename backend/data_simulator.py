"""
data_simulator.py
=================
MRW2 Prototype – Simulated Language Learning Dataset Generator

Produces three core data structures used by all recommender engines:
  • users_df     : 105 users (100 active + 5 cold-start)
  • words_df     : 300 English vocabulary items
  • rating_matrix: (100 × 300) sparse numpy array – cold-start rows are all zeros

Run standalone for a quick sanity-check:
    python backend/data_simulator.py
"""

import numpy as np
import random

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
CEFR_LEVELS  = ["A1", "A2", "B1", "B2", "C1", "C2"]
CEFR_INDEX   = {lvl: i for i, lvl in enumerate(CEFR_LEVELS)}   # A1→0 … C2→5
POS_TAGS     = ["Noun", "Verb", "Adjective", "Adverb"]
POS_WEIGHTS  = [0.35,   0.30,   0.20,        0.15]              # realistic mix

NUM_ACTIVE_USERS     = 100
NUM_COLD_START_USERS = 5
NUM_WORDS            = 300
WORDS_PER_LEVEL      = NUM_WORDS // len(CEFR_LEVELS)            # 50 words/level
INTERACTION_DENSITY  = 0.08
RANDOM_SEED          = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ─────────────────────────────────────────────
# 300 English words distributed evenly across CEFR levels (50 per level)
# ─────────────────────────────────────────────
_WORD_BANK: dict[str, list[tuple[str, str]]] = {
    # (word_or_phrase, part_of_speech)
    "A1": [
        ("apple", "Noun"), ("run", "Verb"), ("big", "Adjective"), ("fast", "Adverb"),
        ("book", "Noun"), ("eat", "Verb"), ("small", "Adjective"), ("slowly", "Adverb"),
        ("cat", "Noun"), ("drink", "Verb"), ("red", "Adjective"), ("well", "Adverb"),
        ("dog", "Noun"), ("go", "Verb"), ("blue", "Adjective"), ("here", "Adverb"),
        ("house", "Noun"), ("see", "Verb"), ("green", "Adjective"), ("now", "Adverb"),
        ("car", "Noun"), ("play", "Verb"), ("old", "Adjective"), ("very", "Adverb"),
        ("table", "Noun"), ("sit", "Verb"), ("new", "Adjective"), ("also", "Adverb"),
        ("water", "Noun"), ("come", "Verb"), ("good", "Adjective"), ("too", "Adverb"),
        ("food", "Noun"), ("talk", "Verb"), ("bad", "Adjective"), ("just", "Adverb"),
        ("school", "Noun"), ("walk", "Verb"), ("happy", "Adjective"), ("again", "Adverb"),
        ("friend", "Noun"), ("sleep", "Verb"), ("cold", "Adjective"), ("only", "Adverb"),
        ("number", "Noun"), ("want", "Verb"), ("hot", "Adjective"), ("never", "Adverb"),
        ("name", "Noun"), ("need", "Verb"),
    ],
    "A2": [
        ("journey", "Noun"), ("describe", "Verb"), ("nervous", "Adjective"), ("nearly", "Adverb"),
        ("holiday", "Noun"), ("explain", "Verb"), ("friendly", "Adjective"), ("quite", "Adverb"),
        ("weather", "Noun"), ("decide", "Verb"), ("popular", "Adjective"), ("usually", "Adverb"),
        ("market", "Noun"), ("invite", "Verb"), ("different", "Adjective"), ("always", "Adverb"),
        ("lesson", "Noun"), ("prepare", "Verb"), ("important", "Adjective"), ("sometimes", "Adverb"),
        ("culture", "Noun"), ("choose", "Verb"), ("careful", "Adjective"), ("often", "Adverb"),
        ("hobby", "Noun"), ("collect", "Verb"), ("similar", "Adjective"), ("already", "Adverb"),
        ("street", "Noun"), ("remember", "Verb"), ("difficult", "Adjective"), ("soon", "Adverb"),
        ("family", "Noun"), ("forget", "Verb"), ("interesting", "Adjective"), ("still", "Adverb"),
        ("problem", "Noun"), ("enjoy", "Verb"), ("funny", "Adjective"), ("maybe", "Adverb"),
        ("answer", "Noun"), ("travel", "Verb"), ("lovely", "Adjective"), ("probably", "Adverb"),
        ("evening", "Noun"), ("finish", "Verb"), ("correct", "Adjective"), ("together", "Adverb"),
        ("airport", "Noun"), ("suggest", "Verb"),
    ],
    "B1": [
        ("circumstance", "Noun"), ("negotiate", "Verb"), ("significant", "Adjective"), ("approximately", "Adverb"),
        ("achievement", "Noun"), ("persuade", "Verb"), ("ambitious", "Adjective"), ("gradually", "Adverb"),
        ("environment", "Noun"), ("contribute", "Verb"), ("efficient", "Adjective"), ("eventually", "Adverb"),
        ("opportunity", "Noun"), ("recognize", "Verb"), ("relevant", "Adjective"), ("particularly", "Adverb"),
        ("consequence", "Noun"), ("investigate", "Verb"), ("consistent", "Adjective"), ("relatively", "Adverb"),
        ("advantage", "Noun"), ("identify", "Verb"), ("sustainable", "Adjective"), ("frequently", "Adverb"),
        ("requirement", "Noun"), ("evaluate", "Verb"), ("flexible", "Adjective"), ("independently", "Adverb"),
        ("experience", "Noun"), ("analyze", "Verb"), ("complex", "Adjective"), ("accordingly", "Adverb"),
        ("knowledge", "Noun"), ("communicate", "Verb"), ("diverse", "Adjective"), ("similarly", "Adverb"),
        ("development", "Noun"), ("implement", "Verb"), ("practical", "Adjective"), ("additionally", "Adverb"),
        ("relationship", "Noun"), ("demonstrate", "Verb"), ("logical", "Adjective"), ("therefore", "Adverb"),
        ("perspective", "Noun"), ("indicate", "Verb"), ("cultural", "Adjective"), ("meanwhile", "Adverb"),
        ("approach", "Noun"), ("maintain", "Verb"),
    ],
    "B2": [
        ("paradox", "Noun"), ("alleviate", "Verb"), ("intricate", "Adjective"), ("inadvertently", "Adverb"),
        ("rhetoric", "Noun"), ("substantiate", "Verb"), ("compelling", "Adjective"), ("predominantly", "Adverb"),
        ("discourse", "Noun"), ("articulate", "Verb"), ("controversial", "Adjective"), ("subsequently", "Adverb"),
        ("hypothesis", "Noun"), ("validate", "Verb"), ("ambiguous", "Adjective"), ("nonetheless", "Adverb"),
        ("phenomenon", "Noun"), ("mitigate", "Verb"), ("coherent", "Adjective"), ("consequently", "Adverb"),
        ("framework", "Noun"), ("facilitate", "Verb"), ("substantial", "Adjective"), ("moreover", "Adverb"),
        ("initiative", "Noun"), ("synthesize", "Verb"), ("comprehensive", "Adjective"), ("furthermore", "Adverb"),
        ("implication", "Noun"), ("anticipate", "Verb"), ("predominant", "Adjective"), ("alternatively", "Adverb"),
        ("correlation", "Noun"), ("perceive", "Verb"), ("systematic", "Adjective"), ("presumably", "Adverb"),
        ("mechanism", "Noun"), ("exacerbate", "Verb"), ("empirical", "Adjective"), ("theoretically", "Adverb"),
        ("dimension", "Noun"), ("incorporate", "Verb"), ("explicit", "Adjective"), ("statistically", "Adverb"),
        ("parameter", "Noun"), ("manipulate", "Verb"), ("inherent", "Adjective"), ("notably", "Adverb"),
        ("constraint", "Noun"), ("derive", "Verb"),
    ],
    "C1": [
        ("epistemology", "Noun"), ("obfuscate", "Verb"), ("idiosyncratic", "Adjective"), ("surreptitiously", "Adverb"),
        ("hegemony", "Noun"), ("circumvent", "Verb"), ("esoteric", "Adjective"), ("ostensibly", "Adverb"),
        ("paradigm", "Noun"), ("extrapolate", "Verb"), ("nuanced", "Adjective"), ("intrinsically", "Adverb"),
        ("dichotomy", "Noun"), ("corroborate", "Verb"), ("tangential", "Adjective"), ("axiomatically", "Adverb"),
        ("conjecture", "Noun"), ("exacerbate", "Verb"), ("elusive", "Adjective"), ("paradoxically", "Adverb"),
        ("dialectic", "Noun"), ("extrapolate", "Verb"), ("seminal", "Adjective"), ("empirically", "Adverb"),
        ("inference", "Noun"), ("perpetuate", "Verb"), ("rudimentary", "Adjective"), ("retrospectively", "Adverb"),
        ("abstraction", "Noun"), ("mitigate", "Verb"), ("omniscient", "Adjective"), ("inexorably", "Adverb"),
        ("rationale", "Noun"), ("ameliorate", "Verb"), ("superfluous", "Adjective"), ("irrevocably", "Adverb"),
        ("contention", "Noun"), ("juxtapose", "Verb"), ("categorical", "Adjective"), ("fundamentally", "Adverb"),
        ("ambivalence", "Noun"), ("formulate", "Verb"), ("precarious", "Adjective"), ("cogently", "Adverb"),
        ("determinism", "Noun"), ("delineate", "Verb"), ("tenuous", "Adjective"), ("rigorously", "Adverb"),
        ("pragmatism", "Noun"), ("substantiate", "Verb"),
    ],
    "C2": [
        ("solipsism", "Noun"), ("obsequiate", "Verb"), ("perspicacious", "Adjective"), ("ineffably", "Adverb"),
        ("apocryphal", "Adjective"), ("vitiate", "Verb"), ("recondite", "Adjective"), ("peremptorily", "Adverb"),
        ("sycophancy", "Noun"), ("dissimulate", "Verb"), ("pellucid", "Adjective"), ("tendentiously", "Adverb"),
        ("hubris", "Noun"), ("prevaricate", "Verb"), ("inimical", "Adjective"), ("insouciantly", "Adverb"),
        ("imprimatur", "Noun"), ("obfuscate", "Verb"), ("laconic", "Adjective"), ("ignominiously", "Adverb"),
        ("meretricious", "Adjective"), ("dissemble", "Verb"), ("garrulous", "Adjective"), ("precipitously", "Adverb"),
        ("anathema", "Noun"), ("inveigh", "Verb"), ("truculent", "Adjective"), ("sycophantically", "Adverb"),
        ("internecine", "Adjective"), ("expatiate", "Verb"), ("pusillanimous", "Adjective"), ("lugubriously", "Adverb"),
        ("exegesis", "Noun"), ("dissemble", "Verb"), ("recalcitrant", "Adjective"), ("perfidiously", "Adverb"),
        ("sophistry", "Noun"), ("equivocate", "Verb"), ("ineffable", "Adjective"), ("mellifluously", "Adverb"),
        ("autodidact", "Noun"), ("impugn", "Verb"), ("perspicuous", "Adjective"), ("unequivocally", "Adverb"),
        ("weltanschauung", "Noun"), ("excoriate", "Verb"), ("sesquipedalian", "Adjective"), ("magisterially", "Adverb"),
        ("loquacity", "Noun"), ("obtrude", "Verb"),
    ],
}


def build_users() -> list[dict]:
    """
    Create 105 user records.
    Active users (1-100) are assigned CEFR levels weighted toward B1/B2.
    Cold-start users (101-105) have no CEFR history and is_cold_start=True.
    """
    # Realistic distribution: B1/B2 most common
    cefr_weights = [0.10, 0.15, 0.25, 0.25, 0.15, 0.10]
    first_names = [
        "Alice", "Bob", "Carlos", "Diana", "Elena", "Faisal", "Grace", "Hana",
        "Ivan", "Julia", "Kevin", "Lena", "Marco", "Nina", "Omar", "Petra",
        "Quinn", "Rosa", "Sam", "Tara", "Uma", "Victor", "Wendy", "Xia",
        "Yusuf", "Zara", "Adam", "Bella", "Chad", "Dara", "Evan", "Fiona",
        "George", "Helen", "Ian", "Jana", "Kyle", "Lisa", "Mike", "Nora",
        "Oscar", "Paula", "Raj", "Sara", "Tom", "Ursula", "Vera", "Will",
        "Xena", "Yuki", "Zoe", "Aaron", "Beth", "Cole", "Dana", "Eric",
        "Faye", "Gael", "Holly", "Igor", "Jade", "Kurt", "Luna", "Max",
        "Nova", "Otto", "Pia", "Rex", "Suki", "Theo", "Una", "Vince",
        "Wren", "Xero", "Yara", "Zeus", "Amara", "Bruno", "Cleo", "Diego",
        "Esme", "Felix", "Gina", "Hugo", "Iris", "Joel", "Kira", "Leo",
        "Mia", "Nico", "Opal", "Pax", "Remy", "Sage", "Tino", "Uriel",
        "Val", "Willa", "Xavi", "Yael",
    ]

    users = []
    for uid in range(1, NUM_ACTIVE_USERS + 1):
        cefr = random.choices(CEFR_LEVELS, weights=cefr_weights, k=1)[0]
        users.append({
            "user_id":       uid,
            "name":          first_names[uid - 1],
            "cefr_level":    cefr,
            "is_cold_start": False,
        })

    # Cold-start users – no CEFR level assigned yet
    cold_names = ["NewUser_A", "NewUser_B", "NewUser_C", "NewUser_D", "NewUser_E"]
    for idx, cname in enumerate(cold_names):
        users.append({
            "user_id":       101 + idx,
            "name":          cname,
            "cefr_level":    None,          # unknown for cold-start
            "is_cold_start": True,
        })

    return users


def build_words() -> list[dict]:
    """
    Create 300 vocabulary items from the word bank (50 per CEFR level).
    Returns a list of dicts with word_id, word, cefr_difficulty, part_of_speech.
    """
    words = []
    word_id = 1
    for level in CEFR_LEVELS:
        for (word, pos) in _WORD_BANK[level]:
            words.append({
                "word_id":        word_id,
                "word":           word,
                "cefr_difficulty": level,
                "part_of_speech":  pos,
            })
            word_id += 1
    return words


def build_rating_matrix(users: list[dict], words: list[dict]) -> np.ndarray:
    """
    Build a sparse 100 × 300 rating matrix.

    Ratings (1–5) are biased by the alignment between the active user's CEFR
    level and the word's difficulty:
      - Words at/below user level  → skewed toward 3–5 (partial-to-full mastery)
      - Words 1 level above        → skewed toward 2–4 (learning zone)
      - Words 2+ levels above      → skewed toward 1–2 (mostly unknown)

    Cold-start users (IDs 101–105) are NOT included – they have no history.
    """
    matrix = np.zeros((NUM_ACTIVE_USERS, NUM_WORDS), dtype=np.float32)

    word_cefr_indices = [CEFR_INDEX[w["cefr_difficulty"]] for w in words]

    for u_idx, user in enumerate(users[:NUM_ACTIVE_USERS]):
        u_cefr_idx = CEFR_INDEX[user["cefr_level"]]
        # Decide which words this user has interacted with (≈8% density)
        interacted = np.random.rand(NUM_WORDS) < INTERACTION_DENSITY

        for w_idx in np.where(interacted)[0]:
            diff = word_cefr_indices[w_idx] - u_cefr_idx
            if diff <= 0:
                # At or below user level: likely mastered or near-mastered
                rating = np.random.choice([3, 4, 5], p=[0.2, 0.4, 0.4])
            elif diff == 1:
                # One level above: actively learning
                rating = np.random.choice([2, 3, 4], p=[0.3, 0.4, 0.3])
            elif diff == 2:
                # Two levels above: challenging
                rating = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
            else:
                # Far above level: mostly unknown
                rating = np.random.choice([1, 2], p=[0.7, 0.3])
            matrix[u_idx, w_idx] = rating

    return matrix


# ─────────────────────────────────────────────
# Public dataset singleton
# ─────────────────────────────────────────────
def generate_dataset() -> tuple[list[dict], list[dict], np.ndarray]:
    """
    Returns (users, words, rating_matrix).
    Call once at server startup; all recommenders share these objects.
    """
    users  = build_users()
    words  = build_words()
    matrix = build_rating_matrix(users, words)
    return users, words, matrix


# ─────────────────────────────────────────────
# Quick sanity-check when run directly
# ─────────────────────────────────────────────
if __name__ == "__main__":
    users, words, matrix = generate_dataset()
    print(f"Users     : {len(users)} (active={sum(not u['is_cold_start'] for u in users)}, cold={sum(u['is_cold_start'] for u in users)})")
    print(f"Words     : {len(words)}")
    print(f"Matrix    : {matrix.shape}  non-zero={int((matrix > 0).sum())}  density={((matrix > 0).sum() / matrix.size):.3f}")
    print(f"CEFR dist : { {lvl: sum(1 for u in users if u['cefr_level'] == lvl) for lvl in CEFR_LEVELS} }")
    print(f"Sample user : {users[0]}")
    print(f"Sample word : {words[0]}")
