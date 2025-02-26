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
          <el-scrollbar style="height: calc(100vh-210px);">
            <EnquiryTable 
              :processedResults="processedResults"
              @edit="handleEdit"
            />
          </el-scrollbar>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MapChart from '../components/MapChart.vue';
import EnquiryTable from '../components/EnquiryTable.vue';

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

// Retrieve and process results from session storage on component mount
onMounted(() => {
  const startTime = performance.now();
  const storedResults = sessionStorage.getItem('searchResults');
  const updatedResult = route.query.updatedResult ? JSON.parse(route.query.updatedResult as string) : null;

  if (storedResults) {
    const rawResults = JSON.parse(storedResults);
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