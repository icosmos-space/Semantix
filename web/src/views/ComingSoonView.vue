<template>
  <el-empty :description="`${moduleName} 将在后续 Phase 交付`" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const moduleName = computed(() => String(route.params.module || '模块'))
</script>
