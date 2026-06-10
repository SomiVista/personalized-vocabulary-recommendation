<template>
  <div class="algo-selector" role="tablist" aria-label="Recommendation algorithm">
    <button
      v-for="algo in algorithms"
      :key="algo.key"
      class="tab"
      :class="{ 'tab--active': modelValue === algo.key }"
      role="tab"
      :aria-selected="modelValue === algo.key"
      :id="`tab-${algo.key}`"
      @click="$emit('update:modelValue', algo.key)"
    >
      <span class="tab-icon">{{ algo.icon }}</span>
      <div class="tab-text">
        <span class="tab-name">{{ algo.name }}</span>
        <span class="tab-desc">{{ algo.short }}</span>
      </div>
    </button>

    <!-- Info tooltip for active algorithm -->
    <Transition name="info-slide">
      <div v-if="activeAlgo" class="algo-info glass" role="note">
        <div class="info-header">
          <span class="info-icon">{{ activeAlgo.icon }}</span>
          <strong>{{ activeAlgo.name }}</strong>
        </div>
        <p class="info-desc">{{ activeAlgo.description }}</p>
        <div v-if="activeAlgo.coldStart" class="info-tag info-tag--cold">
          ❄ Cold-Start Safe
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: 'hybrid' },
})
defineEmits(['update:modelValue'])

const algorithms = [
  {
    key:   'content',
    icon:  '📖',
    name:  'Content-Based',
    short: 'CEFR Cosine Sim',
    description: "Recommends words by computing cosine similarity between the user's CEFR profile vector and each word's difficulty/POS feature vector. Applies a Zone of Proximal Development boost for words one level above the user's current CEFR.",
    coldStart: true,
  },
  {
    key:   'svd',
    icon:  '🔢',
    name:  'SVD · ColFilt',
    short: 'TruncatedSVD k=20',
    description: "Collaborative Filtering using scikit-learn TruncatedSVD with 20 latent factors. Decomposes the 100x300 interaction matrix to predict preference scores for unrated words. Gracefully falls back to CBF for cold-start users.",
    coldStart: false,
  },
  {
    key:   'autoencoder',
    icon:  '🧠',
    name:  'Autoencoder',
    short: 'PyTorch 300→32→300',
    description: "Deep neural network (300 to 64 to 32 to 64 to 300) trained on masked MSE to reconstruct the user's sparse rating vector. Non-linear latent representations capture complex preference patterns. Falls back to CBF for cold-start users.",
    coldStart: false,
  },
  {
    key:   'hybrid',
    icon:  '⚡',
    name:  'Hybrid',
    short: '0.4 CBF + 0.35 SVD + 0.25 AE',
    description: "Proposed hybrid engine: uses pure CBF for cold-start users, and a weighted ensemble (40% CBF + 35% SVD + 25% Autoencoder) for active users. Combines interpretability of CBF with collaborative and deep learning power.",
    coldStart: true,
  },
]

const activeAlgo = computed(() =>
  algorithms.find(a => a.key === props.modelValue)
)
</script>

<style scoped>
.algo-selector { display: flex; flex-direction: column; gap: 6px; }

.tab {
  display:       flex;
  align-items:   center;
  gap:           12px;
  width:         100%;
  padding:       12px 14px;
  background:    var(--clr-surface);
  border:        1px solid var(--clr-border);
  border-radius: var(--radius-md);
  color:         var(--clr-text);
  font-family:   inherit;
  cursor:        pointer;
  transition:    all 0.18s ease;
  text-align:    left;
}
.tab:hover {
  background:    var(--clr-surface-hov);
  border-color:  var(--clr-border-hov);
}
.tab--active {
  background:    rgba(99, 102, 241, 0.12);
  border-color:  var(--clr-accent);
  box-shadow:    0 0 0 1px var(--clr-accent), inset 0 0 20px rgba(99,102,241,0.06);
}

.tab-icon { font-size: 20px; flex-shrink: 0; }

.tab-text {
  display:        flex;
  flex-direction: column;
  gap:            1px;
}
.tab-name {
  font-size:   13px;
  font-weight: 600;
  line-height: 1.3;
}
.tab--active .tab-name { color: var(--clr-accent-from); }

.tab-desc {
  font-size:  10px;
  color:      var(--clr-text-muted);
  font-family: 'JetBrains Mono', monospace;
}

/* Info box */
.algo-info {
  margin-top: 4px;
  padding:    14px 16px;
}
.info-header {
  display:     flex;
  align-items: center;
  gap:         8px;
  font-size:   13px;
  font-weight: 600;
  margin-bottom: 6px;
}
.info-icon   { font-size: 16px; }
.info-desc   { font-size: 12px; color: var(--clr-text-muted); line-height: 1.6; }
.info-tag    {
  display:       inline-flex;
  align-items:   center;
  gap:           4px;
  font-size:     10px;
  font-weight:   700;
  padding:       3px 8px;
  border-radius: var(--radius-sm);
  margin-top:    8px;
}
.info-tag--cold {
  background: rgba(6,182,212,0.12);
  color:      var(--clr-accent2);
  border:     1px solid rgba(6,182,212,0.25);
}

/* Transitions */
.info-slide-enter-active, .info-slide-leave-active { transition: all 0.2s ease; }
.info-slide-enter-from, .info-slide-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
