<template>
  <el-container>
    <!-- 主内容 -->
    <el-main>
      <!-- 第一行 -->
      <el-row type="flex" style="padding: 1em;">
        <el-col>
          <el-page-header @back="goBack" title="Back to Menu"></el-page-header>
          <h1>We found {{ processedResults.length }} result{{ processedResults.length !== 1 ? 's' : '' }} for your search</h1>
        </el-col>
      </el-row>

      <!-- 地图部分固定在顶部 -->
      <el-header style="height: 300px; padding: 0;">
        <MapChart :mapData="mapChartData" :enableClick="true" style="width: 100%; height: 100%;" />
      </el-header>

      <!-- 搜索结果部分 -->
      <el-row type="flex">
        <el-col :span="24">
          <el-scrollbar>
            <EnquiryTable 
              :processedResults="currentPageResults"
              @edit="handleEdit"
            />
          </el-scrollbar>
        </el-col>
      </el-row>

      <!-- 分页组件 -->
      <el-row type="flex" justify="center">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="processedResults.length"
        >
        </el-pagination>
      </el-row>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MapChart from '../components/MapChart.vue';
import EnquiryTable from '../components/EnquiryTable.vue';
import { saveSearchResultsToSessionStorage, getSearchResultsFromSessionStorage} from '../splitStorage'


const logPerformance = (startTime: number, message: string) => {
  const endTime = performance.now();
  console.log(`${message}: ${endTime - startTime} ms`);
};

const processedResults = ref<Array<{
  ID: string;
  Source: string;
  Date: string;
  Country: string;
  Brand: string;
  Serotype: string;
  MLST: string;
  AST: string;
  SPI: string;
  AMR: string;
  plasmid: string; 
}>>([]);

const mapChartData = ref<{ [key: string]: number }>({});
const delimiterPattern = /\s*(?:and|,|;)\s*/;
const router = useRouter();
const route = useRoute();

// 分页相关数据
const currentPage = ref(1);
const pageSize = ref(100);

// 计算当前页的结果
const currentPageResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return processedResults.value.slice(start, end);
});

// const saveSearchResultsToSessionStorage = (results: any[]) => {
//   for (let i = 0; i < results.length; i+=500) {
//     if (i+100 > results.length) {
//       sessionStorage.setItem(`searchResults${i}`, JSON.stringify(results.slice(i, results.length)));
//     } else {
//     sessionStorage.setItem(`searchResults${i}`, JSON.stringify(results.slice(i, i+100)));
//     }
//   }
// }

// const getSearchResultsFromSessionStorage = () => {
//   const results: any[] = [];
//   let i=0;
//   while (sessionStorage.getItem(`searchResults${i}`)) {
//     results.push(...JSON.parse(sessionStorage.getItem(`searchResults${i}`)!));
//     i+=500;
//   }
//   return results;
// }

// Retrieve and process results from session storage on component mount
onMounted(() => {
  const startTime = performance.now();
  // const storedResults = sessionStorage.getItem('searchResults');
  const storedResults = getSearchResultsFromSessionStorage();
  const updatedResult = route.query.updatedResult ? JSON.parse(route.query.updatedResult as string) : null;

  if (storedResults) {
    const rawResults = storedResults;
    processedResults.value = rawResults.map((tuple: any) => ({
      ID: tuple[0],
      Source: tuple[1],
      Date: tuple[2],
      Country: tuple[3],
      Brand: tuple[4],
      Serotype: tuple[5],
      MLST: tuple[6],
      AST: tuple[7],
      SPI: tuple[8],
      AMR: tuple[9],
      plasmid: tuple[10]
    }));

    for (let result of processedResults.value) {
      if (result.Date === '1900-01-01') {
        result.Date = 'NaT';
      }
    }

    if (updatedResult) {
      const index = processedResults.value.findIndex(item => item.ID === updatedResult.ID);
      if (index !== -1) {
        processedResults.value[index] = updatedResult;
      }
    }

    // Process map data
    const countryCounts: { [key: string]: number } = {};
    processedResults.value.forEach(result => {
      if (result.Country) {
        const countries = result.Country.split(delimiterPattern);
        countries.forEach(Country => {
          if (!countryCounts[Country]) {
            countryCounts[Country] = 0;
          }
          countryCounts[Country] += 1;
        });
      }
      const keys = ['ID', 'Source', 'Date', 'Brand', 'Serotype', 'MLST'];
      keys.forEach(key => {
        if (typeof result[key] === 'string' && result[key].startsWith("['") && result[key].endsWith("']")) {
          result[key] = result[key].slice(2, -2);
        }
      });
    });

    mapChartData.value = countryCounts;
  }
  logPerformance(startTime, "Processing stored results and map data");
});

const handleEdit = (index: number, row: any) => {
  sessionStorage.setItem('selectedResult', JSON.stringify(row));
  router.push({ name: 'UpdatePage' });
};

const goBack = () => {
  router.back();
};

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize;
};

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage;
};
</script>

<style scoped>
.result-box {
  border: 1px solid #ddd;
  padding: 10px;
  margin-bottom: 10px;
  text-align: left;
  background-color: rgb(231, 231, 231);
}

.hidden {
  display: none;
}

.word-cloud-container {
  border: 1px solid rgb(211, 208, 208);
  border-radius: 5px;
  padding: 10px;
  box-sizing: border-box;
}
</style>    