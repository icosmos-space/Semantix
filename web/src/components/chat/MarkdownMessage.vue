<template>
  <div ref="root" class="md-body" v-html="html"></div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { renderChatMarkdown } from '@/utils/markdown'
import { destroyGptVisIn, mountGptVisIn } from '@/utils/mountGptVis'

const props = defineProps<{ content: string }>()
const root = ref<HTMLElement | null>(null)
const html = computed(() => renderChatMarkdown(props.content))

async function remount() {
  await nextTick()
  if (root.value) mountGptVisIn(root.value)
}

watch(html, remount, { immediate: true })

onBeforeUnmount(() => {
  if (root.value) destroyGptVisIn(root.value)
})
</script>

<style scoped>
.md-body {
  line-height: 1.6;
  overflow-x: auto;
}
.md-body :deep(pre) {
  background: #0f172a;
  color: #e2e8f0;
  padding: 12px;
  border-radius: 8px;
  overflow: auto;
}
.md-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0 12px;
}
.md-body :deep(th),
.md-body :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 6px 10px;
  text-align: left;
}
</style>
