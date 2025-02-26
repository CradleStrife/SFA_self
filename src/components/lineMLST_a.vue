<template>
    <div class="custom-table-container">
      <el-row>
        <div class="filter-container">
          <el-select v-model="topN" placeholder="Select Top N" style="width: 200px;">
            <el-option v-for="option in topNOptions" :key="option" :label="`Top ${option}`" :value="option"></el-option>
          </el-select>
        </div>
      </el-row>
  
      <el-row class="charts-container">
        <!-- lineMLST.vue component section -->
        <el-col :span="12" class="chart-col">
          <div class="filter-container">
            <el-select v-model="selectedPeriodMLST" placeholder="Select Period" style="width: 200px; margin-right: 10px;">
              <el-option label="Monthly" value="monthly"></el-option>
              <el-option label="6-Monthly" value="six_monthly"></el-option>
              <el-option label="Yearly" value="yearly"></el-option>
            </el-select>
            <el-autocomplete
              v-model="selectedMLST"
              :fetch-suggestions="querySearchMLST"
              placeholder="Enter MLST"
              style="width: 200px; margin-right: 10px;"
            ></el-autocomplete>
            <el-autocomplete
              v-model="selectedCountry"
              :fetch-suggestions="querySearchCountry"
              placeholder="Enter Country"
              style="width: 200px; margin-right: 10px;"
            ></el-autocomplete>
            <el-autocomplete
              v-model="selectedSource"
              :fetch-suggestions="querySearchSource"
              placeholder="Enter Source"
              style="width: 200px;"
            ></el-autocomplete>
            <el-button @click="addCombination" style="width: 80px; margin-left: 6px;">Add</el-button>
            <el-button @click="resetChart" style="width: 80px; margin-left: 6px;">Reset</el-button>
          </div>
          <v-chart :option="chartOptionMLST" autoresize style="height: 500px;"></v-chart>
        </el-col>
  
        <!-- lineMLSTall.vue component section -->
        <el-col :span="12" class="chart-col">
          <div class="filter-container">
            <div style="height: 36.8px;"></div>
          </div>
          <v-chart :option="chartOptionMLSTAll" autoresize style="height: 500px;"></v-chart>
          <!-- 移动后的图例模块 -->
          <div class="legend-container">
            <el-scrollbar style="height: 150px;">
              <div v-for="group in filteredGroupsMLSTAll" :key="group" class="legend-item">
                <span :style="{ color: colorMapMLSTAll[group] }">■</span> {{ group }}: {{ nonCumulativeTotals[group] }} <!-- Non-cumulative total for legend -->
              </div>
            </el-scrollbar>
          </div>
        </el-col>
      </el-row>
    </div>
  </template>
  
  <script lang="ts" setup>
  import { ref, computed, watch } from 'vue';
  import dayjs from 'dayjs';
  import * as echarts from 'echarts';
  import VChart from 'vue-echarts';
  import { use } from 'echarts/core';
  import { CanvasRenderer } from 'echarts/renderers';
  import { LineChart } from 'echarts/charts';
  import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components';
  
  use([
    CanvasRenderer,
    LineChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent
  ]);
  
  interface MlsttypeData {
    "mlst": string;
    count: number;
    country: string;
    source: string;
    pub_years: string;
  }
  
  interface ProcessedData {
    period: string;
    mlst: string;
    country: string;
    source: string;
    total_count: number;
  }
  
  const props = defineProps<{
    mlsttypeData: MlsttypeData[];
  }>();
  
  const topN = ref<number>(10); // Default to top 10
  const topNOptions = [10, 20, 30]; // Options for the top N dropdown
  
  const selectedPeriodMLST = ref<string>('yearly');
  const selectedMLST = ref<string>('');
  const selectedCountry = ref<string>('');
  const selectedSource = ref<string>('');
  const combinations = ref<Array<{ mlst: string; country: string; source: string }>>([]);
  const selectedPeriodMLSTAll = ref<string>('yearly');
  
  let nonCumulativeTotals: { [key: string]: number } = {}; // Non-cumulative totals
  
  const addCombination = () => {
    if (selectedMLST.value && selectedCountry.value && selectedSource.value) {
      combinations.value.push({
        mlst: selectedMLST.value,
        country: selectedCountry.value,
        source: selectedSource.value,
      });
      selectedMLST.value = ''; // Clear input fields
      selectedCountry.value = '';
      selectedSource.value = '';
    }
  };
  
  const resetChart = () => {
    combinations.value = []; // Clear all combinations
    chartOptionMLST.value = {}; // Reset the chart option to empty
  };
  
  // Process data with cumulative and non-cumulative logic
  const processData = (data: MlsttypeData[], period: string): ProcessedData[] => {
  nonCumulativeTotals = {}; // Reset the non-cumulative totals each time
  const periodData: { [key: string]: ProcessedData } = {};
  const cumulativeTotals: { [key: string]: number } = {};
  const cumulativeData: ProcessedData[] = []; // Initialize cumulativeData here

  // Get all unique years
  const allYears = Array.from(new Set(data.map(item => dayjs(item.pub_years.toString()).year()))).sort((a, b) => a - b);

  // Process data
  data.forEach((item: MlsttypeData) => {
    const mlst = item["mlst"] ?? "undefined";
    const count = item.count ?? 0;
    const country = item.country ?? "undefined";
    const source = item.source ?? "undefined";
    const pub_years = item.pub_years ?? "undefined";

    if (typeof pub_years !== 'string') {
      console.error('pub_years is not a string:', pub_years);
      return; // Skip this item if pub_years is not a string
    }

    const date = dayjs(pub_years);
    let periodKey = '';

    switch (period) {
      case 'monthly':
        periodKey = date.format('YYYY-MM');
        break;
      case 'six_monthly':
        const month = date.month();
        const halfYear = month < 6 ? 'H1' : 'H2';
        periodKey = `${date.year()}-${halfYear}`;
        break;
      case 'yearly':
      default:
        periodKey = date.year().toString();
        break;
    }

    const compositeKey = `${mlst}-${country}-${source}`;

    // Non-cumulative totals for the legend
    if (!nonCumulativeTotals[compositeKey]) {
      nonCumulativeTotals[compositeKey] = 0;
    }
    nonCumulativeTotals[compositeKey] += count;

    // Cumulative totals for the graph
    if (!cumulativeTotals[compositeKey]) {
      cumulativeTotals[compositeKey] = 0;
    }
    cumulativeTotals[compositeKey] += count;

    // Store cumulative totals in periodData
    periodData[`${compositeKey}-${periodKey}`] = {
      period: periodKey,
      mlst: mlst,
      country: country,
      source: source,
      total_count: cumulativeTotals[compositeKey],
    };
  });

  // Sorting and accumulating data
  Object.keys(cumulativeTotals).forEach(compositeKey => {
    let lastTotal = 0;
    let firstAppearance = true;  // Track the first appearance of the series

    allYears.forEach(year => {
      const periodKey = year.toString();
      const fullKey = `${compositeKey}-${periodKey}`;

      // If there is data for this year, add it to the cumulative count
      if (periodData[fullKey]) {
        lastTotal = periodData[fullKey].total_count; // Update the last total to the current year's count
      }

      // Push the result (either the new total or the carried-over total)
      cumulativeData.push({
        period: periodKey,
        mlst: periodData[fullKey]?.mlst || compositeKey.split('-')[0],
        country: periodData[fullKey]?.country || compositeKey.split('-')[1],
        source: periodData[fullKey]?.source || compositeKey.split('-')[2],
        total_count: lastTotal,  // Carry forward the last total if no new data
      });
    });
  });

  return cumulativeData;
};



  const uniqueGroups = computed(() => {
  const groups = new Set<string>();
  props.mlsttypeData.forEach(item => {
    groups.add(`${item["mlst"] ?? "undefined"}-${item.country ?? "undefined"}-${item.source ?? "undefined"}`);
  });
  return Array.from(groups);
});
  const processedDataMLST = computed(() => {
    return processData(props.mlsttypeData, selectedPeriodMLST.value);
  });
  
  const processedDataMLSTAll = computed(() => {
    return processData(props.mlsttypeData, selectedPeriodMLSTAll.value);
  });
  
  const filteredGroupsMLSTAll = computed(() => {
    const counts: { [key: string]: number } = {};
    processedDataMLSTAll.value.forEach(item => {
      const groupKey = `${item.mlst}-${item.country}-${item.source}`;
      if (!counts[groupKey]) {
        counts[groupKey] = 0;
      }
      counts[groupKey] += nonCumulativeTotals[groupKey] || 0;
    });
  
    const sortedGroups = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);
    return sortedGroups.slice(0, topN.value);
  });
  
  const chartDataMLST = computed(() => {
    return processedDataMLST.value;
  });
  
  const chartDataMLSTAll = computed(() => {
    return processedDataMLSTAll.value;
  });
  
  const groupCountsMLST = computed(() => {
    const counts: { [key: string]: number } = {};
    chartDataMLST.value.forEach(item => {
      const groupKey = `${item.mlst}-${item.country}-${item.source}`;
      if (!counts[groupKey]) {
        counts[groupKey] = 0;
      }
      counts[groupKey] += item.total_count;
    });
    return counts;
  });
  
  const groupCountsMLSTAll = computed(() => {
    const counts: { [key: string]: number } = {};
    chartDataMLSTAll.value.forEach(item => {
      const groupKey = `${item.mlst}-${item.country}-${item.source}`;
      if (!counts[groupKey]) {
        counts[groupKey] = 0;
      }
      counts[groupKey] += item.total_count;
    });
    return counts;
  });
  
  const colorMapMLST = ref<{ [key: string]: string }>({});
  const chartOptionMLST = ref({});
  const colorMapMLSTAll = ref<{ [key: string]: string }>({});
  const chartOptionMLSTAll = ref({});
  
  watch(
    [combinations, selectedPeriodMLST, chartDataMLST], // Watch these dependencies
    ([newCombinations, newPeriod, newData]) => {
      if (newCombinations.length === 0 || newData.length === 0) {
        chartOptionMLST.value = {
          title: {
            text: 'MLST Data (Individual)',
          },
          xAxis: {
            type: 'category',
            data: [], // 空数据
          },
          yAxis: {
            type: 'value',
          },
          series: [],
        };
        return;
      }
  
      const periods = Array.from(new Set(newData.map(item => item.period))); // Get unique periods
  
      const seriesData = newCombinations.map(combination => {
        const groupKey = `${combination.mlst}-${combination.country}-${combination.source}`;
        const color = echarts.color.random(); // Generate a random color for each combination
        colorMapMLST.value[groupKey] = color;
  
        return {
          name: groupKey,
          type: 'line',
          itemStyle: { color },
          data: periods.map(period => {
            const item = newData.find(data => 
              data.period === period && 
              data.mlst === combination.mlst && 
              data.country === combination.country && 
              data.source === combination.source
            );
            return item ? item.total_count : 0;
          }),
        };
      });
  
      chartOptionMLST.value = {
        title: {
          text: 'MLST Data (Individual)',
        },
        tooltip: {
          trigger: 'item',
          formatter: function (params: any) {
            return `${params.seriesName}: ${params.data}`;
          }
        },
        xAxis: {
          type: 'category',
          data: periods,
        },
        yAxis: {
          type: 'value',
        },
        series: seriesData,
      };
    },
    { deep: true, immediate: true }
  );
  
  
  
  watch([chartDataMLSTAll, selectedPeriodMLSTAll, topN], (newValues) => {
    const [newData] = newValues;
  
    if (newData.length === 0) return;
  
    const periods = Array.from(new Set(newData.map(item => item.period))); // Get unique periods
    const groups = Object.keys(groupCountsMLSTAll.value).sort((a, b) => groupCountsMLSTAll.value[b] - groupCountsMLSTAll.value[a]);
    const topGroups = groups.slice(0, topN.value);
    const seriesData = topGroups.map((group, index) => {
      const color = echarts.color.random(); // Generate a random color for each group
      colorMapMLSTAll.value[group] = color;
      return {
        name: group,
        type: 'line',
        itemStyle: { color },
        data: periods.map(period => {
          const item = newData.find(data => data.period === period && `${data.mlst}-${data.country}-${data.source}` === group);
          return item ? item.total_count : 0;
        }),
      };
    });
  
    chartOptionMLSTAll.value = {
      title: {
        text: 'MLST Data (Overall)',
      },
      tooltip: {
        trigger: 'item',
        formatter: function (params: any) {
          return `${params.seriesName}: ${params.data}`;
        }
      },
      xAxis: {
        type: 'category',
        data: periods,
      },
      yAxis: {
        type: 'value',
      },
      series: seriesData,
    };
  }, { immediate: true });
  
  const querySearchMLST = (queryString: string, cb: (results: any[]) => void) => {
    const results = uniqueGroups.value
      .map(group => group.split('-')[0])
      .filter(mlst => mlst.toLowerCase().includes(queryString.toLowerCase()));
    cb([...new Set(results)].map(mlst => ({ value: mlst })));
  };
  
  const querySearchCountry = (queryString: string, cb: (results: any[]) => void) => {
    const results = uniqueGroups.value
      .map(group => group.split('-')[1])
      .filter(country => country.toLowerCase().includes(queryString.toLowerCase()));
    cb([...new Set(results)].map(country => ({ value: country })));
  };
  
  const querySearchSource = (queryString: string, cb: (results: any[]) => void) => {
    const results = uniqueGroups.value
      .map(group => group.split('-')[2])
      .filter(source => source.toLowerCase().includes(queryString.toLowerCase()));
    cb([...new Set(results)].map(source => ({ value: source })));
  };
  </script>
  
  <style scoped>
.custom-table-container {
  margin: 20px;
}
.filter-container {
  margin-bottom: 20px;
  justify-content: center;
  width: 100%; /* Ensure the content is centered within its container */
  display: flex;
}
.charts-container {
  display: flex;
  justify-content: space-between;
}
.chart-col {
  display: flex;
  flex-direction: column;
}
.legend-container {
  margin-top: 20px;
  width: 100%;
}
.legend-item {
  margin-right: 10px;
  text-align: left;
  width: 100%;
}
</style>
  