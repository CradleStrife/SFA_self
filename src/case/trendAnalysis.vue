<template>
  <el-container>
<!-- Year Range Layer -->
<div v-if="isYearRangeVisible" class="fixed-floating-layer">
    <el-row type="flex" class="year-range-row" style="padding: 15px; background-color: rgba(255, 255, 255, 0.9); border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
      <el-col :span="6" :offset="6">
        <b style="font-size: 24px;">Year Range</b>
      </el-col>
      <el-col :span="8">
        <el-date-picker
          v-model="value2"
          type="daterange"
          unlink-panels
          range-separator="To"
          start-placeholder="Start Date"
          end-placeholder="End Date"
          style="font-size: 16px; width: 100%;"
        />
      </el-col>
      <!-- Add a hide button with text -->
      <el-col :span="2" style="text-align: right;">
        <el-button
          @click="toggleYearRangeVisibility"
          type="warning"
          icon="el-icon-arrow-up"
          style="font-size: 16px; padding: 10px 20px;"
        >
          Hide Year Range
        </el-button>
      </el-col>
    </el-row>
  </div>
  <div v-else class="show-floating-layer-button">
  <!-- Show button when the layer is hidden -->
  <el-button
    type="success"
    @click="toggleYearRangeVisibility"
    icon="el-icon-arrow-down"
    style="font-size: 18px; padding: 15px 30px; border-radius: 10px; background-color: rgba(0, 128, 0, 0.8); color: white;"
  >
    Show Year Range
  </el-button>
</div>


      <!--------------------------------------Back Button------------------------------------------>

    <el-main>
      <el-row type="flex">
        <el-col :span="24">
          <el-page-header @back="goBack" title="Back"></el-page-header>
        </el-col>
      </el-row>

      <!-------------------------------------- First layer Serovar------------------------------------------->

      <h1>Trend Analysis</h1>
      <el-row type="flex">
        <!-- <h6>Serovar Monitoring</h6> -->
        <el-col :span="10":offset="1" >
          <div style="display: inline-block;"></div>
          <sero_ID :seroData="seroData" :start-date="value2 ? value2[0] : null" :end-date="value2 ? value2[1] : null" />
        </el-col>
        <el-col :span="10" :offset="1">
          <div style="display: inline-block;"></div>
          <mlst_ID :mlstData="mlstData" :start-date="value2 ? value2[0] : null" :end-date="value2 ? value2[1] : null" />
        </el-col>
      </el-row>

      <!-------------------------------------- Hint for click (1.24 larry)------------------------------------------->
      <div style="text-align: center; margin-top: 10px; margin-bottom: 30px; font-size: 14px; color: #666;">
        Click on an MLST in the table above to display its total count trend over time.
      </div>

        <!-------------------------------------- First layer MLST------------------------------------------->
      <el-row type="flex">
        <el-col :span="24">
          <div style="display: inline-block;"></div>
          <h3>MLSTs with the Highest Frequency of count</h3>
          <Bar_MLST :chartData="mlstData" />
        </el-col>
      </el-row>

      <!-------------------------------------- Second layer ------------------------------------------->
      <el-row type="flex">
        <el-col :span="20" :offset="2">
          <h2>Top 10 Countries</h2>
        </el-col>
      </el-row>
      <!-------------------------------------- Barchart here  ------------------------------------------->
      <el-row type="flex">
        <el-col :span="10" :offset="2">
          <div style="display: inline-block;"></div>
          <BarChart :chartData="countryChartData" />
        </el-col>
        <!-------------------------------------- Map here  ------------------------------------------->
        <el-col :span="10" >
          <div style="display: inline-block;"></div>
          <MapChart :mapData="mapChartData" />
        </el-col>
        <div style="clear:both"></div>
      </el-row>
      <!-------------------------------------- Word Cloud here  ------------------------------------------->
      <el-row type="flex">
        <el-col :span="10" :offset="2"> 
          <div style="display: inline-block;"></div>         
          <h3>Top 10 Serotype</h3>
          <WordCloud :processdata="serotypeData.slice(0,10)" />
        </el-col>
      <!-------------------------------------- country table here  ------------------------------------------->
        <el-col :span="10" >
          <div style="display: inline-block;"></div>
          <h4>Countries Associated with Serotypes</h4>
          <Countrytable :serocountryData="serocountryData"/>
        </el-col>
        <div style="clear:both"></div>        
      </el-row>
         <!-------------------------------------- MLST Table here  ------------------------------------------->
      <el-row type="flex">
        <el-col :span="24">
         <el-select class="hidden-select"></el-select>
          <div style="display: inline-block;"></div>
          <h5>Top 3 MLST for each Serotype</h5>
          <TableChart :seroMLSTData="seroMLSTData"/>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<!-------------------------------------- Script Layer  ------------------------------------------->
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

.hidden-select {
  display: none;
}

/* larry */
/* Fixed floating layer */
.fixed-floating-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  background-color: #ffffff;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  padding: 10px 0;
}

/* Show button when layer is hidden */
.show-floating-layer-button {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 1001;
}

/* Main content spacing */
.content-with-margin {
  margin-top: 80px; /* 留出浮动层的高度空间 */
}

/* Adjust main content to leave space for the floating layer */
.content-with-margin {
  margin-top: 80px; /* Adjust based on the height of the floating layer */
}

/* Styling for the year range row */
.year-range-row {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
}
</style>