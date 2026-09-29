<template>
  <div class="help-center-page" data-testid="help-center-page">
    <PageHeader
      :title="t('help.title')"
      :subtitle="t('help.subtitle')"
      icon-class="bi bi-question-circle"
      :help-key="false"
    >
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('help.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { label: t('route.names.HelpCenter') },
          ]"
        />
      </template>
    </PageHeader>

    <div class="row mb-4">
      <div class="col-md-8 col-lg-6">
        <label class="form-label" for="help-search">{{ t('help.searchLabel') }}</label>
        <div class="input-group">
          <input
            id="help-search"
            v-model="searchInput"
            type="search"
            class="form-control"
            :placeholder="t('help.searchPlaceholder')"
            data-testid="help-search"
            @keyup.enter="applySearch"
          >
          <button type="button" class="btn btn-primary" data-testid="help-search-submit" @click="applySearch">
            {{ t('help.searchButton') }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="contextualKey && !loading && articles.length > 1"
      class="alert alert-info"
      data-testid="help-contextual-banner"
    >
      {{ t('help.contextualBanner') }}
    </div>

    <PageStateShell
      :loading="loading"
      :error="error"
      :empty="!articles.length"
      :empty-title="t('help.emptyTitle')"
      :empty-body="t('help.emptyBody')"
      empty-icon-class="bi bi-journal-x"
      empty-test-id="help-center-empty"
      error-test-id="help-center-error"
      skeleton="cards"
      :skeleton-count="4"
      :loading-label="t('help.loading')"
      :loading-hint="t('help.loadingHint')"
    >
      <template v-if="searchInput || contextualKey" #emptyActions>
        <button type="button" class="btn btn-outline-primary" data-testid="help-clear-search" @click="clearSearch">
          {{ t('help.emptyClear') }}
        </button>
      </template>
    <div>
      <section
        v-for="group in topicGroups"
        :key="group.topic"
        class="mb-4"
        :data-testid="`help-topic-${group.topic}`"
      >
        <h3 class="h5 mb-3">{{ topicLabel(group.topic) }}</h3>
        <div class="list-group">
          <router-link
            v-for="article in group.articles"
            :key="article.slug"
            :to="{ name: 'HelpArticle', params: { slug: article.slug } }"
            class="list-group-item list-group-item-action"
            :data-testid="`help-article-link-${article.slug}`"
          >
            <div class="fw-semibold">{{ article.title }}</div>
            <div v-if="article.introduction" class="text-muted small">{{ article.introduction }}</div>
          </router-link>
        </div>
      </section>
    </div>
    </PageStateShell>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { fetchHelpArticles, unwrapHelpArticles } from '@/services/help'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import PageStateShell from '@/components/State/PageStateShell.vue'

const TOPIC_ORDER = [
  'getting_started',
  'applications',
  'documents',
  'review',
  'partner',
  'admin',
  'account',
  'other',
]

const route = useRoute()
const router = useRouter()
const { t, te } = useI18n()
const { error: errorToast } = useToast()

const loading = ref(true)
const error = ref('')
const articles = ref([])
const searchInput = ref(typeof route.query.q === 'string' ? route.query.q : '')

const contextualKey = computed(() => (typeof route.query.key === 'string' ? route.query.key : ''))

function topicLabel(topic) {
  const key = `help.topics.${topic}`
  return te(key) ? t(key) : t('help.topics.other')
}

const topicGroups = computed(() => {
  const buckets = new Map()
  for (const article of articles.value) {
    const topic = article.topic || 'other'
    if (!buckets.has(topic)) buckets.set(topic, [])
    buckets.get(topic).push(article)
  }
  return TOPIC_ORDER.filter((topic) => buckets.has(topic)).map((topic) => ({
    topic,
    articles: buckets.get(topic),
  })).concat(
    [...buckets.keys()]
      .filter((topic) => !TOPIC_ORDER.includes(topic))
      .map((topic) => ({ topic, articles: buckets.get(topic) })),
  )
})

function applySearch() {
  const q = searchInput.value.trim()
  const nextQuery = { ...route.query }
  if (q) nextQuery.q = q
  else delete nextQuery.q
  router.replace({ name: 'HelpCenter', query: nextQuery })
}

function clearSearch() {
  searchInput.value = ''
  router.replace({ name: 'HelpCenter' })
}

async function loadArticles() {
  loading.value = true
  error.value = ''
  try {
    const q = typeof route.query.q === 'string' ? route.query.q.trim() : ''
    const key = contextualKey.value
    const { data } = await fetchHelpArticles({ q, key })
    const list = unwrapHelpArticles(data)
    articles.value = list
    if (key && !q && list.length === 1 && list[0].slug) {
      await router.replace({ name: 'HelpArticle', params: { slug: list[0].slug } })
    }
  } catch (e) {
    console.error(e)
    articles.value = []
    error.value = t('help.loadError')
    errorToast(error.value)
  } finally {
    loading.value = false
  }
}

watch(
  () => [route.query.q, route.query.key],
  () => {
    searchInput.value = typeof route.query.q === 'string' ? route.query.q : ''
    loadArticles()
  },
  { immediate: true },
)
</script>
