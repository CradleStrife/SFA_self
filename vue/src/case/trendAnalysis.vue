<template>
  <el-container class="main-container">
    <!-- 统一头部容器 -->
    <div class="header-container">
      <!-- 单一返回按钮 -->
      <el-page-header 
        @back="goBack" 
        title="Back" 
      ></el-page-header>

      <div class="year-range-container">
        <div class="year-range-row">
          <div class="year-range-title" style="font-size: 24px;">
            Year Range
          </div>
          <el-date-picker
            v-model="value2"
            type="daterange"
            unlink-panels
            range-separator="To"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            style="width: 200px;"
            @change="onYearRangeChange"
          />
        </div>
      </div>
    </div>

    <el-main class="main-content">
      <!-- 删除重复的返回按钮 -->
      <!-- 原代码中的以下段落已删除 -->
      <!--
      <el-row type="flex">
        <el-col :span="24">
          <el-page-header @back="goBack" title="Back"></el-page-header>
        </el-col>
      </el-row>
      -->

      <!-------------------------------------- First layer Serovar------------------------------------------->

      <h1 style="text-align: center; margin-top: 40px;">Trend Analysis</h1>
      <el-row type="flex" justify="space-around" margin="30px 0">
        <el-col :span="10">
          <sero_ID 
            :seroData="seroData" 
            :start-date="value2 ? value2[0] : null" 
            :end-date="value2 ? value2[1] : null" 
          />
        </el-col>
        <el-col :span="10">
          <mlst_ID 
            :mlstData="mlstData" 
            :start-date="value2 ? value2[0] : null" 
            :end-date="value2 ? value2[1] : null" 
          />
        </el-col>
      </el-row>

      <!-------------------------------------- MLST Frequency Chart -------------------------------------------->
      <el-row type="flex" justify="center" margin="30px 0">
        <el-col :span="24">
          <div style="text-align: center;">
            <h3>MLSTs with the Highest Frequency of Count</h3>
            <Bar_MLST :chartData="mlstData" />
          </div>
        </el-col>
      </el-row>

      <!-------------------------------------- Country Analysis -------------------------------------------->
      <el-row type="flex" justify="space-around" margin="30px 0">
        <el-col :span="10">
          <BarChart :chartData="countryChartData" />
        </el-col>
        <el-col :span="10">
          <MapChart :mapData="mapChartData" />
        </el-col>
      </el-row>

      <!-------------------------------------- Serotype Analysis -------------------------------------------->
      <el-row type="flex" justify="center" margin="30px 0">
        <el-col :span="20">
          <!-- <WordCloud :processdata="serotypeData.slice(0,10)" /> -->
          <wordcloudserotype :processdata="serotypeData.slice(0,10)" />
        </el-col>
      </el-row>

      <!-------------------------------------- MLST Table -------------------------------------------->
      <el-row type="flex" justify="center" margin="30px 0">
        <el-col :span="24">
          <TableChart :seroMLSTData="seroMLSTData" />
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import BarChart from '../components/BarChart.vue';
import MapChart from '../components/MapChart.vue';
import WordCloud from '../components/wordcloud.vue';
import TableChart from '../components/TableChart.vue';
import Countrytable from '../components/Countrytable.vue';
import sero_ID from '../components/sero_ID.vue';
import mlst_ID from '../components/mlst_ID.vue';
import Bar_MLST from '../components/Bar_MLST.vue';


//1.22
// 控制 Year Range 显示的状态
const isYearRangeVisible = ref(true);
const toggleYearRangeVisibility = () => {
  isYearRangeVisible.value = !isYearRangeVisible.value;
};

interface SeroData {
  ID: string[];
  Date: string[];
  Serotype: string[];
}

interface mlstData {
  ID: string[];
  Date: string[];
  MLST: string[];
}

const router = useRouter();
const value2 = ref<[Date, Date] | undefined>([new Date(), new Date()]);
const countryChartData = ref([]);
const mapChartData = ref({});
const serotypeData = ref([]);
const seroMLSTData = ref([]);
const serocountryData = ref([]);
const seroData = ref<SeroData[]>([]);
const mlstData = ref<mlstData[]>([]);

const instance = getCurrentInstance();
if (!instance) {
  throw new Error("Failed to get current instance");
}

const apiUrl = (instance.proxy as any).$apiHost;
if (!apiUrl) {
  throw new Error("API URL not found");
}

const goBack = () => {
  console.log('go back');
  router.back();
};

const logPerformance = (startTime: number, message: string) => {
        const endTime = performance.now();
        console.log(`${message}: ${endTime - startTime} ms`);
      };

const fetchCountryData = async () => {
  const [startDate, endDate] = value2.value || [];
  try {
    const startDateParam = startDate ? startDate.toISOString().split('T')[0] : null;
    const endDateParam = endDate ? endDate.toISOString().split('T')[0] : null;
    
    const requiredData = ['country_counts', 'serotypes','sero_MLST','country_sero','process_ID_serodata','process_ID_MLSTdata'].join(',');

    const response = await axios.get(`${apiUrl}/api/search/`, {
      params: {
        start_date: startDateParam,
        end_date: endDateParam,
        required_data: requiredData
      }
    });
    sessionStorage.setItem('index_type',"local")
    // console.log('API Response:', response.data);

    countryChartData.value = response.data.country_counts || {};
    mapChartData.value = response.data.country_counts || {};
    serotypeData.value = response.data.serotypes || [];
    seroMLSTData.value = response.data.sero_MLST || [];
    serocountryData.value = response.data.country_sero || [];
    seroData.value = response.data.process_ID_serodata || []; 
    mlstData.value = response.data.process_ID_MLSTdata || []; 

  } catch (error) {
    console.error('Error fetching country data:', error);
  }
};

watch(value2, async (newVal, oldVal) => {
  if (newVal && newVal.length === 2) {
    await fetchCountryData();

    // 确保默认日期范围能立即触发子组件更新
    if (mlstData.value.length > 0) {
      const [startDate, endDate] = newVal;
      mlstData.value = [...mlstData.value]; // 触发 Vue 的响应式机制
      seroData.value = [...seroData.value]; // 更新 seroData 的响应性
    }
  }
});


onMounted(async () => {
  try {
    const startYear = 1900;
    const endYear = new Date().getFullYear();
    value2.value = [new Date(`${startYear}-01-01`), new Date()] as [Date, Date];

    // 加载默认日期范围内的数据
    await fetchCountryData();

    // 如果有数据，确保触发子组件表格显示
    if (mlstData.value.length > 0) {
      const [startDate, endDate] = value2.value;
      mlstData.value = [...mlstData.value]; // 强制 Vue 更新
    }
    //对sero
    if (seroData.value.length > 0) {
      const [startDate, endDate] = value2.value;
      seroData.value = [...seroData.value]; // 强制 Vue 更新
    }
  } catch (error) {
    console.error('Error fetching data during onMounted:', error);
  }
});


// const shortcuts = [
//   {
//     text: 'This month',
//     value: [new Date(), new Date()],
//   },
//   {
//     text: 'This year',
//     value: () => {
//       const end = new Date();
//       const start = new Date(new Date().getFullYear(), 0);
//       return [start, end];
//     },
//   },
//   {
//     text: 'Last 6 months',
//     value: () => {
//       const end = new Date();
//       const start = new Date();
//       start.setMonth(start.getMonth() - 6);
//       return [start, end];
//     },
//   },
// ];
</script>

<style scoped>
/* 主要样式修改 */
.main-container {
  flex-direction: column;
  height: 100vh;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e0e0e0;
  position: relative; /* 为后续可能的悬浮效果预留 */
}

/* Year Range容器样式 */
.year-range-container {
  display: flex;
  align-items: center;
  gap: 20px;
  /* 居中处理 */
  margin-left: auto;
  margin-right: auto;
  max-width: 600px; /* 控制最大宽度 */
}

.year-range-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 响应式设计调整 */
@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    align-items: stretch;
    padding: 12px 16px;
  }

  .year-range-container {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    width: 100%;
  }

  .year-range-title {
    font-size: 18px;
    margin-bottom: 8px;
  }
}

/* 移除原有按钮样式 */
.show-floating-layer-button {
  display: none;
}

/* 其他样式保持不变 */
.el-main {
  padding-top: 60px; /* 根据header高度调整 */
}
</style>