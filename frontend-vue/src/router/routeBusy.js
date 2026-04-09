import { ref } from 'vue'

/** True while a client-side navigation is resolving (guards, lazy chunks). Binds to `<main aria-busy>`. */
export const routeBusy = ref(false)
