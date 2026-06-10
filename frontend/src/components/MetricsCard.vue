<template>
  <div class="metrics-card glass" :class="{ loading: isLoading }">
    <div class="card-header">
      <div class="card-title">
        <span class="card-icon">📊</span>
        Algorithm Benchmark
      </div>
      <div class="card-tag mono">Held-out 20% test split</div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="isLoading" class="skeleton-wrapper">
      <div v-for="i in 3" :key="i" class="skeleton-row">
        <div class="skeleton-label"></div>
        <div class="skeleton-bar"></div>
      </div>
    </div>

    <!-- Metrics -->
    <div v-else class="metrics-grid">
      <!-- RMSE -->
      <div class="metric-item fade-slide" id="metric-rmse">
        <div class="metric-header">
          <div class="metric-label">
            <span class="metric-dot" :style="{ background: rmseColor }"></span>
            RMSE
          </div>
          <span class="metric-value mono" :style="{ color: rmseColor }">
            {{ metrics?.rmse?.toFixed(4) ?? '—' }}
          </span>
        </div>
        <div class="metric-bar-track">
          <div
            class="metric-bar-fill"
            :style="{ width: rmseBarWidth, background: rmseColor }"
          ></div>
        </div>
        <span class="metric-hint">Root Mean Squared Error (lower = better)</span>
      </div>

      <!-- MAE -->
      <div class="metric-item fade-slide" id="metric-mae" style="animation-delay:0.05s">
        <div class="metric-header">
          <div class="metric-label">
            <span class="metric-dot" :style="{ background: maeColor }"></span>
            MAE
          </div>
          <span class="metric-value mono" :style="{ color: maeColor }">
            {{ metrics?.mae?.toFixed(4) ?? '—' }}
          </span>
        </div>
        <div class="metric-bar-track">
          <div
            class="metric-bar-fill"
            :style="{ width: maeBarWidth, background: maeColor }"
          ></div>
        </div>
        <span class="metric-hint">Mean Absolute Error (lower = better)</span>
      </div>

      <!-- Precision@5 -->
      <div class="metric-item fade-slide" id="metric-p5" style="animation-delay:0.10s">
        <div class="metric-header">
          <div class="metric-label">
            <span class="metric-dot" :style="{ background: precColor }"></span>
            Precision@5
          </div>
          <span class="metric-value mono" :style="{ color: precColor }">
            {{ metrics?.precision_at_5 != null ? (metrics.precision_at_5 * 100).toFixed(1) + '%' : '—' }}
          </span>
        </div>
        <div class="metric-bar-track">
          <div
            class="metric-bar-fill"
            :style="{ width: precBarWidth, background: precColor }"
          ></div>
        </div>
        <span class="metric-hint">Fraction of top-5 recs that are relevant (higher = better)</span>
      </div>
    </div>

    <!-- Rated words counter -->
    <div v-if="ratedCount != null" class="rated-count">
      <span class="pulse-dot"></span>
      <span>{{ ratedCount }} words rated by this user</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  metrics:   { type: Object, default: null },
  ratedCount:{ type: Number, default: null },
  isLoading: { type: Boolean, default: false },
})

// ── RMSE: 0 is perfect, 4 is worst possible (rating scale 1-5)
const rmseColor = computed(() => {
  const v = props.metrics?.rmse ?? 2
  if (v < 0.7) return '#10b981'   // green
  if (v < 1.2) return '#f59e0b'   // amber
  return '#ef4444'                  // red
})
const rmseBarWidth = computed(() => {
  const v = props.metrics?.rmse ?? 0
  return Math.max(4, Math.min(100, (1 - v / 4) * 100)) + '%'
})

// ── MAE
const maeColor = computed(() => {
  const v = props.metrics?.mae ?? 2
  if (v < 0.5) return '#10b981'
  if (v < 1.0) return '#f59e0b'
  return '#ef4444'
})
const maeBarWidth = computed(() => {
  const v = props.metrics?.mae ?? 0
  return Math.max(4, Math.min(100, (1 - v / 4) * 100)) + '%'
})

// ── Precision@5: 1.0 is perfect
const precColor = computed(() => {
  const v = props.metrics?.precision_at_5 ?? 0
  if (v > 0.6) return '#10b981'
  if (v > 0.3) return '#f59e0b'
  return '#ef4444'
})
const precBarWidth = computed(() => {
  const v = props.metrics?.precision_at_5 ?? 0
  return Math.max(4, Math.min(100, v * 100)) + '%'
})
</script>

<style scoped>
.metrics-card {
  padding: 20px;
  transition: opacity 0.2s;
}
.metrics-card.loading { opacity: 0.6; pointer-events: none; }

.card-header {
  display:       flex;
  align-items:   center;
  justify-content: space-between;
  margin-bottom: 18px;
  flex-wrap:     wrap;
  gap:           6px;
}
.card-title {
  display:     flex;
  align-items: center;
  gap:         8px;
  font-size:   14px;
  font-weight: 600;
}
.card-icon  { font-size: 16px; }
.card-tag   {
  font-size:  10px;
  color:      var(--clr-text-muted);
  background: var(--clr-surface);
  border:     1px solid var(--clr-border);
  padding:    2px 8px;
  border-radius: var(--radius-sm);
}

/* Metrics */
.metrics-grid { display: flex; flex-direction: column; gap: 16px; }

.metric-item { display: flex; flex-direction: column; gap: 5px; }

.metric-header {
  display:       flex;
  align-items:   center;
  justify-content: space-between;
}
.metric-label {
  display:     flex;
  align-items: center;
  gap:         7px;
  font-size:   12px;
  font-weight: 600;
  color:       var(--clr-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.07em;
}
.metric-dot   { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.metric-value { font-size: 16px; font-weight: 700; transition: color 0.3s; }

.metric-bar-track {
  height:        6px;
  background:    var(--clr-surface-hov);
  border-radius: 999px;
  overflow:      hidden;
}
.metric-bar-fill {
  height:        100%;
  border-radius: 999px;
  transition:    width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.metric-hint {
  font-size: 10px;
  color:     var(--clr-text-faint);
}

/* Skeleton */
.skeleton-wrapper { display: flex; flex-direction: column; gap: 16px; }
.skeleton-row    { display: flex; flex-direction: column; gap: 6px; }
.skeleton-label  { height: 12px; width: 60px; background: var(--clr-surface-hov); border-radius: 4px; animation: shimmer 1.2s infinite; }
.skeleton-bar    { height: 6px; width: 100%; background: var(--clr-surface-hov); border-radius: 999px; animation: shimmer 1.2s infinite 0.2s; }

@keyframes shimmer {
  0%   { opacity: 0.5; }
  50%  { opacity: 1; }
  100% { opacity: 0.5; }
}

/* Rated count */
.rated-count {
  display:     flex;
  align-items: center;
  gap:         8px;
  margin-top:  16px;
  padding-top: 14px;
  border-top:  1px solid var(--clr-border);
  font-size:   12px;
  color:       var(--clr-text-muted);
}
</style>
