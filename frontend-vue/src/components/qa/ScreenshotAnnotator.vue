<template>
  <div class="seim-qa-annotator" role="dialog" aria-modal="true" :aria-label="t('qa.annotate.title')" data-testid="qa-annotator" data-qa-ignore>
    <div class="seim-qa-annotator__panel bg-body rounded shadow p-2">
      <div class="d-flex flex-wrap align-items-center gap-2 mb-2">
        <strong class="me-2">{{ t('qa.annotate.title') }}</strong>
        <div class="btn-group btn-group-sm" role="group" :aria-label="t('qa.annotate.tools')">
          <button type="button" class="btn" :class="tool === 'box' ? 'btn-danger' : 'btn-outline-danger'" data-testid="qa-annotate-box" @click="tool = 'box'">
            <i class="bi bi-square me-1" aria-hidden="true" />{{ t('qa.annotate.highlight') }}
          </button>
          <button type="button" class="btn" :class="tool === 'redact' ? 'btn-dark' : 'btn-outline-dark'" data-testid="qa-annotate-redact" @click="tool = 'redact'">
            <i class="bi bi-eraser-fill me-1" aria-hidden="true" />{{ t('qa.annotate.redact') }}
          </button>
        </div>
        <button type="button" class="btn btn-outline-secondary btn-sm" :disabled="!shapes.length" data-testid="qa-annotate-undo" @click="undo">
          <i class="bi bi-arrow-counterclockwise me-1" aria-hidden="true" />{{ t('qa.annotate.undo') }}
        </button>
        <span class="small text-muted d-none d-md-inline">{{ t('qa.annotate.hint') }}</span>
        <div class="ms-auto d-flex gap-2">
          <button type="button" class="btn btn-outline-secondary btn-sm" @click="emit('cancel')">{{ t('qa.common.cancel') }}</button>
          <button type="button" class="btn btn-primary btn-sm" data-testid="qa-annotate-apply" @click="apply">{{ t('qa.annotate.apply') }}</button>
        </div>
      </div>
      <div class="seim-qa-annotator__canvas-wrap">
        <canvas
          ref="canvas"
          class="seim-qa-annotator__canvas"
          data-testid="qa-annotate-canvas"
          @pointerdown="onDown"
          @pointermove="onMove"
          @pointerup="onUp"
          @pointerleave="onUp"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({ file: { type: Object, required: true } })
const emit = defineEmits(['apply', 'cancel'])
const { t } = useI18n()

const canvas = ref(null)
const tool = ref('box')
const shapes = ref([])
let img = null
let objectUrl = ''
let drag = null

function ctx() {
  return canvas.value?.getContext?.('2d') || null
}

function draw() {
  const c = ctx()
  if (!c || !img) return
  c.clearRect(0, 0, canvas.value.width, canvas.value.height)
  c.drawImage(img, 0, 0)
  const all = drag ? [...shapes.value, drag] : shapes.value
  const lw = Math.max(3, Math.round(canvas.value.width / 300))
  for (const s of all) {
    const x = Math.min(s.x1, s.x2)
    const y = Math.min(s.y1, s.y2)
    const w = Math.abs(s.x2 - s.x1)
    const h = Math.abs(s.y2 - s.y1)
    if (s.tool === 'redact') {
      c.fillStyle = '#000'
      c.fillRect(x, y, w, h)
    } else {
      c.strokeStyle = '#e11d48'
      c.lineWidth = lw
      c.strokeRect(x, y, w, h)
    }
  }
}

function point(e) {
  const rect = canvas.value.getBoundingClientRect()
  const sx = rect.width ? canvas.value.width / rect.width : 1
  const sy = rect.height ? canvas.value.height / rect.height : 1
  return { x: Math.round((e.clientX - rect.left) * sx), y: Math.round((e.clientY - rect.top) * sy) }
}

function onDown(e) {
  const p = point(e)
  drag = { tool: tool.value, x1: p.x, y1: p.y, x2: p.x, y2: p.y }
  canvas.value.setPointerCapture?.(e.pointerId)
}

function onMove(e) {
  if (!drag) return
  const p = point(e)
  drag.x2 = p.x
  drag.y2 = p.y
  draw()
}

function onUp() {
  if (!drag) return
  if (Math.abs(drag.x2 - drag.x1) > 3 && Math.abs(drag.y2 - drag.y1) > 3) shapes.value.push(drag)
  drag = null
  draw()
}

function undo() {
  shapes.value.pop()
  draw()
}

function apply() {
  if (!shapes.value.length) {
    emit('apply', props.file)
    return
  }
  draw()
  const name = (props.file.name || 'screenshot').replace(/\.[^.]+$/, '') + '-annotated.png'
  canvas.value.toBlob((blob) => {
    if (!blob) {
      emit('cancel')
      return
    }
    emit('apply', new File([blob], name, { type: 'image/png' }))
  }, 'image/png')
}

function onKey(e) {
  if (e.key === 'Escape') emit('cancel')
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') undo()
}

defineExpose({ shapes, apply, undo, tool })

onMounted(() => {
  window.addEventListener('keydown', onKey)
  if (typeof URL.createObjectURL !== 'function') return
  objectUrl = URL.createObjectURL(props.file)
  img = new Image()
  img.onload = () => {
    canvas.value.width = img.naturalWidth
    canvas.value.height = img.naturalHeight
    draw()
  }
  img.src = objectUrl
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  if (objectUrl) URL.revokeObjectURL(objectUrl)
})
</script>

<style scoped>
.seim-qa-annotator {
  position: fixed;
  inset: 0;
  z-index: 1095;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.seim-qa-annotator__panel {
  max-width: 100%;
  max-height: 100%;
  display: flex;
  flex-direction: column;
}
.seim-qa-annotator__canvas-wrap {
  overflow: auto;
  min-height: 0;
}
.seim-qa-annotator__canvas {
  max-width: min(1200px, 92vw);
  max-height: 78vh;
  cursor: crosshair;
  touch-action: none;
  display: block;
}
</style>
