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
          :session-mastery-count="sessionMasteryCount"
          @refresh="fetchRecommendations"
          @interacted="onInteracted"
          @mastered="onMastered"
          @word-click="openWordDrawer"
        />

        <!-- Interaction log -->
        <div v-if="selectedUser" class="log-panel glass fade-slide">
          <div class="log-header">
            <span>📝</span> Interaction Log
            <button
              v-if="interactionLog.length"
              class="log-clear mono"
              @click="interactionLog = []"
            >
              clear
            </button>
          </div>
          
          <div v-if="interactionLog.length" class="log-scroll">
            <div
              v-for="(entry, i) in [...interactionLog].reverse()"
              :key="i"
              class="log-entry"
            >
              <span class="log-icon">{{ entry.rating === 5 ? '✓' : '📖' }}</span>
              <span class="log-word">{{ entry.word?.word || 'Unknown' }}</span>
              <span
                v-if="entry.word"
                class="log-cefr cefr-badge"
                :class="`cefr--${(entry.word.cefr_difficulty || 'a1').toLowerCase()}`"
              >
                {{ entry.word.cefr_difficulty }}
              </span>
              <span class="log-rating mono">rating={{ entry.rating }}</span>
              <span class="log-time mono">{{ entry.time }}</span>
            </div>
          </div>

          <div v-else class="log-empty-state">
            <div class="log-empty-icon">📝</div>
            <div class="log-empty-text">No interactions recorded yet.</div>
            <div class="log-empty-hint">Mark recommended words above as "Mastered" or "Study" to populate the log.</div>
          </div>
        </div>

        <!-- Charts Panel -->
        <ChartsPanel
          v-if="selectedUser"
          :all-metrics="allMetrics"
          :recommendations="recommendations"
          :user="selectedUser"
          :active-method="selectedMethod"
          @select-method="selectedMethod = $event"
        />

      </section>
    </main>

    <!-- Word Details Drawer — Backdrop (Feature 3) -->
    <Transition name="fade-backdrop">
      <div
        v-if="selectedWordForDrawer"
        class="drawer-backdrop"
        @click="closeWordDrawer"
        aria-hidden="true"
      ></div>
    </Transition>

    <!-- Word Details Drawer (Slide-over) -->
    <Transition name="slide">
      <div v-if="selectedWordForDrawer" class="word-drawer glass" role="dialog" aria-modal="true" aria-label="Word details panel">
        <div class="drawer-header">
          <h2>Word Details</h2>
          <button class="btn-close" @click="closeWordDrawer" title="Close panel">✕</button>
        </div>
        <div class="drawer-content" v-if="selectedWordForDrawer">
          <div class="drawer-word-header">
            <h1 class="drawer-word">{{ selectedWordForDrawer.word }}</h1>
            <span class="cefr-badge" :class="`cefr--${selectedWordForDrawer.cefr_difficulty.toLowerCase()}`">
              {{ selectedWordForDrawer.cefr_difficulty }}
            </span>
            <span class="pos-chip">{{ selectedWordForDrawer.part_of_speech }}</span>
          </div>

          <!-- Score bar in drawer -->
          <div class="drawer-score-row" v-if="selectedWordForDrawer.score != null">
            <span class="drawer-score-label">Engine Score</span>
            <div class="drawer-score-bar-track">
              <div
                class="drawer-score-bar-fill"
                :style="{ width: drawerScoreWidth }"
              ></div>
            </div>
            <span class="drawer-score-val mono">{{ selectedWordForDrawer.score?.toFixed(3) }}</span>
          </div>

          <div class="drawer-section">
            <h3>🔍 Etymology &amp; Origin</h3>
            <p>{{ getWordDetails(selectedWordForDrawer).origin }}</p>
          </div>

          <div class="drawer-section">
            <h3>📖 Definition &amp; Context</h3>
            <p>{{ getWordDetails(selectedWordForDrawer).definition }}</p>
          </div>

          <div class="drawer-section">
            <h3>📝 Example Sentence</h3>
            <div class="example-box">
              <p class="example-text">"{{ getWordDetails(selectedWordForDrawer).example }}"</p>
              <span class="example-tag">Tailored for {{ selectedWordForDrawer.cefr_difficulty }}</span>
            </div>
          </div>

          <!-- Derivative Forms (Feature 3 enhancement) -->
          <div class="drawer-section">
            <h3>🔠 Derivative Forms</h3>
            <div class="derivative-grid">
              <div
                v-for="form in getDerivativeForms(selectedWordForDrawer)"
                :key="form.label"
                class="derivative-card"
              >
                <span class="derivative-tag">{{ form.label }}</span>
                <span class="derivative-word">{{ form.value }}</span>
              </div>
            </div>
          </div>

          <div class="drawer-section">
            <h3>🔗 Synonyms &amp; Antonyms</h3>
            <div class="syn-ant-row">
              <div>
                <strong>Synonyms:</strong>
                <div class="pills-list">
                  <span class="pill" v-for="s in getWordDetails(selectedWordForDrawer).synonyms" :key="s">{{ s }}</span>
                </div>
              </div>
              <div>
                <strong>Antonyms:</strong>
                <div class="pills-list">
                  <span class="pill" v-for="a in getWordDetails(selectedWordForDrawer).antonyms" :key="a">{{ a }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Audio controls in drawer -->
          <div class="drawer-audio-row">
            <button class="btn btn-primary pronounce-drawer-btn" @click="pronounceWord(selectedWordForDrawer.word, drawerAudioLang, drawerAudioRate)">
              🔊 Listen Pronunciation
            </button>
            <div class="drawer-audio-opts">
              <select class="drawer-audio-select" v-model="drawerAudioLang">
                <option value="en-US">🇺🇸 US English</option>
                <option value="en-GB">🇬🇧 UK English</option>
              </select>
              <select class="drawer-audio-select" v-model="drawerAudioRate">
                <option :value="1.0">Normal 1.0×</option>
                <option :value="0.75">Slow 0.75×</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </Transition>

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
import { ref, computed, onMounted, watch } from 'vue'
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

const selectedWordForDrawer = ref(null)
const sessionMasteryCount   = ref(0)
const drawerAudioLang       = ref('en-US')
const drawerAudioRate       = ref(1.0)

// Computed score bar width for drawer
const drawerScoreWidth = computed(() => {
  const s = selectedWordForDrawer.value?.score ?? 0
  const n = s <= 1 ? s : (s - 1) / 4
  return Math.max(4, Math.min(100, n * 100)) + '%'
})

// ── Word Details Database & Helpers ────────────────────────
const wordDetailsDb = {
  "apple": {
    origin: "Old English 'æppel', of Germanic origin.",
    definition: "A round fruit with red, green, or yellow skin and crisp white flesh.",
    example: "She took a bite of the sweet red apple.",
    synonyms: ["fruit", "pome"],
    antonyms: ["N/A"]
  },
  "run": {
    origin: "Old English 'rinnan', of Germanic origin.",
    definition: "Move at a speed faster than a walk, never having both feet on the ground at the same time.",
    example: "We need to run to catch the school bus.",
    synonyms: ["jog", "dash", "sprint"],
    antonyms: ["walk", "crawl"]
  },
  "big": {
    origin: "Middle English: of unknown origin.",
    definition: "Of considerable size, extent, or intensity.",
    example: "They live in a big house near the park.",
    synonyms: ["large", "huge", "giant"],
    antonyms: ["small", "tiny", "little"]
  },
  "paradox": {
    origin: "Greek 'paradoxon' - contrary to opinion.",
    definition: "A seemingly absurd or contradictory statement or proposition which when investigated may prove to be well founded or true.",
    example: "It is a paradox that computers need so much paper.",
    synonyms: ["contradiction", "anomaly", "puzzle"],
    antonyms: ["certainty", "consistency"]
  },
  "alleviate": {
    origin: "Late Latin 'alleviatus' - lightened.",
    definition: "Make suffering, deficiency, or a problem less severe.",
    example: "He took some medicine to alleviate his headache.",
    synonyms: ["ease", "relieve", "mitigate"],
    antonyms: ["aggravate", "worsen"]
  },
  "intricate": {
    origin: "Late Latin 'intricatus' - entangled.",
    definition: "Very detailed, complicated, or detailed.",
    example: "The watch has an intricate mechanism with many small gears.",
    synonyms: ["complex", "complicated", "elaborate"],
    antonyms: ["simple", "straightforward"]
  },
  "epistemology": {
    origin: "Greek 'episteme' (knowledge) + 'logos' (study).",
    definition: "The theory of knowledge, especially with regard to its methods, validity, and scope.",
    example: "Epistemology investigates the distinction between justified belief and opinion.",
    synonyms: ["philosophy of knowledge", "gnoseology"],
    antonyms: ["N/A"]
  },
  "obfuscate": {
    origin: "Latin 'obfuscat-' - darkened.",
    definition: "Make obscure, unclear, or unintelligible.",
    example: "The politician tried to obfuscate the issue with complex statistics.",
    synonyms: ["obscure", "confuse", "blur"],
    antonyms: ["clarify", "explain", "simplify"]
  },
  "solipsism": {
    origin: "Latin 'solus' (alone) + 'ipse' (self).",
    definition: "The view or theory that the self is all that can be known to exist.",
    example: "His solipsism made it difficult for him to empathize with the suffering of others.",
    synonyms: ["egoism", "subjectivism"],
    antonyms: ["altruism", "realism"]
  }
}

function getWordDetails(wordObj) {
  if (!wordObj) return { origin: '', definition: '', example: '', synonyms: [], antonyms: [] }
  const w = wordObj.word.toLowerCase()
  if (wordDetailsDb[w]) {
    return wordDetailsDb[w]
  }
  
  const pos = wordObj.part_of_speech
  const cefr = wordObj.cefr_difficulty
  
  let definition = `A dynamic vocabulary term classified as a ${pos} in standard English.`
  let origin = `Derived from historical root forms of Germanic and Latinate origin.`
  let example = `This ${pos} is essential for learners at the ${cefr} level.`
  let synonyms = ["term", "expression"]
  let antonyms = ["N/A"]
  
  if (pos === "Noun") {
    definition = `A noun denoting an object, concept, or phenomenon relevant to ${cefr} level discussions.`
    example = `We discussed the importance of this '${wordObj.word}' during our class yesterday.`
    synonyms = [wordObj.word + " concept", "entity", "idea"]
  } else if (pos === "Verb") {
    definition = `An action verb representing processes or states suitable for ${cefr} expression.`
    example = `Please try to ${wordObj.word} this concept when you write your summary.`
    synonyms = ["act", "perform", "execute"]
  } else if (pos === "Adjective") {
    definition = `A descriptive modifier to characterize subjects in ${cefr} environments.`
    example = `The results were very ${wordObj.word}, confirming our hypothesis.`
    synonyms = ["characteristic", "distinctive", "particular"]
  } else if (pos === "Adverb") {
    definition = `A modifier indicating manner, time, or degree.`
    example = `She completed the task ${wordObj.word}, exceeding our expectations.`
    synonyms = ["similarly", "directly", "adequately"]
  }
  
  return { origin, definition, example, synonyms, antonyms }
}

function openWordDrawer(word) {
  selectedWordForDrawer.value = word
}

function closeWordDrawer() {
  selectedWordForDrawer.value = null
}

/** Derivative forms generator (Feature 3) */
function getDerivativeForms(wordObj) {
  if (!wordObj) return []
  const w   = wordObj.word
  const pos = wordObj.part_of_speech
  const forms = []
  if (pos === 'Noun') {
    forms.push({ label: 'Verb',      value: w.endsWith('tion') ? w.replace('tion','te') : w + 'ize' })
    forms.push({ label: 'Adjective', value: w + 'al' })
    forms.push({ label: 'Adverb',    value: w + 'ally' })
  } else if (pos === 'Verb') {
    forms.push({ label: 'Noun',      value: w + 'tion' })
    forms.push({ label: 'Adjective', value: w + 'ive' })
    forms.push({ label: 'Past',      value: w.endsWith('e') ? w + 'd' : w + 'ed' })
  } else if (pos === 'Adjective') {
    forms.push({ label: 'Noun',      value: w + 'ness' })
    forms.push({ label: 'Adverb',    value: w + 'ly' })
    forms.push({ label: 'Comparative', value: 'more ' + w })
  } else if (pos === 'Adverb') {
    forms.push({ label: 'Adjective', value: w.endsWith('ly') ? w.slice(0,-2) : w })
    forms.push({ label: 'Noun',      value: w.endsWith('ly') ? w.slice(0,-2) + 'ness' : w + 'ness' })
  } else {
    forms.push({ label: 'Base', value: w })
  }
  return forms
}

function pronounceWord(text, lang = 'en-US', rate = 1.0) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = lang
    utterance.rate = rate
    const voices = window.speechSynthesis.getVoices()
    const match  = voices.find(v => v.lang.startsWith(lang.slice(0,5)))
    if (match) utterance.voice = match
    window.speechSynthesis.speak(utterance)
  }
}

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
  const currentUserId = selectedUser.value.user_id

  try {
    const params = new URLSearchParams({
      user_id: currentUserId,
      method:  selectedMethod.value,
    })
    const res  = await fetch(`/api/recommend?${params}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()

    // Race condition check: make sure user didn't change while request was in flight
    if (selectedUser.value?.user_id !== currentUserId) {
      return
    }

    recommendations.value = data.recommendations
    currentMetrics.value  = data.metrics
    ratedCount.value      = data.rated_words
    interactionLog.value  = data.interaction_log || []
  } catch (err) {
    if (selectedUser.value?.user_id === currentUserId) {
      console.error('[recommend] Error:', err)
      showError(`Failed to fetch recommendations: ${err.message}`)
      recommendations.value = []
      interactionLog.value  = []
      currentMetrics.value  = null
    }
  } finally {
    if (selectedUser.value?.user_id === currentUserId) {
      loadingRec.value = false
    }
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
    
    // Race condition check: if user changed, discard these metrics
    if (userId !== selectedUser.value?.user_id) {
      return
    }

    const newMetrics = {}
    methods.forEach((m, i) => {
      if (results[i]?.metrics) newMetrics[m] = results[i].metrics
    })
    allMetrics.value = newMetrics
  } catch (err) {
    console.warn('[fetchAllMetrics] Failed:', err)
  }
}

// Watch selectedUser to load/sync recommendations, metrics, and logs dynamically per user
watch(selectedUser, (newUser) => {
  recommendations.value = []
  interactionLog.value = []
  if (newUser) {
    fetchRecommendations()
    fetchAllMetrics(newUser.user_id)
  } else {
    currentMetrics.value = null
  }
})

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

function onInteracted({ word, rating }) {
  const now = new Date()
  interactionLog.value.push({
    word,
    rating,
    time: now.toLocaleTimeString(),
  })
  // fetchRecommendations is called by RecommendationTable after delay
}

function onMastered() {
  sessionMasteryCount.value++
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

/* ── Interaction log empty state ── */
.log-empty-state {
  display:        flex;
  flex-direction: column;
  align-items:    center;
  justify-content: center;
  padding:        30px 20px;
  gap:            6px;
  text-align:     center;
}
.log-empty-icon {
  font-size: 24px;
  opacity: 0.3;
}
.log-empty-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--clr-text-muted);
}
.log-empty-hint {
  font-size: 11px;
  color: var(--clr-text-faint);
}

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

/* ── Word details drawer (slide-over) ── */
.word-drawer {
  position:       fixed;
  top:            0;
  right:          0;
  width:          420px;
  height:         100vh;
  z-index:        1000;
  padding:        30px 24px;
  display:        flex;
  flex-direction: column;
  gap:            24px;
  backdrop-filter: blur(20px);
  border-left:    1px solid var(--clr-border);
  box-shadow:     -10px 0 30px rgba(0, 0, 0, 0.4);
}

.drawer-header {
  display:         flex;
  align-items:     center;
  justify-content: space-between;
}
.drawer-header h2 {
  font-size:   11px;
  font-weight: 700;
  color:       var(--clr-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.btn-close {
  background:  rgba(255,255,255,0.04);
  border:      1px solid var(--clr-border);
  color:       var(--clr-text);
  border-radius: 50%;
  width:       32px;
  height:      32px;
  display:     flex;
  align-items: center;
  justify-content: center;
  cursor:      pointer;
  font-size:   12px;
  transition:  all 0.2s;
}
.btn-close:hover {
  background:  rgba(255,255,255,0.1);
  border-color: var(--clr-border-hov);
}

.drawer-content {
  display:        flex;
  flex-direction: column;
  gap:            24px;
  flex:           1;
  overflow-y:     auto;
  padding-right:  4px;
}

.drawer-word-header {
  display:     flex;
  align-items: center;
  gap:         10px;
  flex-wrap:   wrap;
}
.drawer-word {
  font-size:   36px;
  font-weight: 800;
  line-height: 1.1;
  background:  linear-gradient(135deg, var(--clr-accent-from), var(--clr-accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  width:       100%;
  margin-bottom: 4px;
}
.drawer-word-header .cefr-badge {
  font-size: 11px;
  padding:   3px 8px;
}
.drawer-word-header .pos-chip {
  font-size:     11px;
  font-weight:   500;
  padding:       3px 8px;
  border-radius: var(--radius-sm);
  background:    rgba(99,102,241,0.1);
  color:         var(--clr-accent-from);
  border:        1px solid rgba(99,102,241,0.2);
}

.drawer-section {
  display:        flex;
  flex-direction: column;
  gap:            8px;
}
.drawer-section h3 {
  font-size:      11px;
  font-weight:    700;
  color:          var(--clr-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.drawer-section p {
  font-size:   14px;
  line-height: 1.6;
  color:       var(--clr-text);
}

.example-box {
  background:    rgba(255, 255, 255, 0.02);
  border:        1px solid var(--clr-border);
  padding:       14px;
  border-radius: var(--radius-md);
  position:      relative;
}
.example-text {
  font-style: italic;
  font-size:  14px;
  color:      var(--clr-text);
  line-height: 1.5;
}
.example-tag {
  display:    inline-block;
  font-size:  9px;
  color:      var(--clr-text-muted);
  margin-top: 8px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.syn-ant-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.pills-list {
  display:   flex;
  flex-wrap: wrap;
  gap:       6px;
  margin-top: 6px;
}
.pills-list .pill {
  font-size:     11px;
  padding:       3px 8px;
  border-radius: var(--radius-sm);
  background:    rgba(255,255,255,0.04);
  border:        1px solid var(--clr-border);
  color:         var(--clr-text);
}

.pronounce-drawer-btn {
  margin-top: auto;
  width:      100%;
  padding:    12px;
  font-size:  14px;
  font-weight: 700;
  border-radius: var(--radius-md);
}

/* Drawer Transitions */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* ── Drawer backdrop (Feature 3) ── */
.drawer-backdrop {
  position:   fixed;
  inset:      0;
  z-index:    999;
  background: rgba(5, 8, 20, 0.55);
  backdrop-filter: blur(6px);
}
.fade-backdrop-enter-active,
.fade-backdrop-leave-active { transition: opacity 0.3s ease; }
.fade-backdrop-enter-from,
.fade-backdrop-leave-to     { opacity: 0; }

/* ── Drawer score bar ── */
.drawer-score-row {
  display:     flex;
  align-items: center;
  gap:         10px;
  padding:     10px 14px;
  background:  rgba(99,102,241,0.06);
  border:      1px solid rgba(99,102,241,0.15);
  border-radius: var(--radius-md);
}
.drawer-score-label {
  font-size:   10px;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color:       var(--clr-accent-from);
  flex-shrink: 0;
}
.drawer-score-bar-track {
  flex:          1;
  height:        5px;
  background:    var(--clr-surface-hov);
  border-radius: 999px;
  overflow:      hidden;
}
.drawer-score-bar-fill {
  height:        100%;
  border-radius: 999px;
  background:    linear-gradient(90deg, var(--clr-accent-from), var(--clr-accent-to));
  transition:    width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.drawer-score-val {
  font-size:   11px;
  color:       var(--clr-text-muted);
  flex-shrink: 0;
}

/* ── Derivative forms (Feature 3) ── */
.derivative-grid {
  display:               grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap:                   8px;
}
.derivative-card {
  display:        flex;
  flex-direction: column;
  gap:            4px;
  padding:        8px 10px;
  border-radius:  var(--radius-md);
  background:     rgba(255,255,255,0.03);
  border:         1px solid var(--clr-border);
}
.derivative-tag {
  font-size:      9px;
  font-weight:    700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color:          var(--clr-accent-from);
}
.derivative-word {
  font-size:   13px;
  font-weight: 500;
  color:       var(--clr-text);
  font-style:  italic;
}

/* ── Drawer audio controls (Feature 4) ── */
.drawer-audio-row {
  display:        flex;
  flex-direction: column;
  gap:            10px;
  margin-top:     auto;
  padding-top:    8px;
  border-top:     1px solid var(--clr-border);
}
.pronounce-drawer-btn {
  width:         100%;
  padding:       12px;
  font-size:     14px;
  font-weight:   700;
  border-radius: var(--radius-md);
}
.drawer-audio-opts {
  display: flex;
  gap:     8px;
}
.drawer-audio-select {
  flex:          1;
  padding:       6px 8px;
  font-size:     12px;
  background:    var(--clr-surface);
  border:        1px solid var(--clr-border);
  border-radius: var(--radius-sm);
  color:         var(--clr-text);
  cursor:        pointer;
  transition:    border-color 0.15s;
}
.drawer-audio-select:hover,
.drawer-audio-select:focus {
  border-color: var(--clr-accent-from);
  outline:      none;
}

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
