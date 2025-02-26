<template>
  <el-container>
    <el-main>
      <el-row type="flex">
        <el-col :span="24">
          <el-page-header @back="goBack" title="Back"></el-page-header>
        </el-col>
      </el-row>

      <!-------------------------------------- Start of layer  ------------------------------------------->
      <el-row type="flex">
        <el-col :span="4" :offset="6">
          <b>Year Range</b>
        </el-col>
        <!-------------------------------------- Year Range here  ------------------------------------------->
        <el-col :span="8">
          <!-- Start Year Input -->
          <el-input
            v-model.number="yearRange[0]"
            placeholder="Start Year"
            type="number"
            :min="1900"
            :max="new Date().getFullYear()"
            style="width: 120px; margin-right: 10px;"
            @input="onYearRangeChange"
          ></el-input>
          <span>to</span>
          <!-- End Year Input -->
          <el-input
            v-model.number="yearRange[1]"
            placeholder="End Year"
            type="number"
            :min="1900"
            :max="new Date().getFullYear()"
            style="width: 120px; margin-left: 10px;"
            @input="onYearRangeChange"
          ></el-input>
        </el-col>
      </el-row>

      <!-------------------------------------- First layer Serovar ------------------------------------------->
      <h1>Trend Analysis</h1>
      <el-row type="flex">
        <el-col :span="10" :offset="1">
          <sero_ID_a :seroData="seroid" :start-year="yearRange[0]" :end-year="yearRange[1]" />
        </el-col>
        <el-col :span="10" :offset="1">
          <mlst_ID_a :mlstData="mlstid" :start-year="yearRange[0]" :end-year="yearRange[1]" />
        </el-col>
      </el-row>

      <!-------------------------------------- Second layer MLST ------------------------------------------->
      <el-row type="flex">
        <el-col :span="24">
          <h1>MLSTs with the Highest Frequency of Count</h1>
          <Bar_MLST_a :chartData="mlstid" />
        </el-col>
      </el-row>

      <!-------------------------------------- Second layer ------------------------------------------->
      <el-row type="flex">
        <el-col :span="24" >
          <h2>Top Occurrence Serotype</h2>
          <linesero_a :serotypeData="tableData" />
        </el-col>
      </el-row>

      <!-------------------------------------- third layer ------------------------------------------->
      <el-row type="flex">
        <el-col :span="24" >
          <h2>Top Occurrence MLST</h2>
          <lineMLST_a :mlsttypeData="mlsttableData" />
        </el-col>
      </el-row>

      <!-------------------------------------- Fourth layer ------------------------------------------->
      <el-row type="flex">
        <el-col :span="10" :offset="2">
          <h3>{{ `Top ${topNsero || 'N'} Serotype` }}</h3>
          <el-select v-model="topNsero" placeholder="Select Top N" style="width: 200px; margin-bottom: 20px;">
            <el-option v-for="n in topNOptions" :key="n" :label="`Top ${n}`" :value="n" />
          </el-select>
          <WordCloud :processdata="filteredSerovarData" />
        </el-col>
        <el-col :span="10">
          <h3>{{ `Top ${topNmlst || 'N'} MLST` }}</h3>
          <el-select v-model="topNmlst" placeholder="Select Top N" style="width: 200px; margin-bottom: 20px;">
            <el-option v-for="n in topNOptions" :key="n" :label="`Top ${n}`" :value="n" />
          </el-select>
          <WordCloud :processdata="filteredMLSTData" />
        </el-col>
      </el-row>

      <!-------------------------------------- Before MLST Table  ------------------------------------------->
      <el-row type="flex" align="middle" justify="space-between">
          <!-- Serotype 筛选框 -->
          <el-col :span="8">
            <el-input
              v-model="selectedSerotype"
              placeholder="Filter by Serotype"
              clearable
            />
          </el-col>

          <!-- Top N 选择框 -->
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

          <!-- 重置按钮 -->
          <el-col :span="4">
            <el-button type="primary" @click="resetFilters">Reset All Filters</el-button>
          </el-col>
        </el-row>

      <!-------------------------------------- MLST Table here  ------------------------------------------->
      <el-row type="flex">
        <el-col :span="24">
          <p>seroMLSTData: {{ seroMLSTData }}</p> <!-- 显示调试数据 -->
          <p v-if="!seroMLSTData.length">No Data Available</p>
          <TableChart :seroMLSTData="filteredSeroMLSTData" />
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
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

const mlstid = ref<mlstid[]>([]);
const seroword = ref<Seroword[]>([]);
const seroMLSTData = computed(() => mlsttableData.value);
const seroid = ref<seroid[]>([]);
const mlstword = ref<mlstword[]>([]);
const tableData = ref([]);
const topNmlst = ref<number>(10);
const topNOptions = [10, 20, 30];
const topNsero = ref<number>(10);
const yearRange = ref<[number, number]>([1900, 2024]); // Default years
const mlsttableData = ref([]);
// 新增变量
const selectedSerotype = ref<string | null>(null); // 用户选择的Serotype
const topN = ref<number | null>(null); // 用户选择的Top N

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
  try {
    const response = await axios.get(`${apiUrl}/api/search/`, {
      params: {
        start_date: startYear,
        end_date: endYear,
        required_data: [
          'serotype',
          'mlst_a',
          'process_mlst_tabledata_a',
          'process_country_sourcedata_a',
          'process_ID_MLSTdata_a',
          'process_ID_serodata_a',
        ].join(','),
        index: 'assay_data',
      },
    });

    // 打印日志
    console.log('API Response:', response.data); 
    console.log('Full API Response:', JSON.stringify(response.data, null, 2));
    console.log('MLST Table Data (from API):', response.data.process_mlst_tabledata_a);
    console.log('Assigned to mlsttableData:', mlsttableData.value);
    console.log('Original Data:', seroMLSTData.value); // 打印原始数据
    console.log('Filtered Data:', filteredSeroMLSTData.value); // 打印筛选后的数据


    // 处理响应数据
    seroword.value = response.data.serotype || [];
    mlstword.value = response.data.mlst_a || [];
    seroid.value = response.data.process_ID_serodata_a || [];
    mlstid.value = response.data.process_ID_MLSTdata_a || [];
    tableData.value = response.data.process_country_sourcedata_a || [];
    mlsttableData.value = response.data.process_mlst_tabledata_a || [];
    
    // 打印各字段的状态
    console.log('Serotype Data:', seroword.value);
    console.log('MLST Data:', mlstword.value);
    console.log('Process ID Serodata:', seroid.value);
    console.log('Process ID MLSTdata:', mlstid.value);
    console.log('Country Source Data:', tableData.value);
    console.log('MLST Table Data:', mlsttableData.value);
  } catch (error) {
    console.error('Error fetching country data:', error);
  }
};



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
const onYearRangeChange = () => {
  const [startYear, endYear] = yearRange.value;
  if (startYear <= endYear) {
    fetchCountryData(startYear, endYear);
  } else {
    console.error('Invalid year range: Start year must be less than or equal to end year.');
  }
};

// Fetch data on initial load
onMounted(async () => {
  const [startYear, endYear] = yearRange.value;
  await fetchCountryData(startYear, endYear);  // Send default year range to the backend
});

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
  return data;
});

// 添加一个重置筛选功能
const resetFilters = () => {
  selectedSerotype.value = null; // 清空Serotype选择
  topN.value = null; // 清空Top N选择
};

</script>

<style scoped>
.hidden-select {
  display: none;
}
</style>
