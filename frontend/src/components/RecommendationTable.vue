<template>
  <div class="rec-table-wrapper glass">
    <div class="table-header">
      <div class="table-title">
        <span class="table-icon">🎯</span>
        Top-5 Recommendations
        <span v-if="methodLabel" class="method-pill">{{ methodLabel }}</span>
      </div>

      <!-- Session mastery counter (Feature 5) -->
      <Transition name="mastery-count">
        <div v-if="sessionMasteryCount > 0" class="mastery-chip" aria-live="polite">
          <span class="mastery-trophy">🏆</span>
          <span class="mastery-num">{{ sessionMasteryCount }}</span>
          <span class="mastery-label">mastered this session</span>
        </div>
      </Transition>

      <button
        class="btn btn-primary refresh-btn"
        id="btn-refresh-recommendations"
        :disabled="isLoading"
        @click="$emit('refresh')"
      >
        <span v-if="isLoading" class="spinner"></span>
        <span v-else>↻</span>
        Refresh
      </button>
    </div>

    <!-- Empty / error state -->
    <div v-if="!isLoading && (!recommendations || recommendations.length === 0)" class="empty-state">
      <div class="empty-icon">🔍</div>
      <div class="empty-text">No recommendations available</div>
      <div class="empty-hint">Select a user and algorithm to get started</div>
    </div>

    <!-- Loading skeleton rows -->
    <div v-else-if="isLoading" class="skeleton-table">
      <div v-for="i in 5" :key="i" class="skeleton-row-outer" :style="{ animationDelay: (i * 0.05) + 's' }">
        <div class="skel skel-rank"></div>
        <div class="skel skel-word"></div>
        <div class="skel skel-cefr"></div>
        <div class="skel skel-pos"></div>
        <div class="skel skel-bar"></div>
        <div class="skel skel-btns"></div>
      </div>
    </div>

    <!-- Data table -->
    <div v-else class="table-scroll">
      <table class="rec-table" aria-label="Vocabulary recommendations">
        <thead>
          <tr>
            <th>#</th>
            <th>Word / Phrase</th>
            <th>CEFR</th>
            <th>Part of Speech</th>
            <th title="Hover score for AI weight breakdown">Score ✦</th>
            <th>Action</th>
          </tr>
        </thead>
        <TransitionGroup tag="tbody" name="list">
          <WordInteractionRow
            v-for="(word, idx) in recommendations"
            :key="word.word_id"
            :word="word"
            :rank="idx + 1"
            :user-id="userId"
            @interacted="onInteracted"
            @mastered="onMastered"
            @word-click="$emit('word-click', $event)"
          />
        </TransitionGroup>
      </table>
    </div>

    <!-- Cold-start notice -->
    <div v-if="isColdStart && !isLoading" class="cold-notice">
      <span>❄</span>
      <div>
        <strong>Cold-Start Mode</strong> — This user has no interaction history.
        SVD and Autoencoder automatically fall back to Content-Based Filtering.
        Rate some words to activate personalised collaborative learning!
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import WordInteractionRow from './WordInteractionRow.vue'

const props = defineProps({
  recommendations:     { type: Array,   default: () => [] },
  userId:              { type: Number,  default: null },
  method:              { type: String,  default: 'hybrid' },
  isColdStart:         { type: Boolean, default: false },
  isLoading:           { type: Boolean, default: false },
  sessionMasteryCount: { type: Number,  default: 0 },
})
const emit = defineEmits(['refresh', 'interacted', 'word-click', 'mastered'])

const refreshKey = ref(0)

const methodLabels = {
  content:     '📖 Content-Based',
  svd:         '🔢 SVD',
  autoencoder: '🧠 Autoencoder',
  hybrid:      '⚡ Hybrid',
}

const methodLabel = computed(() => methodLabels[props.method] || props.method)

// Re-mount rows whenever algorithm changes to clear stale interaction states
watch(() => props.method, () => { refreshKey.value++ })

function onInteracted(payload) {
  emit('interacted', payload)
  // After brief delay trigger refresh so new recommendations replace rated word
  setTimeout(() => {
    refreshKey.value++
    emit('refresh')
  }, 800)
}

function onMastered(payload) {
  emit('mastered', payload)
}
</script>

<style scoped>
.rec-table-wrapper { overflow: visible; }   /* allow XAI tooltip to escape */

/* Header */
.table-header {
  display:         flex;
  align-items:     center;
  justify-content: space-between;
  padding:         18px 20px 14px;
  border-bottom:   1px solid var(--clr-border);
  flex-wrap:       wrap;
  gap:             10px;
}
.table-title {
  display:     flex;
  align-items: center;
  gap:         8px;
  font-size:   14px;
  font-weight: 600;
}
.table-icon  { font-size: 16px; }
.method-pill {
  font-size:     11px;
  font-weight:   600;
  padding:       2px 9px;
  border-radius: 999px;
  background:    rgba(99,102,241,0.12);
  color:         var(--clr-accent-from);
  border:        1px solid rgba(99,102,241,0.25);
}
.refresh-btn { font-size: 12px; padding: 7px 14px; }

/* ── Mastery counter chip (Feature 5) ── */
.mastery-chip {
  display:       flex;
  align-items:   center;
  gap:           6px;
  padding:       5px 12px;
  border-radius: 999px;
  background:    linear-gradient(135deg, rgba(16,185,129,0.15), rgba(6,182,212,0.12));
  border:        1px solid rgba(16,185,129,0.35);
  box-shadow:    0 0 14px rgba(16,185,129,0.12);
  animation:     masteryPop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.mastery-trophy { font-size: 14px; }
.mastery-num {
  font-size:   14px;
  font-weight: 800;
  color:       #34d399;
}
.mastery-label {
  font-size:   11px;
  font-weight: 600;
  color:       #6ee7b7;
  white-space: nowrap;
}

@keyframes masteryPop {
  0%   { transform: scale(0.7); opacity: 0; }
  100% { transform: scale(1);   opacity: 1; }
}

/* Mastery counter Transition */
.mastery-count-enter-active { transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
.mastery-count-leave-active { transition: all 0.25s ease; }
.mastery-count-enter-from   { opacity: 0; transform: scale(0.7) translateY(-4px); }
.mastery-count-leave-to     { opacity: 0; transform: scale(0.85); }

/* Empty state */
.empty-state {
  display:         flex;
  flex-direction:  column;
  align-items:     center;
  justify-content: center;
  padding:         60px 20px;
  gap:             8px;
  text-align:      center;
}
.empty-icon { font-size: 40px; opacity: 0.4; }
.empty-text { font-size: 15px; font-weight: 600; color: var(--clr-text-muted); }
.empty-hint { font-size: 12px; color: var(--clr-text-faint); }

/* Table */
.table-scroll { overflow-x: auto; overflow-y: visible; }
.rec-table {
  width:           100%;
  border-collapse: collapse;
}
.rec-table thead tr { background: rgba(255,255,255,0.02); }
.rec-table th {
  padding:        10px 10px;
  font-size:      10px;
  font-weight:    700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color:          var(--clr-text-muted);
  border-bottom:  1px solid var(--clr-border);
  text-align:     left;
  white-space:    nowrap;
}

/* Cold-start notice */
.cold-notice {
  display:       flex;
  align-items:   flex-start;
  gap:           12px;
  padding:       14px 18px;
  margin:        0 16px 16px;
  border-radius: var(--radius-md);
  background:    rgba(6,182,212,0.06);
  border:        1px solid rgba(6,182,212,0.2);
  font-size:     12px;
  color:         var(--clr-accent2);
  line-height:   1.6;
}
.cold-notice > span { font-size: 18px; flex-shrink: 0; margin-top: 1px; }

/* Skeleton */
.skeleton-table { padding: 8px 0; }
.skeleton-row-outer {
  display:       flex;
  align-items:   center;
  gap:           12px;
  padding:       12px 20px;
  border-bottom: 1px solid var(--clr-border);
  animation:     shimmer 1.2s infinite;
}
.skel {
  background:    var(--clr-surface-hov);
  border-radius: 4px;
  height:        16px;
}
.skel-rank  { width: 28px; height: 28px; border-radius: 50%; }
.skel-word  { flex: 2; }
.skel-cefr  { width: 44px; }
.skel-pos   { width: 70px; }
.skel-bar   { flex: 1; }
.skel-btns  { width: 160px; }

@keyframes shimmer {
  0%   { opacity: 0.5; }
  50%  { opacity: 1; }
  100% { opacity: 0.5; }
}

/* ── List TransitionGroup ── */
.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from {
  opacity:   0;
  transform: translateY(12px);
}
.list-leave-to {
  opacity:   0;
  transform: translateX(-30px);
}
.list-move {
  transition: transform 0.4s ease;
}
</style>
