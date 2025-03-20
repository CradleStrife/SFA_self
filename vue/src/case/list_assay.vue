<template>
  <el-container>
    <el-main>
      <el-row type="flex" style="height: 100%; flex-direction: column;">
        <el-row type="flex" style="padding: 1em;">
          <el-col>
            <el-page-header @back="goBack" title="Back"></el-page-header>
            <h1>
              We found {{ totalResults }} result{{ totalResults !== 1 ? 's' : '' }} for your search
            </h1>
            <p>Current index: {{ index_type }}</p>
          </el-col>
        </el-row>

        <el-row type="flex">
          <el-col :span="24">
            <el-scrollbar> <!-- 调整滚动区域高度 -->
              <RecursiveTable 
                :processedResults="currentPageResults"
                :showMore="showMore"
                @toggleShowMore="toggleShowMore"
              />
            </el-scrollbar>
          </el-col>
        </el-row>

        <!-- 分页组件 -->
        <el-row type="flex" justify="center" style="padding: 1em;">
          <el-pagination
            @size-change="handlePageSizeChange"
            @current-change="handleCurrentPageChange"
            :current-page="currentPage"
            :page-sizes="[50, 100, 200]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalResults"
            background
          ></el-pagination>
        </el-row>
      </el-row>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, getCurrentInstance } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import RecursiveTable from '../components/RecursiveTable.vue';
import { saveSearchResultsToSessionStorage, getSearchResultsFromSessionStorage } from '../splitStorage';

const instance = getCurrentInstance();
const apiUrl = (instance.proxy as any).$apiHost;

const router = useRouter();
const route = useRoute();

// 分页相关状态
const currentPage = ref(1);
const pageSize = ref(100);
const totalResults = ref(0);

// 数据状态
const processedResults = ref<any[]>([]);
const showMore = ref<boolean[]>([]);

// 计算当前页数据
const currentPageResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return processedResults.value.slice(start, end);
});

const index_type=ref();

onMounted(async () => {
  const startTime = performance.now();
  index_type.value = sessionStorage.getItem('index_type');
  // 从分块存储中获取完整数据
  const rawResults = getSearchResultsFromSessionStorage();
  processedResults.value = rawResults.map(item => ({
    ...item,
    // 初始化showMore状态
    showMore: false
  }));
  
  totalResults.value = processedResults.value.length;
  showMore.value = Array(processedResults.value.length).fill(false);

  logPerformance(startTime, "Loading and processing results");
});

// 分页控制方法
const handlePageSizeChange = (newSize: number) => {
  pageSize.value = newSize;
  currentPage.value = 1; // 切换页大小后回到第一页
};

const handleCurrentPageChange = (newPage: number) => {
  currentPage.value = newPage;
};

// 显示更多控制
const toggleShowMore = (index: number) => {
  processedResults.value[index].showMore = !processedResults.value[index].showMore;
};

const goBack = () => {
  router.back();
};

const logPerformance = (startTime: number, message: string) => {
  const endTime = performance.now();
  console.log(`${message}: ${endTime - startTime} ms`);
};
</script>

<style scoped>
/* 保持原有样式 */
.result-box {
  border: 1px solid #ddd;
  padding: 10px;
  margin-bottom: 10px;
  text-align: left;
  background-color: rgb(231, 231, 231);
}

/* 分页样式优化 */
.el-pagination {
  margin-top: 1rem;
  padding: 0 1em;
}
</style>