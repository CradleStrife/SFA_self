<template>
  <el-container class="main-container">
    <div class="header-container">
      <div>
        <!-- 保留一个返回按钮 -->
        <el-page-header @back="goBack" title="Back"></el-page-header>
      </div>
      
      <div class="year-range-container">
        <div class="year-range-row">
          <div class="year-range-title" style="font-size: 24px;">
            Year Range
          </div>
          <el-date-picker
            v-model="yearRange"
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
    <el-main>

      <!-- Title and First Layer -->
      <h1>Trend Analysis</h1>
      <select v-model="selected_index" @change="reloadData">
        <option v-for="option in index_options" :value="option">{{ option }}</option>
      </select>
      <button type="primary" @click="reloadData">Reload Data</button>
      <el-row type="flex">
        <el-col :span="10" :offset="1">
          <sero_ID_a 
          :seroData="seroid" 
          :start-year="yearRange[0] ? yearRange[0].getFullYear() : null" 
          :end-year="yearRange[1] ? yearRange[1].getFullYear() : null"
          @row-click="handleSeroClick"
          />
        </el-col>
        <el-col :span="10" :offset="1">
          <mlst_ID_a 
          :mlstData="mlstid" 
          :start-year="yearRange[0] ? yearRange[0].getFullYear() : null" 
          :end-year="yearRange[1] ? yearRange[1].getFullYear() : null"
          @row-click="handleMLSTClick"  
          />
        </el-col>
      </el-row>

      <!-- 点击表格后显示的趋势图 -->
      <div v-if="selectedItem">
        <h4>Trend for {{ selectedItem.name }}</h4>
        <v-chart :option="trendChartOption" autoresize style="height: 400px;"></v-chart>
      </div>

      <!-- MLSTs Frequency Chart -->
      <el-row type="flex">
        <el-col :span="24">
          <h1>MLSTs with the Highest Frequency of Count</h1>
          <Bar_MLST_a :chartData="mlstid" />
        </el-col>
      </el-row>

      <!-- Top Occurrence Serotype -->
      <el-row type="flex">
        <el-col :span="24" >
          <h2>Top Occurrence Serotype</h2>
          <linesero_a :serotypeData="tableData" />
        </el-col>
      </el-row>

      <!-- Top Occurrence MLST -->
      <el-row type="flex">
        <el-col :span="24" >
          <h2>Top Occurrence MLST</h2>
          <lineMLST_a :mlsttypeData="mlsttableData" />
        </el-col>
      </el-row>

      <!-- Word Clouds -->
      <el-row type="flex">
        <el-col :span="10" :offset="2">
          <h3>{{ `Top ${topNsero || 'N'} Serotype` }}</h3>
          <el-select v-model="topNsero" placeholder="Select Top N" style="width: 200px; margin-bottom: 20px;">
            <el-option v-for="n in topNOptions" :key="n" :label="`Top ${n}`" :value="n" />
          </el-select>
          <wordcloudserotype :processdata="filteredSerovarData" />
        </el-col>
        <el-col :span="10">
          <h3>{{ `Top ${topNmlst || 'N'} MLST` }}</h3>
          <el-select v-model="topNmlst" placeholder="Select Top N" style="width: 200px; margin-bottom: 20px;">
            <el-option v-for="n in topNOptions" :key="n" :label="`Top ${n}`" :value="n" />
          </el-select>
          <wordcloudmlst :processdata="filteredMLSTData" />
        </el-col>
      </el-row>

      <!-- Table Filters -->
      <!-- <el-row type="flex" align="middle" justify="space-between">
        <el-col :span="8">
          <el-input
            v-model="selectedSerotype"
            placeholder="Filter by Serotype"
            clearable
          />
        </el-col>
        <el-col :span="8">
          <el-select v-model="topN" placeholder="Select Top N" clearable>
            <el-option
              v-for="n in topNOptions"
              :key="n"
              :label="`Top ${n}`"
              :value="n"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="resetFilters">Reset All Filters</el-button>
        </el-col>
      </el-row> -->

      <!-- MLST Table -->
      <el-row type="flex">
        <el-col :span="24">
          <TableChart :seroMLSTData="filteredSeroMLSTData" />
        </el-col>
      </el-row>
    </el-main>
    
  </el-container>
</template>
<script lang="ts" setup>
// laiyi 在 script setup 的开头添加这个导入
import { type Record as TypeRecord } from 'typescript';
import { ref, onMounted, computed, watch, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import linesero_a from '../components/linesero_a.vue';
import lineMLST_a from '../components/lineMLST_a.vue';
import WordCloud from '../components/wordcloud.vue';
import TableChart from '../components/TableChart.vue';
import sero_ID_a from '../components/sero_ID_a.vue';
import mlst_ID_a from '../components/mlst_ID_a.vue';
import Bar_MLST_a from '../components/Bar_MLST_a.vue';
import VChart from 'vue-echarts';
import * as echarts from 'echarts/core';
// 添加在 imports 部分
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import {
  LineChart,
  BarChart
} from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent
} from "echarts/components";
import {assay_types,sub_types,index_names} from '../index_names';
const index_options=ref(assay_types);
const selected_index=ref(index_options.value[0])
  
// 注册必要的组件
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent
]);

//laiyi:3/4
interface SerotypeRecord {
  name: string;
  initialCount: number;
  finalCount: number;
  increase: number;
}

interface MLSTRecord {
  name: string;
  initialCount: number;
  finalCount: number;
  increase: number;
}


interface AggregatedData {
  [key: string]: number;
}

// laiyi:添加在 script setup 顶部
interface Record {
  ID: string[];
  Date: string[];
  MLST: string[];
}

interface SelectedItem {
  name: string;
  type: 'serotype' | 'mlst';
}

interface ChartRow {
  name: string;
  initialCount: number;
  finalCount: number;
  increase: number;
}

interface ChartOption {
  title: {
    text: string;
    left: string;
  };
  tooltip: {
    trigger: string;
  };
  xAxis: {
    type: string;
    data: string[];
  };
  yAxis: {
    type: string;
    name: string;
  };
  series: Array<{
    type: string;
    data: number[];
    smooth: boolean;
  }>;
}

interface seroid {
  ID: string[];
  Date: string[];
  Serotype: string[];
}
interface mlstid {
  ID: string[];
  Date: string[];
  MLST: string[];
}

interface mlstword {
  name: string;
  value: number;
}
interface Seroword {
  name: string;
  value: number;
}

//laiyi



//laiyi
const trendChartOption = ref({});


const mlstid = ref<mlstid[]>([]);
const seroword = ref<Seroword[]>([]);
const seroMLSTData = computed(() => mlsttableData.value);
const seroid = ref<seroid[]>([]);
const mlstword = ref<mlstword[]>([]);
const tableData = ref([]);
const topNmlst = ref<number>(10);
const topNOptions = [10, 20, 30];
const topNsero = ref<number>(10);

const mlsttableData = ref([]);
// 新增变量
const selectedSerotype = ref<string | null>(null); // 用户选择的Serotype
const topN = ref<number | null>(null); // 用户选择的Top N
//laiyi添加：
const isYearRangeVisible = ref(true);
const selectedItem = ref<SelectedItem | null>(null);



// 修改点击处理函数
// 处理 Serovar 点击事件
// 处理 Serovar 点击事件
const handleSeroClick = (row: SerotypeRecord) => {
  selectedItem.value = {
    name: row.name,
    type: 'serotype'
  };
  
  // 筛选出与当前血清型对应的数据
  const dataForSero = seroid.value
    .filter((record) => record.Serotype.includes(row.name))
    .map((record) => ({
      date: record.Date[0],
      count: 1,
    }));

  // 按日期聚合数据
  const aggregatedData: AggregatedData = dataForSero.reduce((acc: AggregatedData, { date, count }) => {
    if (!acc[date]) {
      acc[date] = 0;
    }
    acc[date] += count;
    return acc;
  }, {});

  // 更新图表配置
  trendChartOption.value = {
    title: {
      text: `Trend for ${row.name}`,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: Object.keys(aggregatedData).sort(),
      axisLabel: {
        rotate: 45,
      },
    },
    yAxis: {
      type: 'value',
      name: 'Total Count',
    },
    series: [
      {
        type: 'line',
        data: Object.keys(aggregatedData)
          .sort()
          .map(date => aggregatedData[date]),
        smooth: true,
        lineStyle: {
          color: '#007BFF',
        },
        areaStyle: {
          opacity: 0.1,
        },
      },
    ],
  };
};

// 处理 MLST 点击事件
// 处理 MLST 点击事件
const handleMLSTClick = (row: MLSTRecord) => {
  selectedItem.value = {
    name: row.name,
    type: 'mlst'
  };
  
  // 筛选出与当前MLST对应的数据
  const dataForMLST = mlstid.value
    .filter((record) => record.MLST.includes(row.name))
    .map((record) => ({
      date: record.Date[0],
      count: 1,
    }));

  // 按日期聚合数据
  const aggregatedData: AggregatedData = dataForMLST.reduce((acc: AggregatedData, { date, count }) => {
    if (!acc[date]) {
      acc[date] = 0;
    }
    acc[date] += count;
    return acc;
  }, {});

  // 更新图表配置
  trendChartOption.value = {
    title: {
      text: `Trend for ${row.name}`,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: Object.keys(aggregatedData).sort(),
      axisLabel: {
        rotate: 45,
      },
    },
    yAxis: {
      type: 'value',
      name: 'Total Count',
    },
    series: [
      {
        type: 'line',
        data: Object.keys(aggregatedData)
          .sort()
          .map(date => aggregatedData[date]),
        smooth: true,
        lineStyle: {
          color: '#007BFF',
        },
        areaStyle: {
          opacity: 0.1,
        },
      },
    ],
  };
};







const instance = getCurrentInstance();
if (!instance) {
  throw new Error("Failed to get current instance");
}

const apiUrl = (instance.proxy as any).$apiHost;
if (!apiUrl) {
  throw new Error("API URL not found");
}

const router = useRouter();
const goBack = () => {
  router.back();
};
const fetchCountryData = async (startYear: number, endYear: number) => {
  console.log("fetch country data")
  try {
    // 使用纯年份格式
    const startDate = `${startYear}`;
    const endDate = `${endYear}`;

    console.log('请求日期:', { startDate, endDate });
    seroword.value = [];
    mlstword.value = [];
    seroid.value = [];
    mlstid.value = [];
    tableData.value = [];
    mlsttableData.value = [];
    const response = await axios.get(`${apiUrl}/api/search/`, {
      params: {
        start_date: startDate,
        end_date: endDate,
        required_data: [
          'serotype',
          'mlst_a',
          'process_mlst_tabledata_a',
          'process_country_sourcedata_a',
          'process_ID_MLSTdata_a',
          'process_ID_serodata_a',
        ].join(','),
        cache_bust: new Date().getTime(),  // 添加时间戳来避免缓存
        index: 'assay_data',  // 添加这一行，指定索引名称
        assay_index_name: index_names[selected_index.value]["assay"]
        // assay_index_name: index_names["ecoli"]["assay"]
      }
    });
    
    console.log("assay index name:",index_names[selected_index.value]["assay"])
    if (response.data) {
      console.log('API响应收到完整数据:', response.data);
      console.log('API响应收到，数据类型:', Object.keys(response.data));
  
      seroword.value = response.data.serotype || [];
      mlstword.value = response.data.mlst_a || [];
      seroid.value = response.data.process_ID_serodata_a || [];
      mlstid.value = response.data.process_ID_MLSTdata_a || [];
      tableData.value = response.data.process_country_sourcedata_a || [];
      mlsttableData.value = response.data.process_mlst_tabledata_a || [];
      
      console.log('处理后的数据:', {
        seroword: seroword.value.length,
        mlstword: mlstword.value.length,
        seroid: seroid.value.length,
        mlstid: mlstid.value.length,
        tableData: tableData.value.length,
        mlsttableData: mlsttableData.value.length
      });
      sessionStorage.setItem('index_type',selected_index.value)
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('API请求失败:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
    }
    // 设置空数据
    seroword.value = [];
    mlstword.value = [];
    seroid.value = [];
    mlstid.value = [];
    tableData.value = [];
    mlsttableData.value = [];
  }
};

const yearRange = ref<[Date, Date]>([new Date('1900-01-01'), new Date()]); 

// Reactively update filtered data when topN changes
const filteredMLSTData = computed(() => {
  const sortedData = [...mlstword.value].sort((a, b) => b.value - a.value);
  return topNmlst.value !== undefined ? sortedData.slice(0, topNmlst.value) : sortedData;
});



const filteredSerovarData = computed(() => {
  const sortedData = [...seroword.value].sort((a, b) => b.value - a.value);
  return topNsero.value !== undefined ? sortedData.slice(0, topNsero.value) : sortedData;
});

// Validate and apply year changes
// const onYearRangeChange = () => {
//   const [startYear, endYear] = yearRange.value;
//   if (startYear <= endYear) {
//     fetchCountryData(startYear, endYear);
//   } else {
//     console.error('Invalid year range: Start year must be less than or equal to end year.');
//   }
// };

// Fetch data on initial load
onMounted(async () => {
  console.log('onMounted');
  const currentYear = new Date().getFullYear();
  await fetchCountryData(1900, currentYear);
});
const onYearRangeChange = async (dates: [Date, Date] | null) => {
  if (dates) {
    const [start, end] = dates;
    const startYear = start.getFullYear();
    const endYear = end.getFullYear();
    console.log('年份范围已选择:', { startYear, endYear });
    await fetchCountryData(startYear, endYear);
  }
};

//新添加
// 修改 seroMLSTData 数据，增加筛选和Top N逻辑
const filteredSeroMLSTData = computed(() => {
  let data = mlsttableData.value; // 从原始数据开始
  // 如果选择了Serotype，筛选符合条件的数据
  if (selectedSerotype.value) {
    data = data.filter((item: any) => item.serotype === selectedSerotype.value);
  }
  // 如果选择了Top N，限制返回的数据条数
  if (topN.value) {
    data = data.slice(0, topN.value); // 截取前N条数据
  }
  console.log('filteredSeroMLSTData:', data);
  return data;
});

// 添加一个重置筛选功能
const resetFilters = () => {
  selectedSerotype.value = null; // 清空Serotype选择
  topN.value = null; // 清空Top N选择
};

// 添加这个 watch
// 监听yearRange变化

async function reloadData() {
  sessionStorage.clear();
  const [newStart, newEnd]=yearRange.value;
  await fetchCountryData(newStart.getFullYear(), newEnd.getFullYear());
}

watch(
  () => yearRange.value,
  async ([newStart, newEnd]) => {
    if (newStart && newEnd) {
      await fetchCountryData(newStart.getFullYear(), newEnd.getFullYear());
    }
  },
  { immediate: true, deep: true }
);

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