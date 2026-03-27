import { ref, onUnmounted } from 'vue'

/**
 * Reactive polling composable.
 * Calls `fn` immediately, then every `intervalMs`.
 * Stops automatically on component unmount.
 */
export function usePolling(fn, intervalMs = 10000) {
  const isPolling = ref(false)
  let timer = null

  function start() {
    if (isPolling.value) return
    isPolling.value = true
    fn()
    timer = setInterval(fn, intervalMs)
  }

  function stop() {
    isPolling.value = false
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  onUnmounted(stop)

  return { start, stop, isPolling }
}
