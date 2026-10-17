/**
 * Role switcher: the tester's own tokens are stashed locally while acting as a
 * demo account (or, for admins, impersonating a user) and restored on Return.
 * The server never mints tester tokens from a demo token.
 */
import { useAuthStore } from '@/stores/auth'
import { useQaStore } from '@/stores/qa'
import { demoLogin, demoReturn, impersonate } from '@/qa/api'

export const STASH_KEY = 'seim_qa_stash'

export function readStash() {
  try {
    const raw = localStorage.getItem(STASH_KEY)
    const parsed = raw ? JSON.parse(raw) : null
    return parsed && parsed.access && parsed.refresh ? parsed : null
  } catch {
    return null
  }
}

export function clearStash() {
  localStorage.removeItem(STASH_KEY)
}

function stashCurrent(auth) {
  // Never overwrite an existing stash: switching A -> B keeps the original tester.
  if (readStash()) return
  localStorage.setItem(
    STASH_KEY,
    JSON.stringify({
      access: auth.accessToken,
      refresh: localStorage.getItem('refresh_token') || localStorage.getItem('seim_refresh_token'),
      email: auth.user?.email || '',
    }),
  )
}

async function adopt(data) {
  const auth = useAuthStore()
  const qa = useQaStore()
  await auth.adoptTokens(data.access, data.refresh)
  qa.reset()
  await qa.load(true)
}

export async function switchToDemo(userId) {
  const auth = useAuthStore()
  const { data } = await demoLogin(userId)
  stashCurrent(auth)
  await adopt(data)
  return data.acting_as
}

export async function startImpersonation(userId, reason) {
  const auth = useAuthStore()
  const { data } = await impersonate(userId, reason)
  stashCurrent(auth)
  await adopt(data)
  return data.acting_as
}

/** Return to the tester's own account. Returns false when there was nothing to restore. */
export async function returnToMyAccount() {
  const auth = useAuthStore()
  const stash = readStash()
  const currentRefresh =
    localStorage.getItem('refresh_token') || localStorage.getItem('seim_refresh_token')
  try {
    await demoReturn(currentRefresh)
  } catch {
    // Audit is best effort; still restore the tester session.
  }
  if (!stash) {
    await auth.logout()
    return false
  }
  clearStash()
  try {
    await adopt(stash)
  } catch {
    await auth.logout()
    return false
  }
  return true
}
