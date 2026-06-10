<template>
  <div class="user-selector">
    <label for="user-search" class="selector-label">
      <span class="label-icon">👤</span>
      Learner Profile
    </label>

    <!-- Search input -->
    <div class="input-wrapper" :class="{ open: isOpen }" ref="wrapperRef">
      <input
        id="user-search"
        ref="inputRef"
        v-model="searchQuery"
        type="text"
        class="search-input"
        placeholder="Search users…"
        autocomplete="off"
        @focus="openDropdown"
        @click="onClick"
        @blur="onBlur"
        @keydown.escape="closeDropdown"
        @keydown.arrow-down.prevent="moveHighlight(1)"
        @keydown.arrow-up.prevent="moveHighlight(-1)"
        @keydown.enter.prevent="selectHighlighted"
      />
      <span class="input-caret" :class="{ rotated: isOpen }">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </span>
    </div>

    <!--
      Teleport the dropdown to <body> so the sidebar's overflow:auto
      clipping context does NOT clip it. Positioned with position:fixed
      using coordinates from wrapperRef.getBoundingClientRect().
    -->
    <Teleport to="body">
      <Transition name="dropdown">
        <div
          v-if="isOpen && filteredUsers.length"
          ref="dropdownRef"
          class="dropdown-teleported"
          role="listbox"
          :style="dropdownStyle"
        >
          <div v-if="coldStartVisible" class="section-header">
            ❄ Cold-Start Users
          </div>

          <div
            v-for="(user, idx) in filteredUsers"
            :key="user.user_id"
            class="option"
            :class="{
              'option--cold':        user.is_cold_start,
              'option--highlighted': idx === highlighted,
              'option--selected':    modelValue?.user_id === user.user_id,
            }"
            role="option"
            :aria-selected="modelValue?.user_id === user.user_id"
            @mousedown.prevent="selectUser(user)"
            @mouseover="highlighted = idx"
          >
            <div class="option-left">
              <span class="avatar">{{ user.name.charAt(0) }}</span>
              <div class="option-info">
                <span class="option-name">{{ user.name }}</span>
                <span class="option-id mono">#{{ user.user_id }}</span>
              </div>
            </div>
            <div class="option-right">
              <span v-if="user.is_cold_start" class="badge badge--cold">❄ Cold Start</span>
              <span v-else class="badge" :class="`badge--${user.cefr_level?.toLowerCase()}`">
                {{ user.cefr_level }}
              </span>
            </div>
          </div>

          <div v-if="filteredUsers.length === 0" class="option-empty">No users found</div>
        </div>
      </Transition>
    </Teleport>

    <!-- Current selection display -->
    <div v-if="modelValue" class="current-user glass fade-slide">
      <div class="current-left">
        <div class="current-avatar">{{ modelValue.name.charAt(0) }}</div>
        <div>
          <div class="current-name">{{ modelValue.name }}</div>
          <div class="current-meta mono">ID: {{ modelValue.user_id }}</div>
        </div>
      </div>
      <div class="current-right">
        <span v-if="modelValue.is_cold_start" class="badge badge--cold">❄ Cold Start</span>
        <span v-else class="badge" :class="`badge--${modelValue.cefr_level?.toLowerCase()}`">
          {{ modelValue.cefr_level }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'

const props = defineProps({
  users:      { type: Array,  default: () => [] },
  modelValue: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue'])

const searchQuery = ref('')
const isOpen      = ref(false)
const highlighted = ref(0)
const inputRef    = ref(null)
const wrapperRef  = ref(null)
const dropdownRef = ref(null)
let justFocused   = false

// ── Fixed-position style for the teleported dropdown ────────
const dropdownStyle = ref({})

function updateDropdownPosition() {
  if (!wrapperRef.value) return
  const rect = wrapperRef.value.getBoundingClientRect()
  dropdownStyle.value = {
    position: 'fixed',
    top:      `${rect.bottom + 6}px`,
    left:     `${rect.left}px`,
    width:    `${rect.width}px`,
    zIndex:   9999,
  }
}

function onClick() {
  if (justFocused) return
  if (isOpen.value) {
    closeDropdown()
  } else {
    openDropdown()
  }
}

// ── Filtered list ────────────────────────────────────────────
const filteredUsers = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (!q) return props.users
  return props.users.filter(u =>
    u.name.toLowerCase().includes(q) ||
    String(u.user_id).includes(q) ||
    (u.cefr_level || '').toLowerCase().includes(q)
  )
})

const coldStartVisible = computed(() =>
  filteredUsers.value.some(u => u.is_cold_start)
)

// ── Open / close ─────────────────────────────────────────────
function onScrollClose(e) {
  // Ignore scrolls that happen inside the dropdown list itself
  if (dropdownRef.value && dropdownRef.value.contains(e.target)) return
  closeDropdown()
}

function openDropdown() {
  updateDropdownPosition()
  isOpen.value = true
  justFocused = true
  setTimeout(() => { justFocused = false }, 200)
  // Close dropdown on external scroll (prevents misaligned fixed position)
  window.addEventListener('scroll', onScrollClose, true)
  window.addEventListener('resize', closeDropdown)
}

function closeDropdown() {
  isOpen.value = false
  window.removeEventListener('scroll', onScrollClose, true)
  window.removeEventListener('resize', closeDropdown)
}

function selectUser(user) {
  emit('update:modelValue', user)
  searchQuery.value = ''
  closeDropdown()
}

// Delay so @mousedown.prevent on options fires before blur closes
function onBlur() {
  setTimeout(() => closeDropdown(), 160)
}

function moveHighlight(dir) {
  highlighted.value = Math.max(0,
    Math.min(filteredUsers.value.length - 1, highlighted.value + dir)
  )
}

function selectHighlighted() {
  const u = filteredUsers.value[highlighted.value]
  if (u) selectUser(u)
}

onUnmounted(() => {
  window.removeEventListener('scroll', onScrollClose, true)
  window.removeEventListener('resize', closeDropdown)
})
</script>

<style scoped>
.user-selector { position: relative; }

.selector-label {
  display:     flex;
  align-items: center;
  gap:         6px;
  font-size:   11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color:       var(--clr-text-muted);
  margin-bottom: 10px;
}
.label-icon { font-size: 14px; }

.input-wrapper {
  position:    relative;
  display:     flex;
  align-items: center;
}
.search-input {
  width:        100%;
  padding:      11px 40px 11px 14px;
  background:   var(--clr-surface);
  border:       1px solid var(--clr-border);
  border-radius: var(--radius-md);
  color:        var(--clr-text);
  font-family:  inherit;
  font-size:    14px;
  transition:   border-color 0.2s, box-shadow 0.2s;
  outline:      none;
}
.search-input:focus,
.input-wrapper.open .search-input {
  border-color: var(--clr-accent);
  box-shadow:   0 0 0 3px rgba(99,102,241,0.15);
}
.search-input::placeholder { color: var(--clr-text-muted); }

.input-caret {
  position:   absolute;
  right:      12px;
  color:      var(--clr-text-muted);
  transition: transform 0.2s;
  pointer-events: none;
}
.input-caret.rotated { transform: rotate(180deg); }

/* Current user card */
.current-user {
  display:       flex;
  align-items:   center;
  justify-content: space-between;
  padding:       14px 16px;
  margin-top:    12px;
}
.current-left  { display: flex; align-items: center; gap: 12px; }
.current-avatar {
  width:           40px; height: 40px;
  border-radius:   50%;
  background:      linear-gradient(135deg, var(--clr-accent-from), var(--clr-accent-to));
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       16px;
  font-weight:     700;
  color:           #fff;
  flex-shrink:     0;
}
.current-name { font-size: 14px; font-weight: 600; }
.current-meta { font-size: 11px; color: var(--clr-text-muted); margin-top: 2px; }

.badge {
  font-size:    10px;
  font-weight:  700;
  letter-spacing: 0.06em;
  padding:      3px 8px;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
}
.badge--cold { background: rgba(6,182,212,0.15); color: var(--clr-accent2); border: 1px solid rgba(6,182,212,0.3); }
.badge--a1   { background: rgba(34,197,94,0.15);  color: var(--cefr-a1); border: 1px solid rgba(34,197,94,0.3); }
.badge--a2   { background: rgba(134,239,172,0.12);color: var(--cefr-a2); border: 1px solid rgba(134,239,172,0.3); }
.badge--b1   { background: rgba(250,204,21,0.12); color: var(--cefr-b1); border: 1px solid rgba(250,204,21,0.3); }
.badge--b2   { background: rgba(249,115,22,0.12); color: var(--cefr-b2); border: 1px solid rgba(249,115,22,0.3); }
.badge--c1   { background: rgba(248,113,113,0.12);color: var(--cefr-c1); border: 1px solid rgba(248,113,113,0.3); }
.badge--c2   { background: rgba(239,68,68,0.12);  color: var(--cefr-c2); border: 1px solid rgba(239,68,68,0.3); }

/* Dropdown transition (applied via Teleport – needs global) */
.dropdown-enter-active, .dropdown-leave-active { transition: all 0.18s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-6px); }
</style>

<!-- Global styles for the teleported dropdown (cannot be scoped) -->
<style>
.dropdown-teleported {
  max-height:    260px;
  overflow-y:    auto;
  background:    #131929;
  border:        1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  box-shadow:    0 16px 48px rgba(0,0,0,0.72), 0 0 0 1px rgba(99,102,241,0.12);
  padding:       4px;
  /* Scrollbar */
  scrollbar-width: thin;
  scrollbar-color: #6366f1 #0d1120;
}
.dropdown-teleported::-webkit-scrollbar       { width: 5px; }
.dropdown-teleported::-webkit-scrollbar-track { background: #0d1120; }
.dropdown-teleported::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 999px; }

.dropdown-teleported .section-header {
  font-size:   10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color:       #64748b;
  padding:     8px 12px 4px;
}

.dropdown-teleported .option {
  display:       flex;
  align-items:   center;
  justify-content: space-between;
  padding:       9px 12px;
  border-radius: 6px;
  cursor:        pointer;
  transition:    background 0.15s;
}
.dropdown-teleported .option--highlighted,
.dropdown-teleported .option:hover     { background: rgba(255,255,255,0.07); }
.dropdown-teleported .option--selected { background: rgba(99,102,241,0.12); }

.dropdown-teleported .option-left {
  display:     flex;
  align-items: center;
  gap:         10px;
}
.dropdown-teleported .avatar {
  width:  30px; height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.dropdown-teleported .option-info { display: flex; flex-direction: column; }
.dropdown-teleported .option-name { font-size: 13px; font-weight: 500; color: #e2e8f0; }
.dropdown-teleported .option-id   { font-size: 10px; color: #64748b; font-family: 'JetBrains Mono', monospace; }
.dropdown-teleported .option-empty { padding: 16px; text-align: center; color: #64748b; font-size: 13px; }

.dropdown-teleported .badge {
  font-size: 10px; font-weight: 700; letter-spacing: 0.06em;
  padding: 3px 8px; border-radius: 6px; text-transform: uppercase;
}
.dropdown-teleported .badge--cold { background: rgba(6,182,212,0.15);   color: #06b6d4; border: 1px solid rgba(6,182,212,0.3); }
.dropdown-teleported .badge--a1   { background: rgba(34,197,94,0.15);   color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.dropdown-teleported .badge--a2   { background: rgba(134,239,172,0.12); color: #86efac; border: 1px solid rgba(134,239,172,0.3); }
.dropdown-teleported .badge--b1   { background: rgba(250,204,21,0.12);  color: #facc15; border: 1px solid rgba(250,204,21,0.3); }
.dropdown-teleported .badge--b2   { background: rgba(249,115,22,0.12);  color: #f97316; border: 1px solid rgba(249,115,22,0.3); }
.dropdown-teleported .badge--c1   { background: rgba(248,113,113,0.12); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }
.dropdown-teleported .badge--c2   { background: rgba(239,68,68,0.12);   color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
</style>
