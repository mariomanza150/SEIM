/**
 * Screenshot helpers for the Report-issue widget.
 * - capturePage(): html2canvas (lazy-loaded, never in the main bundle)
 * - captureScreen(): getDisplayMedia single frame (permission prompt)
 */

function canvasToFile(canvas, name) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error('capture-failed'))
        return
      }
      resolve(new File([blob], name, { type: 'image/png' }))
    }, 'image/png')
  })
}

function stamp() {
  return new Date().toISOString().replace(/[:.]/g, '-')
}

export async function capturePage({ ignoreSelector = '[data-qa-ignore]' } = {}) {
  const { default: html2canvas } = await import('html2canvas')
  const canvas = await html2canvas(document.body, {
    logging: false,
    useCORS: true,
    scale: Math.min(window.devicePixelRatio || 1, 2),
    x: window.scrollX,
    y: window.scrollY,
    width: window.innerWidth,
    height: window.innerHeight,
    ignoreElements: (el) => Boolean(el?.matches?.(ignoreSelector)),
  })
  return canvasToFile(canvas, `page-${stamp()}.png`)
}

export function canCaptureScreen() {
  return Boolean(typeof navigator !== 'undefined' && navigator.mediaDevices?.getDisplayMedia)
}

export async function captureScreen() {
  const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false })
  try {
    const video = document.createElement('video')
    video.srcObject = stream
    video.muted = true
    await video.play()
    await new Promise((r) => setTimeout(r, 250))
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    return await canvasToFile(canvas, `screen-${stamp()}.png`)
  } finally {
    stream.getTracks().forEach((t) => t.stop())
  }
}

export function canRecordScreen() {
  return canCaptureScreen() && typeof window !== 'undefined' && typeof window.MediaRecorder !== 'undefined'
}

/**
 * Start a short screen recording. Returns { stop(): Promise<File> }.
 * Auto-stops after maxSeconds.
 */
export async function startRecording({ maxSeconds = 60 } = {}) {
  const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false })
  const mime = ['video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm'].find(
    (m) => window.MediaRecorder.isTypeSupported?.(m),
  )
  const recorder = new window.MediaRecorder(stream, mime ? { mimeType: mime, videoBitsPerSecond: 1_000_000 } : undefined)
  const chunks = []
  recorder.ondataavailable = (e) => e.data?.size && chunks.push(e.data)
  let resolveDone
  const done = new Promise((r) => (resolveDone = r))
  recorder.onstop = () => {
    stream.getTracks().forEach((t) => t.stop())
    resolveDone(new File([new Blob(chunks, { type: 'video/webm' })], `recording-${stamp()}.webm`, { type: 'video/webm' }))
  }
  stream.getVideoTracks()[0]?.addEventListener('ended', () => recorder.state !== 'inactive' && recorder.stop())
  recorder.start(1000)
  const timer = setTimeout(() => recorder.state !== 'inactive' && recorder.stop(), maxSeconds * 1000)
  return {
    stop() {
      clearTimeout(timer)
      if (recorder.state !== 'inactive') recorder.stop()
      return done
    },
    done,
  }
}
