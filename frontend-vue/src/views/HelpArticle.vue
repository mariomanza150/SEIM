<template>
  <div class="help-article-page" data-testid="help-article-page">
    <PageHeader
      :title="article?.title || t('route.names.HelpArticle')"
      :subtitle="article?.introduction || ''"
      icon-class="bi bi-journal-text"
      :help-key="false"
    >
      <template #breadcrumb>
        <PageBreadcrumb
          :aria-label="t('help.breadcrumbAria')"
          :items="[
            { to: { name: 'Dashboard' }, label: t('route.names.Dashboard') },
            { to: { name: 'HelpCenter' }, label: t('route.names.HelpCenter') },
            { label: article?.title || t('route.names.HelpArticle'), truncate: true },
          ]"
        />
      </template>
      <template #actions>
        <router-link :to="backToHelp" class="btn btn-outline-secondary" data-testid="help-article-back">
          {{ t('help.backToHelp') }}
        </router-link>
      </template>
    </PageHeader>

    <LoadingState
      v-if="loading"
      :spinner-label="t('help.loading')"
      :hint="t('help.loadingHint')"
    />
    <EmptyState
      v-else-if="error"
      icon-class="bi bi-journal-x"
      :title="t('help.articleUnavailableTitle')"
      :body="error"
      test-id="help-article-unavailable"
    >
      <template #actions>
        <router-link :to="{ name: 'HelpCenter' }" class="btn btn-primary">
          {{ t('help.backToHelp') }}
        </router-link>
      </template>
    </EmptyState>
    <template v-else-if="article">
      <div class="card mb-4">
        <div
          class="card-body help-article-body"
          data-testid="help-article-body"
          v-html="bodyHtml"
        />
      </div>
      <section v-if="related.length" data-testid="help-related">
        <h3 class="h5 mb-3">{{ t('help.relatedTitle') }}</h3>
        <div class="list-group">
          <router-link
            v-for="item in related"
            :key="item.slug"
            :to="{ name: 'HelpArticle', params: { slug: item.slug } }"
            class="list-group-item list-group-item-action"
          >
            {{ item.title }}
          </router-link>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { fetchHelpArticle, fetchHelpArticles, unwrapHelpArticles } from '@/services/help'
import { sanitizeHelpHtml } from '@/utils/helpHtml'
import PageHeader from '@/components/PageHeader.vue'
import PageBreadcrumb from '@/components/PageBreadcrumb.vue'
import EmptyState from '@/components/State/EmptyState.vue'
import LoadingState from '@/components/State/LoadingState.vue'

const route = useRoute()
const { t } = useI18n()

const loading = ref(true)
const error = ref('')
const article = ref(null)
const related = ref([])

const bodyHtml = computed(() => sanitizeHelpHtml(article.value?.body_html || ''))
const backToHelp = computed(() => ({ name: 'HelpCenter' }))

async function loadArticle() {
  loading.value = true
  error.value = ''
  article.value = null
  related.value = []
  const slug = String(route.params.slug || '')
  try {
    const { data } = await fetchHelpArticle(slug)
    article.value = data
    if (data?.topic) {
      try {
        const relatedRes = await fetchHelpArticles({ topic: data.topic })
        related.value = unwrapHelpArticles(relatedRes.data).filter((item) => item.slug && item.slug !== slug)
      } catch {
        related.value = []
      }
    }
  } catch (e) {
    const status = e?.response?.status
    error.value = status === 404 ? t('help.articleUnavailableBody') : t('help.articleLoadError')
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.slug,
  () => {
    loadArticle()
  },
  { immediate: true },
)
</script>

<style scoped>
.help-article-body :deep(img) {
  max-width: 100%;
  height: auto;
}

.help-article-body :deep(table) {
  width: 100%;
}
</style>
