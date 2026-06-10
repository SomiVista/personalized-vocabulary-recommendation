<template>
  <div class="app-shell">
    <!-- ══ Background orbs ══ -->
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>
    <div class="orb orb-3" aria-hidden="true"></div>

    <!-- ══ Top Navigation ══ -->
    <header class="topbar" role="banner">
      <div class="topbar-left">
        <div class="brand">
          <div class="brand-logo">
            <svg width="22" height="22" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="url(#brand-grad)"/>
              <path d="M8 20L14 11L20 17L24 12" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="24" cy="12" r="2.5" fill="white"/>
              <defs>
                <linearGradient id="brand-grad" x1="0" y1="0" x2="32" y2="32">
                  <stop offset="0%" stop-color="#6366f1"/>
                  <stop offset="100%" stop-color="#8b5cf6"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div>
            <h1 class="brand-name grad-text">VocabAI Recommender</h1>
            <p class="brand-sub">MRW2 Research Prototype · VGTU</p>
          </div>
        </div>
      </div>

      <div class="topbar-right">
        <div class="status-pill" :class="backendStatus === 'online' ? 'status--online' : 'status--offline'">
          <span class="pulse-dot" v-if="backendStatus === 'online'"></span>
          <span v-else class="status-dot status-dot--off"></span>
          {{ backendStatus === 'online' ? 'Backend Online' : 'Backend Offline' }}
        </div>
        <div class="stat-chip">
          <span class="stat-num">{{ users.length }}</span> users
        </div>
        <div class="stat-chip">
          <span class="stat-num">{{ wordCount }}</span> words
        </div>
      </div>
    </header>

    <!-- ══ Main Layout ══ -->
    <main class="main-layout" role="main">
      <!-- ── LEFT sidebar ── -->
      <aside class="sidebar" role="complementary" aria-label="Configuration panel">

        <!-- User Selector -->
        <section class="sidebar-section glass">
          <UserSelector
            v-model="selectedUser"
            :users="users"
            @update:modelValue="onUserChange"
          />
        </section>

        <!-- Algorithm Selector -->
        <section class="sidebar-section glass">
          <div class="section-title">
            <span>⚙️</span> Algorithm
          </div>
          <AlgorithmSelector
            v-model="selectedMethod"
          />
        </section>

        <!-- Metrics Card -->
        <MetricsCard
          :metrics="currentMetrics"
          :rated-count="ratedCount"
          :is-loading="loadingRec"
        />

      </aside>

      <!-- ── RIGHT content ── -->
      <section class="content-area" aria-label="Recommendations">

        <!-- Hero info banner -->
        <div class="hero-banner glass fade-slide" v-if="!selectedUser">
          <div class="hero-icon">🎓</div>
          <div>
            <div class="hero-title">Personalized Vocabulary Recommender</div>
            <div class="hero-sub">
              Select a learner from the left panel to see AI-powered word recommendations.
              Compare four recommendation algorithms: Content-Based, SVD, Autoencoder, and Hybrid.
            </div>
          </div>
        </div>

        <!-- Recommendation Table -->
        <RecommendationTable
          v-if="selectedUser"
          :recommendations="recommendations"
          :user-id="selectedUser?.user_id"
          :method="selectedMethod"
          :is-cold-start="selectedUser?.is_cold_start"
          :is-loading="loadingRec"
          @refresh="fetchRecommendations"
          @interacted="onInteracted"
        />

        <!-- Charts Panel -->
        <ChartsPanel
          v-if="selectedUser"
          :all-metrics="allMetrics"
          :recommendations="recommendations"
        />

        <!-- Interaction log -->
        <div v-if="interactionLog.length" class="log-panel glass fade-slide">
          <div class="log-header">
            <span>📝</span> Interaction Log
            <button class="log-clear mono" @click="interactionLog = []">clear</button>
          </div>
          <div class="log-scroll">
            <div
              v-for="(entry, i) in [...interactionLog].reverse()"
              :key="i"
              class="log-entry"
            >
              <span class="log-icon">{{ entry.rating === 5 ? '✓' : '📖' }}</span>
              <span class="log-word">{{ entry.word.word }}</span>
              <span class="log-cefr cefr-badge" :class="`cefr--${entry.word.cefr_difficulty.toLowerCase()}`">
                {{ entry.word.cefr_difficulty }}
              </span>
              <span class="log-rating mono">rating={{ entry.rating }}</span>
              <span class="log-time mono">{{ entry.time }}</span>
            </div>
          </div>
        </div>

      </section>
    </main>

    <!-- ══ Error toast ══ -->
    <Transition name="toast">
      <div v-if="errorMsg" class="error-toast" role="alert" id="error-toast">
        ⚠ {{ errorMsg }}
        <button class="toast-close" @click="errorMsg = ''">✕</button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import UserSelector        from './components/UserSelector.vue'
import AlgorithmSelector   from './components/AlgorithmSelector.vue'
import MetricsCard         from './components/MetricsCard.vue'
import RecommendationTable from './components/RecommendationTable.vue'
import ChartsPanel         from './components/ChartsPanel.vue'

// ── State ──────────────────────────────────────────────────
const users          = ref([])
const wordCount      = ref(0)
const selectedUser   = ref(null)
const selectedMethod = ref('hybrid')
const recommendations = ref([])
const currentMetrics = ref(null)
const allMetrics     = ref({})   // all 4 methods' metrics for charts
const ratedCount     = ref(null)
const loadingRec     = ref(false)
const backendStatus  = ref('offline')
const errorMsg       = ref('')
const interactionLog = ref([])

// ── Lifecycle ──────────────────────────────────────────────
onMounted(async () => {
  await loadInitialData()
})

// ── Data loading ───────────────────────────────────────────
async function loadInitialData() {
  try {
    const [usersRes, wordsRes] = await Promise.all([
      fetch('/api/users'),
      fetch('/api/words'),
    ])

    if (!usersRes.ok || !wordsRes.ok) throw new Error('Backend response error')

    const usersData = await usersRes.json()
    const wordsData = await wordsRes.json()

    users.value     = usersData.users
    wordCount.value = wordsData.words.length
    backendStatus.value = 'online'

    // Pre-select first active user for a nice first impression
    const firstActive = users.value.find(u => !u.is_cold_start)
    if (firstActive) {
      selectedUser.value = firstActive
      await fetchRecommendations()
      fetchAllMetrics(firstActive.user_id)  // populate comparison charts
    }
  } catch (err) {
    console.error('[init] Backend error:', err)
    backendStatus.value = 'offline'
    showError('Cannot reach backend. Is the FastAPI server running on port 8000?')
  }
}

async function fetchRecommendations() {
  if (!selectedUser.value) return
  loadingRec.value = true
  errorMsg.value   = ''

  try {
    const params = new URLSearchParams({
      user_id: selectedUser.value.user_id,
      method:  selectedMethod.value,
    })
    const res  = await fetch(`/api/recommend?${params}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()

    recommendations.value = data.recommendations
    currentMetrics.value  = data.metrics
    ratedCount.value      = data.rated_words
  } catch (err) {
    console.error('[recommend] Error:', err)
    showError(`Failed to fetch recommendations: ${err.message}`)
    recommendations.value = []
  } finally {
    loadingRec.value = false
  }
}

// Fetch all 4 algorithms' metrics in parallel for the comparison chart
async function fetchAllMetrics(userId) {
  if (!userId) return
  const methods = ['content', 'svd', 'autoencoder', 'hybrid']
  try {
    const results = await Promise.all(
      methods.map(m =>
        fetch(`/api/recommend?user_id=${userId}&method=${m}&top_n=5`)
          .then(r => r.ok ? r.json() : null)
      )
    )
    const newMetrics = {}
    methods.forEach((m, i) => {
      if (results[i]?.metrics) newMetrics[m] = results[i].metrics
    })
    allMetrics.value = newMetrics
  } catch (err) {
    console.warn('[fetchAllMetrics] Failed:', err)
  }
}

// ── Watchers ───────────────────────────────────────────────
// Watch selectedMethod so any algorithm tab click immediately fetches
// new recommendations. Using watch() ensures selectedMethod.value is
// already updated before fetchRecommendations() reads it.
watch(selectedMethod, () => {
  if (selectedUser.value) {
    recommendations.value = []
    fetchRecommendations()
  }
})

// ── Event handlers ─────────────────────────────────────────
function onUserChange(user) {
  selectedUser.value = user
  recommendations.value = []
  fetchRecommendations()
  fetchAllMetrics(user.user_id)   // refresh comparison chart for new user
}


function onInteracted({ word, rating }) {
  const now = new Date()
  interactionLog.value.push({
    word,
    rating,
    time: now.toLocaleTimeString(),
  })
  // fetchRecommendations is called by RecommendationTable after delay
}

function showError(msg) {
  errorMsg.value = msg
  setTimeout(() => { errorMsg.value = '' }, 6000)
}
</script>

<style>
/* ── App shell ── */
.app-shell {
  min-height:      100vh;
  position:        relative;
  overflow-x:      hidden;
  display:         flex;
  flex-direction:  column;
}

/* ── Background orbs ── */
.orb {
  position:      fixed;
  border-radius: 50%;
  filter:        blur(80px);
  pointer-events: none;
  z-index:       0;
  opacity:       0.25;
}
.orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, #6366f1, transparent);
  top: -150px; left: -150px;
}
.orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, #8b5cf6, transparent);
  bottom: -100px; right: -100px;
}
.orb-3 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, #06b6d4, transparent);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.08;
}

/* ── Topbar ── */
.topbar {
  position:       relative;
  z-index:        10;
  display:        flex;
  align-items:    center;
  justify-content: space-between;
  padding:        14px 28px;
  border-bottom:  1px solid var(--clr-border);
  background:     rgba(9,11,20,0.85);
  backdrop-filter: blur(16px);
  flex-wrap:      wrap;
  gap:            12px;
}

.topbar-left, .topbar-right {
  display:     flex;
  align-items: center;
  gap:         14px;
}

.brand {
  display:     flex;
  align-items: center;
  gap:         12px;
}
.brand-logo {
  flex-shrink: 0;
  line-height: 0;
}
.brand-name {
  font-size:   18px;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.brand-sub {
  font-size:  10px;
  color:      var(--clr-text-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-top: 1px;
}

.status-pill {
  display:       flex;
  align-items:   center;
  gap:           6px;
  font-size:     11px;
  font-weight:   600;
  padding:       5px 12px;
  border-radius: 999px;
}
.status--online {
  background: rgba(16,185,129,0.1);
  border:     1px solid rgba(16,185,129,0.25);
  color:      var(--clr-success);
}
.status--offline {
  background: rgba(239,68,68,0.1);
  border:     1px solid rgba(239,68,68,0.25);
  color:      var(--clr-error);
}
.status-dot--off {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--clr-error);
}

.stat-chip {
  font-size:  11px;
  color:      var(--clr-text-muted);
  background: var(--clr-surface);
  border:     1px solid var(--clr-border);
  padding:    4px 10px;
  border-radius: var(--radius-sm);
}
.stat-num {
  font-weight: 700;
  color:       var(--clr-text);
  margin-right: 3px;
}

/* ── Main layout ── */
.main-layout {
  position:   relative;
  z-index:    1;
  display:    grid;
  grid-template-columns: 320px 1fr;
  gap:        24px;
  padding:    24px 28px;
  flex:       1;
  min-height: 0;
  max-width:  1600px;
  margin:     0 auto;
  width:      100%;
}

/* ── Sidebar ── */
.sidebar {
  display:        flex;
  flex-direction: column;
  gap:            16px;
  position:       sticky;
  top:            24px;
  align-self:     start;
  max-height:     calc(100vh - 100px);
  overflow-y:     auto;
}
.sidebar::-webkit-scrollbar { display: none; }

.sidebar-section {
  padding: 18px;
}

.section-title {
  display:     flex;
  align-items: center;
  gap:         6px;
  font-size:   11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color:       var(--clr-text-muted);
  margin-bottom: 12px;
}

/* ── Content area ── */
.content-area {
  display:        flex;
  flex-direction: column;
  gap:            20px;
  min-width:      0;
}

/* ── Hero banner ── */
.hero-banner {
  display:     flex;
  align-items: flex-start;
  gap:         20px;
  padding:     28px 28px;
}
.hero-icon  { font-size: 48px; line-height: 1; flex-shrink: 0; }
.hero-title {
  font-size:   22px;
  font-weight: 700;
  background:  linear-gradient(135deg, var(--clr-accent-from), var(--clr-accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}
.hero-sub {
  font-size:  14px;
  color:      var(--clr-text-muted);
  line-height: 1.65;
  max-width:  540px;
}

/* ── Interaction log ── */
.log-panel { padding: 16px; }
.log-header {
  display:     flex;
  align-items: center;
  gap:         8px;
  font-size:   12px;
  font-weight: 600;
  margin-bottom: 10px;
  color:       var(--clr-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.07em;
}
.log-clear {
  margin-left: auto;
  background:  none;
  border:      none;
  color:       var(--clr-text-faint);
  cursor:      pointer;
  font-size:   10px;
  padding:     2px 6px;
  border-radius: var(--radius-sm);
  transition:  color 0.15s;
}
.log-clear:hover { color: var(--clr-error); }

.log-scroll {
  display:        flex;
  flex-direction: column;
  gap:            4px;
  max-height:     160px;
  overflow-y:     auto;
}
.log-entry {
  display:     flex;
  align-items: center;
  gap:         8px;
  font-size:   12px;
  padding:     5px 6px;
  border-radius: var(--radius-sm);
  background:  var(--clr-surface);
  animation:   fadeSlideIn 0.2s ease;
}
.log-icon   { width: 18px; text-align: center; }
.log-word   { font-weight: 600; flex: 1; }
.log-rating { color: var(--clr-accent2); }
.log-time   { color: var(--clr-text-faint); font-size: 10px; margin-left: auto; }

.cefr-badge { display: inline-block; font-size: 9px; font-weight: 800; padding: 1px 5px; border-radius: 3px; text-transform: uppercase; }
.cefr--a1 { background: rgba(34,197,94,0.15);  color: var(--cefr-a1); }
.cefr--a2 { background: rgba(134,239,172,0.12); color: var(--cefr-a2); }
.cefr--b1 { background: rgba(250,204,21,0.12);  color: var(--cefr-b1); }
.cefr--b2 { background: rgba(249,115,22,0.12);  color: var(--cefr-b2); }
.cefr--c1 { background: rgba(248,113,113,0.12); color: var(--cefr-c1); }
.cefr--c2 { background: rgba(239,68,68,0.12);   color: var(--cefr-c2); }

/* ── Error toast ── */
.error-toast {
  position:      fixed;
  bottom:        24px;
  left:          50%;
  transform:     translateX(-50%);
  z-index:       999;
  display:       flex;
  align-items:   center;
  gap:           12px;
  padding:       12px 20px;
  background:    rgba(239,68,68,0.15);
  border:        1px solid rgba(239,68,68,0.35);
  border-radius: var(--radius-md);
  color:         #fca5a5;
  font-size:     13px;
  backdrop-filter: blur(12px);
  box-shadow:    0 8px 32px rgba(0,0,0,0.5);
  max-width:     500px;
}
.toast-close {
  background:  none;
  border:      none;
  color:       currentColor;
  cursor:      pointer;
  font-size:   14px;
  margin-left: auto;
  opacity:     0.7;
  padding:     0 2px;
}
.toast-close:hover { opacity: 1; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(20px); }

/* ── Responsive ── */
@media (max-width: 900px) {
  .main-layout {
    grid-template-columns: 1fr;
    padding: 16px;
  }
  .sidebar {
    position: static;
    max-height: none;
  }
}
</style>
