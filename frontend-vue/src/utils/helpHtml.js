const REMOVE_TAGS = new Set(['SCRIPT', 'STYLE', 'IFRAME', 'OBJECT', 'EMBED', 'LINK', 'META', 'NOSCRIPT'])

const ALLOWED_TAGS = new Set([
  'P',
  'BR',
  'UL',
  'OL',
  'LI',
  'A',
  'STRONG',
  'EM',
  'B',
  'I',
  'U',
  'H2',
  'H3',
  'H4',
  'H5',
  'H6',
  'BLOCKQUOTE',
  'CODE',
  'PRE',
  'SPAN',
  'DIV',
  'TABLE',
  'THEAD',
  'TBODY',
  'TR',
  'TH',
  'TD',
  'HR',
  'IMG',
  'FIGURE',
  'FIGCAPTION',
])

const ALLOWED_ATTRS = {
  A: new Set(['href', 'title', 'target', 'rel']),
  IMG: new Set(['src', 'alt', 'title']),
}

function isSafeUrl(value) {
  const trimmed = String(value || '').trim()
  if (!trimmed) return false
  const lower = trimmed.toLowerCase()
  if (lower.startsWith('javascript:') || lower.startsWith('data:') || lower.startsWith('vbscript:')) {
    return false
  }
  return /^(https?:|mailto:|\/|#)/i.test(trimmed)
}

function sanitizeNode(node) {
  let child = node.firstChild
  while (child) {
    const next = child.nextSibling
    if (child.nodeType === Node.TEXT_NODE) {
      child = next
      continue
    }
    if (child.nodeType !== Node.ELEMENT_NODE) {
      child.remove()
      child = next
      continue
    }
    const tag = child.tagName
    if (REMOVE_TAGS.has(tag)) {
      child.remove()
      child = next
      continue
    }
    if (!ALLOWED_TAGS.has(tag)) {
      const firstInserted = child.firstChild
      while (child.firstChild) {
        node.insertBefore(child.firstChild, child)
      }
      child.remove()
      child = firstInserted || next
      continue
    }
    const allowed = ALLOWED_ATTRS[tag] || new Set()
    for (const attr of Array.from(child.attributes)) {
      const name = attr.name.toLowerCase()
      if (name.startsWith('on') || name === 'style' || !allowed.has(name)) {
        child.removeAttribute(attr.name)
        continue
      }
      if ((tag === 'A' && name === 'href') || (tag === 'IMG' && name === 'src')) {
        if (!isSafeUrl(attr.value)) child.removeAttribute(attr.name)
      }
    }
    if (tag === 'A') {
      child.setAttribute('rel', 'noopener noreferrer')
    }
    sanitizeNode(child)
    child = next
  }
}

/**
 * Strip scripts and unsafe attributes from CMS-rendered help HTML.
 * @param {string} html
 * @returns {string}
 */
export function sanitizeHelpHtml(html) {
  if (!html || typeof html !== 'string') return ''
  if (typeof DOMParser === 'undefined') return ''
  const doc = new DOMParser().parseFromString(`<div id="seim-help-root">${html}</div>`, 'text/html')
  const root = doc.getElementById('seim-help-root')
  if (!root) return ''
  sanitizeNode(root)
  return root.innerHTML
}
