<template>
  <div class="charts-panel">

    <!-- ══ Section Header ══ -->
    <div class="panel-header">
      <div class="panel-title">
        <span class="panel-icon">📈</span>
        <div>
          <div class="panel-name">Experimental Analysis</div>
          <div class="panel-sub">Visual comparison of all 4 recommender paradigms · MRW2 Research</div>
        </div>
      </div>
    </div>

    <!-- ══ Row 1: Algorithm Comparison + CEFR Donut ══ -->
    <div class="charts-row">

      <!-- ── Grouped Bar Chart: Algorithm Benchmark ── -->
      <div class="chart-card glass chart-card--large">
        <div class="chart-card-header">
          <div class="chart-card-title">
            <span>🏆</span> Algorithm Benchmark Comparison
          </div>
          <div class="chart-card-sub">RMSE &amp; MAE (lower = better) · Precision@5 (higher = better)</div>
        </div>
        <div class="chart-container" style="height: 280px;">
          <canvas ref="barChartRef" id="chart-algo-comparison"></canvas>
        </div>
        <div class="chart-legend">
          <span v-for="m in metricMeta" :key="m.key" class="legend-item">
            <span class="legend-dot" :style="{ background: m.color }"></span>
            {{ m.label }}
          </span>
        </div>
      </div>

      <!-- ── Donut Chart: CEFR Distribution ── -->
      <div class="chart-card glass chart-card--small">
        <div class="chart-card-header">
          <div class="chart-card-title">
            <span>🎯</span> CEFR Recommendation Distribution
          </div>
          <div class="chart-card-sub">CEFR levels of the current Top-5</div>
        </div>
        <div class="chart-container donut-container">
          <canvas ref="donutChartRef" id="chart-cefr-donut"></canvas>
          <div class="donut-center" v-if="totalRecs > 0">
            <div class="donut-count">{{ totalRecs }}</div>
            <div class="donut-label">words</div>
          </div>
          <div class="donut-empty" v-else>
            No data yet
          </div>
        </div>
        <!-- CEFR Legend -->
        <div class="cefr-legend">
          <div
            v-for="item in cefrLegendItems"
            :key="item.level"
            class="cefr-legend-row"
          >
            <span class="cefr-dot" :style="{ background: item.color }"></span>
            <span class="cefr-level-label">{{ item.level }}</span>
            <div class="cefr-mini-bar-track">
              <div class="cefr-mini-bar" :style="{ width: item.pct + '%', background: item.color }"></div>
            </div>
            <span class="cefr-count">{{ item.count }}</span>
          </div>
        </div>
      </div>

    </div>

    <!-- ══ Row 2: Architecture Diagram ══ -->
    <div class="chart-card glass arch-card">
      <div class="chart-card-header">
        <div class="chart-card-title"><span>🏗</span> Hybrid Recommender System Architecture</div>
        <div class="chart-card-sub">
          Cold-Start path (CBF) vs Active-User path (weighted ensemble) · Zone of Proximal Development aware
        </div>
      </div>

      <div class="arch-diagram">
        <!-- Input -->
        <div class="arch-col arch-col--input">
          <div class="arch-node arch-node--user">
            <div class="arch-node-icon">👤</div>
            <div class="arch-node-label">Learner Profile</div>
            <div class="arch-node-sub">CEFR Level + Ratings</div>
          </div>
          <div class="arch-branch-labels">
            <span class="arch-branch-tag arch-branch-tag--cold">❄ Cold-Start</span>
            <span class="arch-branch-tag arch-branch-tag--active">✓ Active User</span>
          </div>
        </div>

        <!-- Arrow -->
        <div class="arch-arrow-col">
          <div class="arch-arrow arch-arrow--split">
            <svg viewBox="0 0 80 160" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Top branch line (to CBF) -->
              <path d="M10 80 L10 30 L70 30" stroke="#6366f1" stroke-width="1.5" stroke-dasharray="4 3"/>
              <!-- Middle branch line (to SVD) -->
              <path d="M10 80 L10 80 L70 80" stroke="#8b5cf6" stroke-width="1.5" stroke-dasharray="4 3"/>
              <!-- Bottom branch line (to AE) -->
              <path d="M10 80 L10 130 L70 130" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="4 3"/>
              <!-- Arrowheads -->
              <polygon points="68,26 76,30 68,34" fill="#6366f1"/>
              <polygon points="68,76 76,80 68,84" fill="#8b5cf6"/>
              <polygon points="68,126 76,130 68,134" fill="#06b6d4"/>
              <!-- Vertical stem -->
              <line x1="10" y1="30" x2="10" y2="130" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
            </svg>
          </div>
        </div>

        <!-- Engines column -->
        <div class="arch-col arch-col--engines">
          <div class="arch-node arch-node--cbf">
            <div class="arch-node-icon">📖</div>
            <div class="arch-node-label">Content-Based</div>
            <div class="arch-node-sub">Cosine Sim · CEFR+POS</div>
            <div class="arch-node-weight arch-node-weight--cbf">40%</div>
          </div>
          <div class="arch-node arch-node--svd">
            <div class="arch-node-icon">🔢</div>
            <div class="arch-node-label">SVD · ColFilt</div>
            <div class="arch-node-sub">TruncatedSVD k=20</div>
            <div class="arch-node-weight arch-node-weight--svd">35%</div>
          </div>
          <div class="arch-node arch-node--ae">
            <div class="arch-node-icon">🧠</div>
            <div class="arch-node-label">Autoencoder</div>
            <div class="arch-node-sub">PyTorch 300→32→300</div>
            <div class="arch-node-weight arch-node-weight--ae">25%</div>
          </div>
        </div>

        <!-- Merge arrow -->
        <div class="arch-arrow-col">
          <div class="arch-arrow arch-arrow--merge">
            <svg viewBox="0 0 80 160" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Lines merging from 3 engines -->
              <path d="M10 30 L10 80 L70 80" stroke="#6366f1" stroke-width="1.5" stroke-dasharray="4 3"/>
              <path d="M10 80 L70 80" stroke="#8b5cf6" stroke-width="1.5" stroke-dasharray="4 3"/>
              <path d="M10 130 L10 80 L70 80" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="4 3"/>
              <!-- Arrowhead to hybrid -->
              <polygon points="68,76 76,80 68,84" fill="#f59e0b"/>
              <!-- Vertical stem -->
              <line x1="10" y1="30" x2="10" y2="130" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
            </svg>
          </div>
        </div>

        <!-- Hybrid engine -->
        <div class="arch-col arch-col--hybrid">
          <div class="arch-node arch-node--hybrid">
            <div class="arch-node-icon">⚡</div>
            <div class="arch-node-label">Hybrid Engine</div>
            <div class="arch-node-sub">Weighted Ensemble</div>
            <div class="arch-node-formula">
              0.40 × CBF<br>+ 0.35 × SVD<br>+ 0.25 × AE
            </div>
            <div class="arch-node-cold-label">Cold-Start → CBF only</div>
          </div>
        </div>

        <!-- Final arrow -->
        <div class="arch-arrow-col arch-arrow-col--final">
          <svg width="40" height="24" viewBox="0 0 40 24" fill="none">
            <path d="M0 12 L32 12" stroke="#f59e0b" stroke-width="2"/>
            <polygon points="30,8 38,12 30,16" fill="#f59e0b"/>
          </svg>
        </div>

        <!-- Output -->
        <div class="arch-col arch-col--output">
          <div class="arch-node arch-node--output">
            <div class="arch-node-icon">🎓</div>
            <div class="arch-node-label">Top-5 Vocabulary</div>
            <div class="arch-node-sub">ZPD-aligned words</div>
            <div class="arch-output-pills">
              <span class="out-pill out-pill--b1">B1</span>
              <span class="out-pill out-pill--b2">B2</span>
              <span class="out-pill out-pill--c1">C1</span>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  DoughnutController,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'

// Register only what we need (tree-shakeable)
Chart.register(
  BarController, BarElement, CategoryScale, LinearScale,
  DoughnutController, ArcElement,
  Tooltip, Legend,
)

// ── Props ─────────────────────────────────────────────────────
const props = defineProps({
  allMetrics:      { type: Object, default: () => ({}) },
  recommendations: { type: Array,  default: () => [] },
})

// ── Chart refs ────────────────────────────────────────────────
const barChartRef   = ref(null)
const donutChartRef = ref(null)
let   barChart      = null
let   donutChart    = null

// ── Metric metadata ──────────────────────────────────────────
const metricMeta = [
  { key: 'rmse',           label: 'RMSE (lower=better)',      color: '#ef4444' },
  { key: 'mae',            label: 'MAE (lower=better)',       color: '#f97316' },
  { key: 'precision_at_5', label: 'Precision@5 (higher=best)', color: '#10b981' },
]

const ALGO_LABELS  = ['Content-Based', 'SVD', 'Autoencoder', 'Hybrid']
const ALGO_KEYS    = ['content', 'svd', 'autoencoder', 'hybrid']
const ALGO_COLORS  = ['#6366f1', '#8b5cf6', '#06b6d4', '#f59e0b']

// ── Bar chart data ────────────────────────────────────────────
function buildBarDatasets() {
  return metricMeta.map(m => ({
    label:           m.label,
    data:            ALGO_KEYS.map(k => props.allMetrics[k]?.[m.key] ?? 0),
    backgroundColor: m.color + 'cc',
    borderColor:     m.color,
    borderWidth:     1.5,
    borderRadius:    5,
    borderSkipped:   false,
  }))
}

function initBarChart() {
  if (!barChartRef.value) return
  if (barChart) { barChart.destroy(); barChart = null }

  const ctx = barChartRef.value.getContext('2d')
  barChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels:   ALGO_LABELS,
      datasets: buildBarDatasets(),
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#131929',
          borderColor:     'rgba(255,255,255,0.08)',
          borderWidth:     1,
          titleColor:      '#e2e8f0',
          bodyColor:       '#94a3b8',
          padding:         12,
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(4)}`,
          },
        },
      },
      scales: {
        x: {
          ticks: { color: '#94a3b8', font: { size: 11, family: 'Inter' } },
          grid:  { color: 'rgba(255,255,255,0.04)' },
          border:{ color: 'rgba(255,255,255,0.08)' },
        },
        y: {
          beginAtZero: true,
          max:         2,
          ticks: {
            color:     '#94a3b8',
            font:      { size: 10, family: 'JetBrains Mono' },
            stepSize:  0.5,
          },
          grid:   { color: 'rgba(255,255,255,0.06)' },
          border: { color: 'rgba(255,255,255,0.08)' },
        },
      },
    },
  })
}

// ── CEFR donut data ───────────────────────────────────────────
const CEFR_COLORS = {
  A1: '#22c55e', A2: '#86efac', B1: '#facc15',
  B2: '#f97316', C1: '#f87171', C2: '#ef4444',
}
const CEFR_ORDER = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const cefrCounts = computed(() => {
  const counts = { A1: 0, A2: 0, B1: 0, B2: 0, C1: 0, C2: 0 }
  props.recommendations.forEach(r => {
    if (counts[r.cefr_difficulty] !== undefined) counts[r.cefr_difficulty]++
  })
  return counts
})

const totalRecs = computed(() => props.recommendations.length)

const cefrLegendItems = computed(() =>
  CEFR_ORDER
    .filter(lvl => cefrCounts.value[lvl] > 0)
    .map(lvl => ({
      level: lvl,
      color: CEFR_COLORS[lvl],
      count: cefrCounts.value[lvl],
      pct:   totalRecs.value > 0
        ? Math.round((cefrCounts.value[lvl] / totalRecs.value) * 100)
        : 0,
    }))
)

function buildDonutData() {
  const labels = CEFR_ORDER.filter(l => cefrCounts.value[l] > 0)
  return {
    labels,
    datasets: [{
      data:            labels.map(l => cefrCounts.value[l]),
      backgroundColor: labels.map(l => CEFR_COLORS[l] + 'cc'),
      borderColor:     labels.map(l => CEFR_COLORS[l]),
      borderWidth:     2,
      hoverOffset:     8,
    }],
  }
}

function initDonutChart() {
  if (!donutChartRef.value) return
  if (donutChart) { donutChart.destroy(); donutChart = null }

  const ctx = donutChartRef.value.getContext('2d')
  donutChart = new Chart(ctx, {
    type: 'doughnut',
    data: buildDonutData(),
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      cutout:              '68%',
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#131929',
          borderColor:     'rgba(255,255,255,0.08)',
          borderWidth:     1,
          titleColor:      '#e2e8f0',
          bodyColor:       '#94a3b8',
          padding:         10,
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.parsed} word(s)`,
          },
        },
      },
    },
  })
}

// ── Watchers – update charts when data changes ────────────────
watch(
  () => props.allMetrics,
  () => {
    if (barChart) {
      barChart.data.datasets = buildBarDatasets()
      barChart.update('active')
    }
  },
  { deep: true },
)

watch(
  () => props.recommendations,
  async () => {
    await nextTick()
    if (donutChart) {
      const d = buildDonutData()
      donutChart.data.labels   = d.labels
      donutChart.data.datasets = d.datasets
      donutChart.update('active')
    }
  },
  { deep: true },
)

// ── Lifecycle ─────────────────────────────────────────────────
onMounted(async () => {
  await nextTick()
  initBarChart()
  initDonutChart()
})

onUnmounted(() => {
  barChart?.destroy()
  donutChart?.destroy()
})
</script>

<style scoped>
/* ── Panel wrapper ── */
.charts-panel {
  display:        flex;
  flex-direction: column;
  gap:            20px;
}

/* ── Section header ── */
.panel-header {
  display:     flex;
  align-items: center;
  gap:         12px;
}
.panel-title {
  display:     flex;
  align-items: center;
  gap:         12px;
}
.panel-icon  { font-size: 22px; }
.panel-name  { font-size: 15px; font-weight: 700; }
.panel-sub   { font-size: 11px; color: var(--clr-text-muted); margin-top: 2px; }

/* ── Row layouts ── */
.charts-row {
  display:   grid;
  grid-template-columns: 1fr 340px;
  gap:       20px;
}

/* ── Shared card ── */
.chart-card {
  padding:        20px;
  display:        flex;
  flex-direction: column;
  gap:            14px;
  min-width:      0;
}
.chart-card-header { display: flex; flex-direction: column; gap: 3px; }
.chart-card-title  {
  display:     flex;
  align-items: center;
  gap:         8px;
  font-size:   13px;
  font-weight: 600;
}
.chart-card-sub { font-size: 10px; color: var(--clr-text-muted); padding-left: 22px; }

/* ── Chart containers ── */
.chart-container {
  position: relative;
  width:    100%;
}
.donut-container {
  height:          200px;
  display:         flex;
  align-items:     center;
  justify-content: center;
  position:        relative;
}
.donut-center {
  position:        absolute;
  inset:           0;
  display:         flex;
  flex-direction:  column;
  align-items:     center;
  justify-content: center;
  pointer-events:  none;
}
.donut-count {
  font-size:   22px;
  font-weight: 800;
  line-height: 1;
  background:  linear-gradient(135deg, var(--clr-accent-from), var(--clr-accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.donut-label  { font-size: 10px; color: var(--clr-text-muted); text-transform: uppercase; letter-spacing: 0.06em; }
.donut-empty  { font-size: 12px; color: var(--clr-text-muted); position: absolute; }

/* ── Bar chart legend ── */
.chart-legend {
  display:   flex;
  flex-wrap: wrap;
  gap:       12px;
  padding-left: 4px;
}
.legend-item {
  display:     flex;
  align-items: center;
  gap:         5px;
  font-size:   10px;
  color:       var(--clr-text-muted);
}
.legend-dot {
  width:         8px; height: 8px;
  border-radius: 2px;
  flex-shrink:   0;
}

/* ── CEFR legend ── */
.cefr-legend  { display: flex; flex-direction: column; gap: 6px; }
.cefr-legend-row {
  display:     flex;
  align-items: center;
  gap:         8px;
  font-size:   11px;
}
.cefr-dot         { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.cefr-level-label { font-weight: 700; width: 24px; }
.cefr-mini-bar-track {
  flex:          1;
  height:        4px;
  background:    var(--clr-surface-hov);
  border-radius: 999px;
  overflow:      hidden;
}
.cefr-mini-bar {
  height:        100%;
  border-radius: 999px;
  transition:    width 0.5s ease;
}
.cefr-count { font-size: 10px; color: var(--clr-text-muted); width: 14px; text-align: right; }

/* ════════════════════════════════
   Architecture Diagram
   ════════════════════════════════ */
.arch-card { padding: 20px 24px; }

.arch-diagram {
  display:     flex;
  align-items: center;
  gap:         0;
  overflow-x:  auto;
  padding:     8px 0 4px;
}

/* Columns */
.arch-col {
  display:        flex;
  flex-direction: column;
  align-items:    center;
  gap:            10px;
  flex-shrink:    0;
}
.arch-col--input   { min-width: 130px; }
.arch-col--engines { gap: 8px; }
.arch-col--hybrid  { min-width: 148px; }
.arch-col--output  { min-width: 130px; }

/* Nodes */
.arch-node {
  display:        flex;
  flex-direction: column;
  align-items:    center;
  gap:            3px;
  padding:        12px 14px;
  border-radius:  var(--radius-md);
  background:     var(--clr-surface);
  border:         1px solid var(--clr-border);
  text-align:     center;
  width:          100%;
  position:       relative;
  transition:     border-color 0.2s, box-shadow 0.2s;
}
.arch-node:hover {
  border-color: var(--clr-border-hov);
  box-shadow:   0 4px 20px rgba(0,0,0,0.3);
}
.arch-node-icon  { font-size: 18px; line-height: 1; }
.arch-node-label { font-size: 11px; font-weight: 700; margin-top: 2px; }
.arch-node-sub   { font-size: 9px; color: var(--clr-text-muted); }

.arch-node--user   { border-color: rgba(99,102,241,0.4); box-shadow: 0 0 20px rgba(99,102,241,0.08); }
.arch-node--cbf    { border-color: rgba(99,102,241,0.35); }
.arch-node--svd    { border-color: rgba(139,92,246,0.35); }
.arch-node--ae     { border-color: rgba(6,182,212,0.35); }
.arch-node--hybrid {
  border-color: rgba(245,158,11,0.5);
  box-shadow:   0 0 24px rgba(245,158,11,0.1);
  min-width:    138px;
}
.arch-node--output {
  border-color: rgba(16,185,129,0.4);
  box-shadow:   0 0 20px rgba(16,185,129,0.08);
}

/* Weight badges */
.arch-node-weight {
  margin-top:    4px;
  font-size:     10px;
  font-weight:   800;
  padding:       2px 7px;
  border-radius: var(--radius-sm);
}
.arch-node-weight--cbf { background: rgba(99,102,241,0.15); color: #6366f1; }
.arch-node-weight--svd { background: rgba(139,92,246,0.15); color: #8b5cf6; }
.arch-node-weight--ae  { background: rgba(6,182,212,0.15);  color: #06b6d4; }

/* Hybrid formula */
.arch-node-formula {
  font-family: 'JetBrains Mono', monospace;
  font-size:   8.5px;
  color:       var(--clr-text-muted);
  line-height: 1.7;
  margin-top:  4px;
  text-align:  left;
  padding:     4px 8px;
  background:  rgba(245,158,11,0.06);
  border-radius: var(--radius-sm);
  width:       100%;
}
.arch-node-cold-label {
  font-size:     9px;
  color:         var(--clr-accent2);
  margin-top:    3px;
}

/* Branch labels */
.arch-branch-labels {
  display:        flex;
  flex-direction: column;
  gap:            4px;
  width:          100%;
  padding-top:    6px;
}
.arch-branch-tag {
  font-size:     9px;
  font-weight:   700;
  padding:       2px 8px;
  border-radius: var(--radius-sm);
  text-align:    center;
}
.arch-branch-tag--cold   { background: rgba(6,182,212,0.12); color: var(--clr-accent2); border: 1px solid rgba(6,182,212,0.25); }
.arch-branch-tag--active { background: rgba(16,185,129,0.1); color: var(--clr-success); border: 1px solid rgba(16,185,129,0.25); }

/* Arrow columns */
.arch-arrow-col { display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.arch-arrow--split, .arch-arrow--merge { width: 80px; height: 160px; }
.arch-arrow-col--final { padding: 0 8px; }

/* Output pills */
.arch-output-pills { display: flex; gap: 4px; flex-wrap: wrap; justify-content: center; margin-top: 4px; }
.out-pill {
  font-size:     9px;
  font-weight:   800;
  padding:       2px 6px;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
}
.out-pill--b1 { background: rgba(250,204,21,0.15); color: var(--cefr-b1); }
.out-pill--b2 { background: rgba(249,115,22,0.15); color: var(--cefr-b2); }
.out-pill--c1 { background: rgba(248,113,113,0.15); color: var(--cefr-c1); }

/* Responsive */
@media (max-width: 900px) {
  .charts-row { grid-template-columns: 1fr; }
  .arch-diagram { gap: 0; }
}
</style>
