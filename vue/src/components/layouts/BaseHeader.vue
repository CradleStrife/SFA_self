<template>
  <el-menu
    class="el-menu-demo"
    mode="horizontal"
    :default-active="activeIndex"
    router
  >
    <el-menu-item index="/">
      <router-link to="/" class="full-link">Home</router-link>
    </el-menu-item>

    <el-sub-menu index="/localdata">
      <template #title>Local Data</template>
      <el-menu-item index="/GeographicalDistribution">
        <router-link to="/GeographicalDistribution" class="full-link">Geographical Distribution</router-link>
      </el-menu-item>
      <el-menu-item index="/enquiry">
        <router-link to="/enquiry" class="full-link">Enquiry</router-link>
      </el-menu-item>
      <el-menu-item index="/trendAnalysis">
        <router-link to="/trendAnalysis" class="full-link">Trend Analysis</router-link>
      </el-menu-item>
      <el-menu-item index="/upload">
        <router-link to="/upload" class="full-link">Upload</router-link>
      </el-menu-item>
    </el-sub-menu>

    <el-sub-menu index="/assaydata">
      <template #title>Global Data</template>
      <el-menu-item index="/Geo_assay">
        <router-link to="/Geo_assay" class="full-link">Geographical Distribution</router-link>
      </el-menu-item>
      <el-menu-item index="/enquiry_assay">
        <router-link to="/enquiry_assay" class="full-link">Enquiry</router-link>
      </el-menu-item>
      <el-menu-item index="/trend_assay">
        <router-link to="/trend_assay" class="full-link">Trend Analysis</router-link>
      </el-menu-item>
      <!-- <el-menu-item index="/upload_assay">
        <router-link to="/upload_assay" class="full-link">Upload</router-link>
      </el-menu-item> -->
    </el-sub-menu>

    <el-menu-item index="/clustering">
      <router-link to="/clustering" class="full-link">Clustering Analysis</router-link>
    </el-menu-item>

    <el-sub-menu index="/">
      <template #title>Cache</template>
      <el-menu-item @click="clearBackendCache">Clear Backend Cache</el-menu-item>
      <el-menu-item @click="clearBrowserCache">Clear Browser Cache</el-menu-item>
      <el-menu-item @click="clearAllCache">Clear All Cache</el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>

<script lang="ts" setup>
import { getCurrentInstance, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import { useRouter } from 'vue-router';
// 获取当前实例以获取 apiUrl
const instance = getCurrentInstance();
if (!instance) {
  throw new Error("Failed to get current instance");
}

const apiUrl = (instance.proxy as any).$apiHost;
if (!apiUrl) {
  throw new Error("API URL not found");
}
const router = useRouter();

const route = useRoute();
const activeIndex = ref<string>(route.path);  // 初始值绑定当前路由路径

const clearBackendCache = () => {
  axios.delete(`${apiUrl}/api/clear_cache/`);
  location.reload();
}
const clearBrowserCache = () => {
  sessionStorage.clear();
  localStorage.clear();
  location.reload();
}

const clearAllCache = () => {
  axios.delete(`${apiUrl}/api/clear_cache/`);
  sessionStorage.clear();
  localStorage.clear();
  location.reload();
}

// 监听路由变化，动态更新导航栏高亮
watch(
  () => route.path,
  (newPath) => {
    activeIndex.value = newPath;
  },
  { immediate: true }
);
</script>

<style scoped>
.full-link {
  display: block;
  width: 100%;
  height: 100%;
  line-height: inherit;
  color: inherit;
  text-decoration: none;
}
.el-menu-demo {
  display: flex;
  justify-content: center;
  padding: 0;
  margin: 0;
  list-style: none;
  width: 100%;
}

.el-menu-demo > .el-menu-item,
.el-menu-demo > .el-sub-menu {
  flex-grow: 1;
  text-align: center;
}

.el-menu-demo > .el-sub-menu .el-sub-menu__title {
  display: flex;
  justify-content: center;
  width: 100%;
}
</style>
