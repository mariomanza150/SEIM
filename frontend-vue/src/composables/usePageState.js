import { ref, shallowRef } from 'vue'
import i18n from '@/i18n'
import { getApiErrorMessage } from '@/utils/apiErrors'

/**
 * Standard async page state: loading, error, data.
 *
 * Usage in a view:
 *   const { loading, error, data, run, isEmpty } = usePageState(fetchApplications, {
 *     emptyWhen: (d) => !d?.results?.length,
 *     onError: (msg) => errorToast(msg), // optional toast for non-blocking errors
 *   })
 *   onMounted(() => run())
 *
 * Pair with PageStateShell in template:
 *   <PageStateShell :loading="loading" :error="error" :empty="isEmpty()" skeleton="table">
 *     ...content...
 *   </PageStateShell>
 *
 * Concurrent `run()` calls are sequenced: only the latest completion updates
 * `data` / `error` / `loading`. Stale successes and failures are ignored so a
 * slower earlier request cannot wipe a newer result.
 *
 * @param {() => Promise<any>} fetcher
 * @param {{ initialLoading?: boolean, errorFallback?: string, emptyWhen?: (data: any) => boolean, onError?: (message: string, err: unknown) => void }} [options]
 */
export function usePageState(fetcher, options = {}) {
  const {
    initialLoading = false,
    errorFallback = i18n.global.t('common.requestFailed'),
    emptyWhen = null,
    onError = null,
  } = options

  const loading = ref(initialLoading)
  const error = ref('')
  const data = shallowRef(null)
  let runSeq = 0

  async function run(...args) {
    const seq = ++runSeq
    loading.value = true
    error.value = ''
    try {
      const result = await fetcher(...args)
      if (seq !== runSeq) return result
      data.value = result
      return result
    } catch (err) {
      if (seq !== runSeq) throw err
      const message = getApiErrorMessage(err, errorFallback)
      error.value = message
      data.value = null
      onError?.(message, err)
      throw err
    } finally {
      if (seq === runSeq) {
        loading.value = false
      }
    }
  }

  function reset() {
    runSeq += 1
    loading.value = false
    error.value = ''
    data.value = null
  }

  function isEmpty() {
    if (emptyWhen) return emptyWhen(data.value)
    if (data.value == null) return true
    if (Array.isArray(data.value)) return data.value.length === 0
    if (typeof data.value === 'object' && Array.isArray(data.value.results)) {
      return data.value.results.length === 0
    }
    return false
  }

  return {
    loading,
    error,
    data,
    run,
    reset,
    isEmpty,
  }
}
