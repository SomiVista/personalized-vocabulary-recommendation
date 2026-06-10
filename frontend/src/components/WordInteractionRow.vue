<template>
  <tr
    class="word-row"
    :class="{ 'word-row--interacted': interacted }"
    :id="`word-row-${word.word_id}`"
  >
    <!-- Rank -->
    <td class="td-rank">
      <span class="rank-badge">#{{ rank }}</span>
    </td>

    <!-- Word -->
    <td class="td-word">
      <div class="word-cell-content">
        <span class="word-clickable-text" @click="$emit('word-click', word)" title="Click to view details">
          {{ word.word }}
        </span>
        <button class="speak-btn" @click.stop="pronounceWord(word.word)" title="Listen pronunciation">
          🔊
        </button>
      </div>
    </td>

    <!-- CEFR Difficulty -->
    <td class="td-cefr">
      <span class="cefr-badge" :class="`cefr--${word.cefr_difficulty.toLowerCase()}`">
        {{ word.cefr_difficulty }}
      </span>
    </td>

    <!-- Part of Speech -->
    <td class="td-pos">
      <span class="pos-chip">{{ word.part_of_speech }}</span>
    </td>

    <!-- Score bar -->
    <td class="td-score">
      <div class="score-wrapper">
        <div class="score-bar-track">
          <div class="score-bar-fill" :style="{ width: scoreBarWidth }"></div>
        </div>
        <span class="score-value mono">{{ word.score?.toFixed(3) }}</span>
      </div>
    </td>

    <!-- Actions -->
    <td class="td-actions">
      <div class="action-group">
        <button
          class="btn btn-success action-btn"
          :disabled="isSubmitting || interacted"
          :id="`btn-mastered-${word.word_id}`"
          @click="interact(5)"
          title="Mark as fully mastered (rating = 5)"
        >
          <span v-if="isSubmitting && lastAction === 'mastered'" class="spinner"></span>
          <span v-else>✓</span>
          Mastered
        </button>
        <button
          class="btn btn-study action-btn"
          :disabled="isSubmitting || interacted"
          :id="`btn-study-${word.word_id}`"
          @click="interact(2)"
          title="Mark as currently studying (rating = 2)"
        >
          <span v-if="isSubmitting && lastAction === 'study'" class="spinner"></span>
          <span v-else>📖</span>
          Study
        </button>
      </div>
    </td>
  </tr>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  word:   { type: Object,  required: true },
  rank:   { type: Number,  default: 1 },
  userId: { type: Number,  required: true },
})
const emit = defineEmits(['interacted', 'word-click'])

function pronounceWord(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-US'
    window.speechSynthesis.speak(utterance)
  }
}

const isSubmitting = ref(false)
const interacted   = ref(false)
const lastAction   = ref('')

// Normalise score to a 0-100% bar width (scores are cosine sims ≈ 0-1 or reconstructed 1-5)
const scoreBarWidth = computed(() => {
  const s = props.word.score ?? 0
  // Try to normalise: if score ≤ 1 treat as cosine sim; else as 1-5 rating
  const normalised = s <= 1 ? s : (s - 1) / 4
  return Math.max(4, Math.min(100, normalised * 100)) + '%'
})

async function interact(rating) {
  if (isSubmitting.value || interacted.value) return
  lastAction.value = rating === 5 ? 'mastered' : 'study'
  isSubmitting.value = true

  try {
    const res = await fetch('/api/interact', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: props.userId,
        word_id: props.word.word_id,
        rating,
      }),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    interacted.value = true
    emit('interacted', { word: props.word, rating })
  } catch (err) {
    console.error('[interact] Failed:', err)
    alert(`Failed to record interaction: ${err.message}`)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.word-row {
  transition: background 0.2s;
  animation: fadeSlideIn 0.25s ease forwards;
}
.word-row:hover td { background: rgba(255,255,255,0.025); }
.word-row--interacted { opacity: 0.4; }

td {
  padding:        12px 10px;
  border-bottom:  1px solid var(--clr-border);
  vertical-align: middle;
}

/* Rank */
.td-rank   { width: 48px; text-align: center; }
.rank-badge {
  display:       inline-flex;
  align-items:   center;
  justify-content: center;
  width:         28px; height: 28px;
  border-radius: 50%;
  background:    var(--clr-surface-hov);
  border:        1px solid var(--clr-border);
  font-size:     11px;
  font-weight:   700;
  color:         var(--clr-text-muted);
}

/* Word */
.td-word  { min-width: 130px; }
.word-cell-content {
  display:     flex;
  align-items: center;
  gap:         8px;
}
.word-clickable-text {
  font-size:   14px;
  font-weight: 600;
  color:       var(--clr-text);
  cursor:      pointer;
  transition:  color 0.2s;
  border-bottom: 1px dashed transparent;
}
.word-clickable-text:hover {
  color:         var(--clr-accent-from);
  border-bottom-color: var(--clr-accent-from);
}

.speak-btn {
  background:  none;
  border:      none;
  cursor:      pointer;
  font-size:   13px;
  opacity:     0.5;
  transition:  opacity 0.2s, transform 0.2s;
  padding:     2px;
}
.speak-btn:hover {
  opacity:   1;
  transform: scale(1.15);
}

/* CEFR badge */
.td-cefr   { width: 70px; text-align: center; }
.cefr-badge {
  display:       inline-block;
  font-size:     10px;
  font-weight:   800;
  letter-spacing: 0.07em;
  padding:       3px 8px;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
}
.cefr--a1 { background: rgba(34,197,94,0.15);   color: var(--cefr-a1); border: 1px solid rgba(34,197,94,0.3); }
.cefr--a2 { background: rgba(134,239,172,0.12); color: var(--cefr-a2); border: 1px solid rgba(134,239,172,0.3); }
.cefr--b1 { background: rgba(250,204,21,0.12);  color: var(--cefr-b1); border: 1px solid rgba(250,204,21,0.3); }
.cefr--b2 { background: rgba(249,115,22,0.12);  color: var(--cefr-b2); border: 1px solid rgba(249,115,22,0.3); }
.cefr--c1 { background: rgba(248,113,113,0.12); color: var(--cefr-c1); border: 1px solid rgba(248,113,113,0.3); }
.cefr--c2 { background: rgba(239,68,68,0.12);   color: var(--cefr-c2); border: 1px solid rgba(239,68,68,0.3); }

/* POS chip */
.td-pos   { width: 100px; }
.pos-chip {
  display:       inline-block;
  font-size:     11px;
  font-weight:   500;
  padding:       3px 8px;
  border-radius: var(--radius-sm);
  background:    rgba(99,102,241,0.1);
  color:         var(--clr-accent-from);
  border:        1px solid rgba(99,102,241,0.2);
}

/* Score bar */
.td-score    { min-width: 140px; }
.score-wrapper {
  display:     flex;
  align-items: center;
  gap:         10px;
}
.score-bar-track {
  flex:          1;
  height:        5px;
  background:    var(--clr-surface-hov);
  border-radius: 999px;
  overflow:      hidden;
}
.score-bar-fill {
  height:        100%;
  border-radius: 999px;
  background:    linear-gradient(90deg, var(--clr-accent-from), var(--clr-accent-to));
  transition:    width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.score-value {
  font-size:  11px;
  color:      var(--clr-text-muted);
  flex-shrink: 0;
  min-width:  44px;
  text-align: right;
}

/* Actions */
.td-actions  { width: 200px; }
.action-group {
  display: flex;
  gap:     6px;
}
.action-btn {
  padding:   6px 11px;
  font-size: 12px;
}
</style>
