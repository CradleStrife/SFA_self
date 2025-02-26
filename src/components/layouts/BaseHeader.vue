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
      <template #title>Assay Data</template>
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
  </el-menu>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const activeIndex = ref<string>(route.path);  // 初始值绑定当前路由路径

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
