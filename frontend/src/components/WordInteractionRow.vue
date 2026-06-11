<template>
  <tr
    class="word-row"
    :class="{ 'word-row--interacted': interacted }"
    :id="`word-row-${word.word_id}`"
  >
    <!-- ── Rank ─────────────────────────────────────── -->
    <td class="td-rank">
      <span class="rank-badge">#{{ rank }}</span>
    </td>

    <!-- ── Word / Flashcard + Audio Controls ─────────── -->
    <td class="td-word">
      <div class="word-cell-content">

        <!-- 3D Flashcard (Feature 2) -->
        <div
          class="flashcard-scene"
          :class="{ 'flashcard-scene--flipped': isFlipped }"
          @click="isFlipped = !isFlipped"
          :title="isFlipped ? 'Click to flip back' : 'Click to test active recall'"
        >
          <div class="flashcard" :class="{ flipped: isFlipped }">
            <span class="flashcard-face flashcard-front">{{ word.word }}</span>
            <span class="flashcard-face flashcard-back">{{ wordMeaning }}</span>
          </div>
          <span class="flip-hint" aria-hidden="true">🔄</span>
        </div>

        <!-- ℹ Info badge → opens details drawer (Feature 3) -->
        <button
          class="info-badge-btn"
          @click.stop="$emit('word-click', word)"
          title="View full word details panel"
          aria-label="Open word details"
        >ℹ</button>

        <!-- Audio Controls (Feature 4) -->
        <div class="audio-control-wrap" ref="audioWrapRef">
          <button
            class="speak-btn"
            @click.stop="pronounceWord(word.word)"
            title="Listen pronunciation"
            aria-label="Pronounce word"
          >🔊</button>
          <button
            class="gear-btn"
            @click.stop="showAudioMenu = !showAudioMenu"
            :class="{ 'gear-btn--active': showAudioMenu }"
            title="Audio settings"
            aria-label="Audio settings"
          >⚙</button>

          <Transition name="audio-menu">
            <div v-if="showAudioMenu" class="audio-menu glass" role="menu">
              <div class="audio-menu-section">
                <div class="audio-menu-label">🌐 Accent</div>
                <div class="audio-chips">
                  <button
                    class="audio-chip"
                    :class="{ 'audio-chip--active': audioLang === 'en-US' }"
                    @click.stop="audioLang = 'en-US'"
                  >🇺🇸 US</button>
                  <button
                    class="audio-chip"
                    :class="{ 'audio-chip--active': audioLang === 'en-GB' }"
                    @click.stop="audioLang = 'en-GB'"
                  >🇬🇧 UK</button>
                </div>
              </div>
              <div class="audio-menu-divider"></div>
              <div class="audio-menu-section">
                <div class="audio-menu-label">⏱ Speed</div>
                <div class="audio-chips">
                  <button
                    class="audio-chip"
                    :class="{ 'audio-chip--active': audioRate === 1.0 }"
                    @click.stop="audioRate = 1.0"
                  >1.0×</button>
                  <button
                    class="audio-chip"
                    :class="{ 'audio-chip--active': audioRate === 0.75 }"
                    @click.stop="audioRate = 0.75"
                  >0.75×</button>
                </div>
              </div>
              <div class="audio-play-row">
                <button class="audio-play-btn" @click.stop="pronounceWord(word.word)">
                  ▶ Play with Settings
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </td>

    <!-- ── CEFR Difficulty ─────────────────────────────── -->
    <td class="td-cefr">
      <span class="cefr-badge" :class="`cefr--${word.cefr_difficulty.toLowerCase()}`">
        {{ word.cefr_difficulty }}
      </span>
    </td>

    <!-- ── Part of Speech ─────────────────────────────── -->
    <td class="td-pos">
      <span class="pos-chip">{{ word.part_of_speech }}</span>
    </td>

    <!-- ── Score + XAI Tooltip (Feature 1) ──────────────── -->
    <td class="td-score">
      <div class="score-xai-wrap">
        <div class="score-wrapper">
          <div class="score-bar-track">
            <div class="score-bar-fill" :style="{ width: scoreBarWidth }"></div>
          </div>
          <span class="score-value mono">{{ word.score?.toFixed(3) }}</span>
        </div>

        <!-- XAI Glassmorphism Tooltip -->
        <div class="xai-tooltip" role="tooltip" aria-label="Score composition breakdown">
          <div class="xai-title">⚡ Hybrid Score Breakdown</div>
          <div class="xai-row">
            <span class="xai-label">📖 Content Match &amp; ZPD Boost</span>
            <div class="xai-bar-wrap">
              <div class="xai-bar xai-bar--content" style="width:40%"></div>
            </div>
            <span class="xai-pct">40%</span>
          </div>
          <div class="xai-row">
            <span class="xai-label">👥 Peer Trend (SVD)</span>
            <div class="xai-bar-wrap">
              <div class="xai-bar xai-bar--svd" style="width:35%"></div>
            </div>
            <span class="xai-pct">35%</span>
          </div>
          <div class="xai-row">
            <span class="xai-label">🧠 Neural Reconstruction (AE)</span>
            <div class="xai-bar-wrap">
              <div class="xai-bar xai-bar--ae" style="width:25%"></div>
            </div>
            <span class="xai-pct">25%</span>
          </div>
        </div>
      </div>
    </td>

    <!-- ── Actions (Feature 5: Confetti anchor) ───────── -->
    <td class="td-actions">
      <div class="action-group">
        <div class="confetti-anchor" ref="confettiAnchorRef">
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
        </div>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  word:   { type: Object,  required: true },
  rank:   { type: Number,  default: 1 },
  userId: { type: Number,  required: true },
})
const emit = defineEmits(['interacted', 'word-click', 'mastered'])

// ── Feature 2: 3D Flashcard Flip ───────────────────────────────────────────
const isFlipped = ref(false)

/** Local recall synonyms / meanings for active retrieval testing */
const wordMeaningsMap = {
  'substantial':   'Considerable / Significant',
  'alleviate':     'Ease / Relieve pain',
  'paradox':       'Contradiction / Puzzle',
  'intricate':     'Complex / Elaborate',
  'obfuscate':     'Obscure / Confuse',
  'epistemology':  'Theory of Knowledge',
  'solipsism':     'Only Self Exists (theory)',
  'ubiquitous':    'Everywhere / Omnipresent',
  'ephemeral':     'Fleeting / Short-lived',
  'eloquent':      'Fluent / Expressive',
  'ambiguous':     'Unclear / Having many meanings',
  'benevolent':    'Kind / Generous',
  'subsequently':  'Afterwards / Later on',
  'analyse':       'Examine / Evaluate',
  'complex':       'Complicated / Intricate',
  'concept':       'Idea / Notion',
  'conclude':      'Determine / Deduce',
  'conduct':       'Carry out / Perform',
  'confirm':       'Verify / Validate',
  'consequence':   'Result / Outcome',
  'construct':     'Build / Assemble',
  'contribute':    'Add to / Donate',
  'crucial':       'Vital / Essential',
  'derive':        'Obtain / Extract',
  'despite':       'In spite of / Regardless',
  'distinct':      'Different / Separate',
  'diverse':       'Varied / Mixed',
  'dominant':      'Prevailing / Leading',
  'effective':     'Successful / Efficient',
  'enable':        'Allow / Facilitate',
  'evident':       'Obvious / Clear',
  'evolve':        'Develop / Change gradually',
  'examine':       'Inspect / Analyse',
  'factor':        'Element / Aspect',
  'flexible':      'Adaptable / Versatile',
  'fundamental':   'Basic / Core',
  'generate':      'Produce / Create',
  'hypothesis':    'Theory / Assumption',
  'impact':        'Effect / Influence',
  'imply':         'Suggest / Hint at',
  'inherent':      'Built-in / Innate',
  'initiative':    'Drive / Plan of action',
  'insight':       'Understanding / Perception',
  'integrate':     'Combine / Incorporate',
  'intense':       'Strong / Extreme',
  'interpret':     'Explain / Understand',
  'investigate':   'Examine / Explore',
  'justify':       'Defend / Validate',
  'maintain':      'Keep / Preserve',
  'mitigate':      'Lessen / Reduce severity',
  'modify':        'Alter / Adjust',
  'objective':     'Goal / Aim',
  'obtain':        'Get / Acquire',
  'obvious':       'Clear / Evident',
  'participate':   'Take part / Engage',
  'perceive':      'Observe / Sense',
  'persistent':    'Consistent / Enduring',
  'potential':     'Possible / Promising',
  'precise':       'Exact / Accurate',
  'primary':       'Main / Principal',
  'principle':     'Rule / Foundation',
  'propose':       'Suggest / Recommend',
  'relevant':      'Related / Applicable',
  'rely':          'Depend on / Trust',
  'represent':     'Stand for / Symbolise',
  'resolve':       'Solve / Settle',
  'restrict':      'Limit / Confine',
  'retain':        'Keep / Maintain',
  'significant':   'Important / Notable',
  'similar':       'Alike / Comparable',
  'specific':      'Particular / Exact',
  'strategy':      'Plan / Approach',
  'structure':     'Framework / Organisation',
  'sustain':       'Maintain / Support',
  'theory':        'Hypothesis / Principle',
  'transform':     'Change / Convert',
  'undermine':     'Weaken / Erode',
  'vary':          'Differ / Change',
  'valid':         'Sound / Justified',
  // ── C1 ──────────────────────────────────────────────────
  'abstain':       'Refrain / Hold back',
  'accentuate':    'Emphasise / Highlight',
  'adhere':        'Follow / Stick to',
  'advocate':      'Support / Champion',
  'alleviate':     'Ease / Relieve',
  'ambiguous':     'Unclear / Open to interpretation',
  'ameliorate':    'Improve / Make better',
  'analogous':     'Similar / Comparable',
  'articulate':    'Express clearly / Well-spoken',
  'aspire':        'Aim for / Strive toward',
  'benevolent':    'Kind / Generous',
  'bolster':       'Strengthen / Support',
  'candid':        'Honest / Frank',
  'catalyst':      'Trigger / Driving force',
  'circumvent':    'Bypass / Avoid',
  'coalesce':      'Merge / Come together',
  'coherent':      'Logical / Consistent',
  'collaborate':   'Work together / Partner',
  'commence':      'Begin / Start',
  'comprehensive': 'Thorough / Complete',
  'consensus':     'Agreement / Shared view',
  'consolidate':   'Strengthen / Combine',
  'contemplate':   'Think deeply / Consider',
  'contentious':   'Controversial / Debatable',
  'contradict':    'Oppose / Counter',
  'conventional':  'Traditional / Standard',
  'conviction':    'Strong belief / Certainty',
  'correlate':     'Connect / Relate',
  'critique':      'Analyse critically / Assess',
  'cultivate':     'Develop / Foster',
  'cynical':       'Sceptical / Distrustful',
  'deliberate':    'Intentional / Thoughtful',
  'detrimental':   'Harmful / Damaging',
  'diligent':      'Hardworking / Careful',
  'discrepancy':   'Difference / Inconsistency',
  'eloquent':      'Fluent / Expressive',
  'empirical':     'Evidence-based / Observed',
  'encompass':     'Include / Cover',
  'enhance':       'Improve / Strengthen',
  'equivocal':     'Ambiguous / Uncertain',
  'exacerbate':    'Worsen / Aggravate',
  'facilitate':    'Make easier / Enable',
  'fervent':       'Passionate / Intense',
  'fluctuate':     'Vary / Rise and fall',
  'formidable':    'Impressive / Intimidating',
  'gregarious':    'Sociable / Outgoing',
  'hackneyed':     'Overused / Clichéd',
  'hierarchy':     'Ranking / Chain of authority',
  'immutable':     'Unchangeable / Fixed',
  // ── C2 ──────────────────────────────────────────────────
  'abstruse':      'Difficult to understand / Obscure',
  'acrimonious':   'Bitter / Hostile',
  'autodidact':    'Self-taught person',
  'byzantine':     'Overly complicated / Labyrinthine',
  'cogent':        'Convincing / Logical',
  'determinism':   'All events causally fixed',
  'dichotomy':     'Division into two opposites',
  'didactic':      'Educational / Instructive',
  'disingenuous':  'Insincere / Deceptive',
  'ephemeral':     'Fleeting / Short-lived',
  'epistemology':  'Theory of Knowledge',
  'equanimity':    'Calmness / Composure',
  'esoteric':      'Known to few / Obscure',
  'hegemony':      'Dominance / Leadership',
  'impugn':        'Dispute / Challenge',
  'ineffable':     'Too great for words',
  'juxtapose':     'Place side by side',
  'laconic':       'Brief / Using few words',
  'loquacious':    'Talkative / Chatty',
  'magnanimous':   'Generous / Noble',
  'mendacious':    'Dishonest / Lying',
  'mercurial':     'Volatile / Unpredictable',
  'obfuscate':     'Obscure / Confuse',
  'obsequious':    'Fawning / Overly compliant',
  'omniscient':    'All-knowing / Omniscient',
  'ostentatious':  'Showy / Flashy',
  'pernicious':    'Harmful / Destructive',
  'perfidiously':  'Treacherously / Deceitfully',
  'perspicacious': 'Perceptive / Shrewd',
  'plethora':      'Excess / Abundance',
  'precipitate':   'Cause suddenly / Rash',
  'prevaricate':   'Avoid the truth / Equivocate',
  'propitious':    'Favourable / Auspicious',
  'recalcitrant':  'Stubborn / Defiant',
  'sagacious':     'Wise / Perceptive',
  'sanguine':      'Optimistic / Cheerful',
  'solipsism':     'Only Self Exists (theory)',
  'specious':      'Misleadingly plausible / False',
  'superfluous':   'Unnecessary / Redundant',
  'sycophant':     'Flatterer / Yes-man',
  'tautology':     'Needless repetition',
  'tendentious':   'Biased / Promoting a cause',
  'truculent':     'Aggressive / Defiant',
  'ubiquity':      'State of being everywhere',
  'vacuous':       'Empty / Lacking substance',
  'veracious':     'Truthful / Accurate',
  'vicarious':     'Experienced through others',
  'zealous':       'Enthusiastic / Devoted',
}

/** POS-based synonym fallback — never shows the useless "POS · CEFR level" string */
function deriveBackFace(word, pos) {
  const w = (word || '').toLowerCase()
  if (pos === 'Verb') {
    const stem = w.endsWith('e') ? w.slice(0, -1) : w
    return `${stem}ing / ${stem}ed`
  }
  if (pos === 'Noun') {
    if (w.endsWith('tion') || w.endsWith('sion')) return `${w.slice(0, -4)}e / ${w.slice(0, -4)}al`
    if (w.endsWith('ness'))  return `${w.slice(0, -4)} / ${w.slice(0, -4)}ly`
    if (w.endsWith('ment'))  return `${w.slice(0, -4)}ing / ${w.slice(0, -4)}ed`
    if (w.endsWith('ity'))   return `${w.slice(0, -3)}ous / ${w.slice(0, -3)}ously`
    return `${word}s / related to ${word}`
  }
  if (pos === 'Adjective') {
    if (w.endsWith('ous'))   return `${w.slice(0, -3)}e / characterised by ${w}`
    if (w.endsWith('ive'))   return `${w.slice(0, -3)}ion / having that quality`
    if (w.endsWith('ful'))   return `${w.slice(0, -3)} / full of that quality`
    if (w.endsWith('less'))  return `without ${w.slice(0, -4)} / lacking`
    if (w.endsWith('al'))    return `${w.slice(0, -2)} / relating to ${w}`
    return `${word}ly / showing ${word} quality`
  }
  if (pos === 'Adverb') {
    const base = w.endsWith('ly') ? w.slice(0, -2) : w
    return `${base} / in a ${base} way`
  }
  return `synonym of ${word}`
}

const wordMeaning = computed(() => {
  const key = (props.word.word ?? '').toLowerCase()
  return (
    wordMeaningsMap[key] ||
    deriveBackFace(props.word.word, props.word.part_of_speech)
  )
})

// ── Feature 4: Audio Settings ──────────────────────────────────────────────
const audioLang     = ref('en-US')
const audioRate     = ref(1.0)
const showAudioMenu = ref(false)
const audioWrapRef  = ref(null)

function pronounceWord(text) {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const utter = new SpeechSynthesisUtterance(text)
  utter.lang = audioLang.value
  utter.rate = audioRate.value

  // Try to match a voice for the selected accent
  const voices = window.speechSynthesis.getVoices()
  const match = voices.find(v => v.lang.startsWith(audioLang.value.slice(0, 5)))
  if (match) utter.voice = match

  window.speechSynthesis.speak(utter)
  showAudioMenu.value = false
}

/** Close audio menu when clicking outside */
function onDocumentClick(e) {
  if (audioWrapRef.value && !audioWrapRef.value.contains(e.target)) {
    showAudioMenu.value = false
  }
}
onMounted(()    => document.addEventListener('click', onDocumentClick, true))
onUnmounted(()  => document.removeEventListener('click', onDocumentClick, true))

// ── Score bar ──────────────────────────────────────────────────────────────
const scoreBarWidth = computed(() => {
  const s = props.word.score ?? 0
  // Normalise: cosine sim ≤ 1, or 1-5 rating scale
  const normalised = s <= 1 ? s : (s - 1) / 4
  return Math.max(4, Math.min(100, normalised * 100)) + '%'
})

// ── Feature 5: Confetti Burst ──────────────────────────────────────────────
const isSubmitting      = ref(false)
const interacted        = ref(false)
const lastAction        = ref('')
const confettiAnchorRef = ref(null)

const CONFETTI_COLORS = [
  '#6366f1','#8b5cf6','#a855f7','#ec4899',
  '#f59e0b','#10b981','#06b6d4','#f97316',
]

function launchConfetti() {
  const anchor = confettiAnchorRef.value
  if (!anchor) return
  const rect = anchor.getBoundingClientRect()
  const cx = rect.left + rect.width  / 2
  const cy = rect.top  + rect.height / 2

  for (let i = 0; i < 24; i++) {
    const el    = document.createElement('span')
    el.className = 'confetti-particle'

    const angle = (Math.PI * 2 / 24) * i + (Math.random() - 0.5) * 0.5
    const dist  = 50 + Math.random() * 70
    const dx    = Math.cos(angle) * dist
    const dy    = Math.sin(angle) * dist - 40   // bias upward
    const color = CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)]
    const size  = 5 + Math.random() * 7
    const br    = Math.random() > 0.5 ? '50%' : '2px'
    const delay = Math.random() * 60

    el.style.cssText = `
      position:fixed; left:${cx}px; top:${cy}px;
      width:${size}px; height:${size}px;
      background:${color}; border-radius:${br};
      pointer-events:none; z-index:9999;
      --dx:${dx}px; --dy:${dy}px;
      animation: confettiBurst 0.9s ${delay}ms cubic-bezier(.25,.46,.45,.94) forwards;
    `
    document.body.appendChild(el)
    setTimeout(() => el.remove(), 1100 + delay)
  }
}

// ── Core interaction handler ───────────────────────────────────────────────
async function interact(rating) {
  if (isSubmitting.value || interacted.value) return
  lastAction.value   = rating === 5 ? 'mastered' : 'study'
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

    if (rating === 5) {
      launchConfetti()
      emit('mastered', { word: props.word })
    }

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

<!-- ═══════════════════════════════════════════════════════ Scoped Styles ═══ -->
<style scoped>
/* ── Row base ── */
.word-row {
  transition: background 0.2s;
  animation: fadeSlideIn 0.25s ease forwards;
}
.word-row:hover td { background: rgba(255,255,255,0.025); }
.word-row--interacted { opacity: 0.38; }

td {
  padding:        12px 10px;
  border-bottom:  1px solid var(--clr-border);
  vertical-align: middle;
}

/* ── Rank ── */
.td-rank { width: 48px; text-align: center; }
.rank-badge {
  display:         inline-flex;
  align-items:     center;
  justify-content: center;
  width:           28px; height: 28px;
  border-radius:   50%;
  background:      var(--clr-surface-hov);
  border:          1px solid var(--clr-border);
  font-size:       11px;
  font-weight:     700;
  color:           var(--clr-text-muted);
}

/* ── Word cell ── */
.td-word { min-width: 210px; }
.word-cell-content {
  display:     flex;
  align-items: center;
  gap:         7px;
  flex-wrap:   nowrap;
}

/* ════ Feature 2 — 3D Flashcard ════ */
.flashcard-scene {
  perspective:   700px;
  cursor:        pointer;
  position:      relative;
  display:       inline-flex;
  align-items:   center;
  gap:           4px;
  user-select:   none;
}
.flashcard {
  display:          grid;
  grid-template-areas: "face";
  transform-style:  preserve-3d;
  transition:       transform 0.55s cubic-bezier(0.4, 0, 0.2, 1);
}
.flashcard.flipped { transform: rotateY(180deg); }

.flashcard-face {
  grid-area:          face;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  font-size:          14px;
  font-weight:        600;
  color:              var(--clr-text);
  white-space:        nowrap;
  line-height:        1.3;
}
.flashcard-front {
  border-bottom: 1px dashed rgba(255,255,255,0.2);
  transition:    color 0.2s;
}
.flashcard-scene:hover .flashcard-front {
  color: var(--clr-accent-from);
  border-bottom-color: var(--clr-accent-from);
}
.flashcard-back {
  transform:       rotateY(180deg);
  color:           #a78bfa;
  font-size:       12px;
  font-style:      italic;
  font-weight:     500;
  padding:         1px 6px;
  background:      rgba(99,102,241,0.1);
  border-radius:   4px;
  border:          1px solid rgba(99,102,241,0.25);
  white-space:     nowrap;
}

.flip-hint {
  font-size:   10px;
  opacity:     0;
  transition:  opacity 0.2s;
  margin-left: 2px;
  flex-shrink: 0;
}
.flashcard-scene:hover .flip-hint { opacity: 0.5; }
.flashcard-scene--flipped .flip-hint { opacity: 0; }

/* ── Info badge ── */
.info-badge-btn {
  display:         inline-flex;
  align-items:     center;
  justify-content: center;
  width:           18px; height: 18px;
  border-radius:   50%;
  background:      rgba(99,102,241,0.08);
  border:          1px solid rgba(99,102,241,0.2);
  color:           var(--clr-accent-from);
  font-size:       10px;
  font-weight:     700;
  cursor:          pointer;
  transition:      background 0.15s, transform 0.15s;
  flex-shrink:     0;
}
.info-badge-btn:hover {
  background:  rgba(99,102,241,0.22);
  transform:   scale(1.15);
}

/* ════ Feature 4 — Audio Controls ════ */
.audio-control-wrap {
  position:    relative;
  display:     flex;
  align-items: center;
  gap:         2px;
  flex-shrink: 0;
}

.speak-btn {
  background:  none;
  border:      none;
  cursor:      pointer;
  font-size:   13px;
  opacity:     0.5;
  transition:  opacity 0.2s, transform 0.2s;
  padding:     2px 3px;
  line-height: 1;
}
.speak-btn:hover { opacity: 1; transform: scale(1.15); }

.gear-btn {
  background:  none;
  border:      none;
  cursor:      pointer;
  font-size:   11px;
  opacity:     0.35;
  transition:  opacity 0.2s, transform 0.3s;
  padding:     2px 3px;
  line-height: 1;
}
.gear-btn:hover        { opacity: 0.8; transform: rotate(30deg); }
.gear-btn--active      { opacity: 0.9; transform: rotate(45deg); }

/* Audio settings menu */
.audio-menu {
  position:      absolute;
  top:           calc(100% + 8px);
  left:          50%;
  transform:     translateX(-50%);
  z-index:       500;
  min-width:     175px;
  padding:       12px;
  border-radius: 12px;
  background:    rgba(15, 20, 40, 0.92);
  border:        1px solid rgba(99,102,241,0.25);
  box-shadow:    0 16px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(99,102,241,0.1);
  backdrop-filter: blur(18px);
  display:       flex;
  flex-direction: column;
  gap:           8px;
}
.audio-menu-section { display: flex; flex-direction: column; gap: 6px; }
.audio-menu-label {
  font-size:      9px;
  font-weight:    700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color:          var(--clr-text-muted);
}
.audio-chips { display: flex; gap: 5px; }
.audio-chip {
  flex:            1;
  padding:         5px 8px;
  font-size:       11px;
  font-weight:     600;
  border-radius:   6px;
  background:      rgba(255,255,255,0.04);
  border:          1px solid var(--clr-border);
  color:           var(--clr-text-muted);
  cursor:          pointer;
  transition:      all 0.15s;
  white-space:     nowrap;
  text-align:      center;
}
.audio-chip:hover         { background: rgba(99,102,241,0.12); border-color: rgba(99,102,241,0.3); color: var(--clr-text); }
.audio-chip--active       { background: rgba(99,102,241,0.2);  border-color: rgba(99,102,241,0.5); color: #a5b4fc; }

.audio-menu-divider {
  height:     1px;
  background: var(--clr-border);
  margin:     2px 0;
}

.audio-play-row { margin-top: 2px; }
.audio-play-btn {
  width:         100%;
  padding:       7px;
  font-size:     11px;
  font-weight:   600;
  border-radius: 6px;
  background:    linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.25));
  border:        1px solid rgba(99,102,241,0.35);
  color:         #a5b4fc;
  cursor:        pointer;
  transition:    all 0.15s;
}
.audio-play-btn:hover {
  background: linear-gradient(135deg, rgba(99,102,241,0.4), rgba(139,92,246,0.4));
  color:      #fff;
}

/* Audio menu Transition */
.audio-menu-enter-active,
.audio-menu-leave-active  { transition: opacity 0.18s ease, transform 0.18s ease; }
.audio-menu-enter-from,
.audio-menu-leave-to      { opacity: 0; transform: translateX(-50%) translateY(-6px); }

/* ── CEFR badge ── */
.td-cefr { width: 70px; text-align: center; }
.cefr-badge {
  display:        inline-block;
  font-size:      10px;
  font-weight:    800;
  letter-spacing: 0.07em;
  padding:        3px 8px;
  border-radius:  var(--radius-sm);
  text-transform: uppercase;
}
.cefr--a1 { background: rgba(34,197,94,0.15);   color: var(--cefr-a1); border: 1px solid rgba(34,197,94,0.3); }
.cefr--a2 { background: rgba(134,239,172,0.12); color: var(--cefr-a2); border: 1px solid rgba(134,239,172,0.3); }
.cefr--b1 { background: rgba(250,204,21,0.12);  color: var(--cefr-b1); border: 1px solid rgba(250,204,21,0.3); }
.cefr--b2 { background: rgba(249,115,22,0.12);  color: var(--cefr-b2); border: 1px solid rgba(249,115,22,0.3); }
.cefr--c1 { background: rgba(248,113,113,0.12); color: var(--cefr-c1); border: 1px solid rgba(248,113,113,0.3); }
.cefr--c2 { background: rgba(239,68,68,0.12);   color: var(--cefr-c2); border: 1px solid rgba(239,68,68,0.3); }

/* ── POS chip ── */
.td-pos { width: 100px; }
.pos-chip {
  display:        inline-block;
  font-size:      11px;
  font-weight:    500;
  padding:        3px 8px;
  border-radius:  var(--radius-sm);
  background:     rgba(99,102,241,0.1);
  color:          var(--clr-accent-from);
  border:         1px solid rgba(99,102,241,0.2);
}

/* ════ Feature 1 — XAI Score Tooltip ════ */
.td-score { min-width: 150px; overflow: visible; }

.score-xai-wrap {
  position: relative;
  display:  inline-block;
  width:    100%;
}

.score-wrapper {
  display:     flex;
  align-items: center;
  gap:         10px;
  cursor:      help;
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
  font-size:   11px;
  color:       var(--clr-text-muted);
  flex-shrink: 0;
  min-width:   44px;
  text-align:  right;
}

/* XAI Tooltip */
.xai-tooltip {
  position:       absolute;
  bottom:         calc(100% + 10px);
  left:           50%;
  transform:      translateX(-50%) translateY(4px);
  z-index:        600;
  min-width:      230px;
  padding:        12px 14px;
  border-radius:  12px;
  background:     rgba(10, 14, 30, 0.9);
  border:         1px solid rgba(99,102,241,0.3);
  box-shadow:     0 16px 48px rgba(0,0,0,0.75), 0 0 0 1px rgba(99,102,241,0.08);
  backdrop-filter: blur(20px);
  pointer-events: none;
  /* Hidden by default */
  opacity:        0;
  transition:     opacity 0.22s ease, transform 0.22s ease;
}
/* Show on hover of the wrapper */
.score-xai-wrap:hover .xai-tooltip {
  opacity:   1;
  transform: translateX(-50%) translateY(0);
}

.xai-title {
  font-size:      10px;
  font-weight:    700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color:          #a5b4fc;
  margin-bottom:  10px;
  padding-bottom: 8px;
  border-bottom:  1px solid rgba(255,255,255,0.06);
}
.xai-row {
  display:     flex;
  align-items: center;
  gap:         7px;
  margin-bottom: 7px;
}
.xai-row:last-child { margin-bottom: 0; }
.xai-label {
  font-size:   10px;
  color:       var(--clr-text-muted);
  flex:        1;
  white-space: nowrap;
  overflow:    hidden;
  text-overflow: ellipsis;
  min-width:   0;
}
.xai-bar-wrap {
  width:         60px;
  height:        4px;
  background:    rgba(255,255,255,0.06);
  border-radius: 999px;
  overflow:      hidden;
  flex-shrink:   0;
}
.xai-bar {
  height:        100%;
  border-radius: 999px;
}
.xai-bar--content { background: linear-gradient(90deg, #6366f1, #818cf8); }
.xai-bar--svd     { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.xai-bar--ae      { background: linear-gradient(90deg, #06b6d4, #22d3ee); }
.xai-pct {
  font-size:   10px;
  font-weight: 700;
  color:       #e2e8f0;
  min-width:   28px;
  text-align:  right;
  flex-shrink: 0;
}

/* ── Actions ── */
.td-actions { width: 210px; }
.action-group {
  display:     flex;
  gap:         6px;
  align-items: center;
}
.confetti-anchor { position: relative; display: inline-block; }
.action-btn { padding: 6px 11px; font-size: 12px; }
</style>

<!-- ══ Global keyframes for confetti (particles live on document.body) ══ -->
<style>
@keyframes confettiBurst {
  0%   { transform: translate(0, 0) scale(1) rotate(0deg);   opacity: 1; }
  70%  { opacity: 0.9; }
  100% { transform: translate(var(--dx), var(--dy)) scale(0.3) rotate(540deg); opacity: 0; }
}
</style>
