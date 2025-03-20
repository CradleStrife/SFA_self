<template>
  <el-config-provider namespace="ep">
    <header>
      <BaseHeader />
    </header>
    <main>
      <router-view />
    </main>
  </el-config-provider>
</template>

<script>
import BaseHeader from './components/layouts/BaseHeader.vue';

export default {
  components: {
    BaseHeader
  }
};
</script>

<style>
#app {
  text-align: center;
  color: var(--ep-text-color-primary);
}
</style>
