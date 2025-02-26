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
      <!-- linesero.vue component section -->
      <el-col :span="12" class="chart-col">
        <div class="filter-container">
          <el-select v-model="selectedPeriodLinesero" placeholder="Select Period" style="width: 200px; margin-right: 10px;">
            <el-option label="Monthly" value="monthly"></el-option>
            <el-option label="6-Monthly" value="6-monthly"></el-option>
            <el-option label="Yearly" value="yearly"></el-option>
          </el-select>
          <el-autocomplete
            v-model="selectedSerotypeLinesero"
            :fetch-suggestions="querySearchSerotype"
            placeholder="Serotype"
            style="width: 200px; margin-right: 10px;"
          ></el-autocomplete>
          <el-autocomplete
            v-model="selectedCountryLinesero"
            :fetch-suggestions="querySearchCountry"
            placeholder="Country"
            style="width: 200px; margin-right: 10px;"
          ></el-autocomplete>
          <el-autocomplete
            v-model="selectedSourceLinesero"
            :fetch-suggestions="querySearchSource"
            placeholder="Source"
            style="width: 200px;"
          ></el-autocomplete>
          <el-button @click="addCombination" style="width: 80px; margin-left: 6px;">Add</el-button>
          <el-button @click="resetChart" style="width: 80px; margin-left: 6px;">Reset</el-button>
        </div>
        <v-chart :option="chartOptionLinesero" autoresize style="height: 500px;"></v-chart>
      </el-col>

      <!-- lineseroall.vue component section -->
      <el-col :span="12" class="chart-col">
        <div class="filter-container">
          <div style="height: 36.8px;"></div>
        </div>
        <v-chart :option="chartOptionLineseroAll" autoresize style="height: 500px;"></v-chart>
        <!-- 移动后的图例模块 -->
        <div class="legend-container">
          <el-scrollbar style="height: 150px;">
            <div v-for="group in filteredGroupsLineseroAll" :key="group.serotype + group.country + group.source" class="legend-item">
              <span :style="{ color: colorMapLineseroAll[group.serotype + '-' + group.country + '-' + group.source] }">■</span> 
              {{ group.serotype }} - {{ group.country }} - {{ group.source }}: {{ group.total_count }}
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

interface SerotypeData {
  serotype: string;
  count: number;
  country: string;
  source: string;
  pub_years: string;
}

interface ProcessedData {
  period: string;
  serotype: string;
  country: string;
  source: string;
  total_count: number;
}

const props = defineProps<{
  serotypeData: SerotypeData[];
}>();

const topN = ref<number>(10); // Default to top 10
const topNOptions = [10, 20, 30]; // Options for the top N dropdown

const selectedPeriodLinesero = ref<string>('yearly');
const selectedSerotypeLinesero = ref<string>('');
const selectedCountryLinesero = ref<string>('');
const selectedSourceLinesero = ref<string>('');
const combinations = ref<Array<{ serotype: string; country: string; source: string }>>([]);

const addCombination = () => {
  if (selectedSerotypeLinesero.value && selectedCountryLinesero.value && selectedSourceLinesero.value) {
    combinations.value.push({
      serotype: selectedSerotypeLinesero.value,
      country: selectedCountryLinesero.value,
      source: selectedSourceLinesero.value,
    });
    selectedSerotypeLinesero.value = ''; // Clear input fields
    selectedCountryLinesero.value = '';
    selectedSourceLinesero.value = '';
  }
};

const resetChart = () => {
  combinations.value = []; // Clear all combinations
  chartOptionLinesero.value = {}; // Reset the chart option to empty
};

const selectedPeriodLineseroAll = ref<string>('yearly');

let nonCumulativeTotals: { [key: string]: number } = {}; // Declare with 'let'
// For storing the non-cumulative totals

const processData = (data: SerotypeData[], period: string): ProcessedData[] => {
// Reset nonCumulativeTotals at the beginning of each processing cycle
nonCumulativeTotals = {}; // Ensure it resets for each time range

const periodData: { [key: string]: ProcessedData } = {};
const cumulativeTotals: { [key: string]: number } = {};

// Extract unique years from the dataset and sort them
const allYears = Array.from(new Set(data.map(item => dayjs(item.pub_years.toString()).year()))).sort((a, b) => a - b);

// Step 1: Aggregate data by period and combination
data.forEach((item: SerotypeData) => {
  const { serotype, count, country, source, pub_years } = item;

  const serotypeItem = serotype || 'Unknown';
  const countryItem = country || 'Unknown';
  const sourceItem = source || 'Unknown';
  const date = dayjs(pub_years.toString());

  let periodKey = '';
  switch (period) {
    case 'monthly':
      periodKey = date.format('YYYY-MM');
      break;
    case '6-monthly':
      const month = date.month();
      const halfYear = month < 6 ? 'H1' : 'H2';
      periodKey = `${date.year()}-${halfYear}`;
      break;
    case 'yearly':
    default:
      periodKey = date.year().toString();
      break;
  }

  // Use serotype-country-source combination as composite key
  const compositeKey = `${serotypeItem}-${countryItem}-${sourceItem}`;

  // Step 2: Increment non-cumulative total for the legend
  if (!nonCumulativeTotals[compositeKey]) {
    nonCumulativeTotals[compositeKey] = 0;
  }
  nonCumulativeTotals[compositeKey] += count; // Non-cumulative total count for the legend

  // Step 3: Increment cumulative count for the period
  if (!cumulativeTotals[compositeKey]) {
    cumulativeTotals[compositeKey] = 0;
  }
  cumulativeTotals[compositeKey] += count;

  // Step 4: Store the cumulative total for the current period
  periodData[`${compositeKey}-${periodKey}`] = {
    period: periodKey,
    serotype: serotypeItem,
    country: countryItem,
    source: sourceItem,
    total_count: cumulativeTotals[compositeKey], // Cumulative count for the line graph
  };
});

// Step 5: Sort and accumulate the data for the line graph (same as current behavior)
const cumulativeData: ProcessedData[] = [];
Object.keys(cumulativeTotals).forEach(compositeKey => {
  let lastTotal = 0;
  allYears.forEach(year => {
    const periodKey = year.toString();
    const fullKey = `${compositeKey}-${periodKey}`;

    if (periodData[fullKey]) {
      lastTotal = periodData[fullKey].total_count;
    }

    cumulativeData.push({
      period: periodKey,
      serotype: periodData[fullKey]?.serotype || compositeKey.split('-')[0],
      country: periodData[fullKey]?.country || compositeKey.split('-')[1],
      source: periodData[fullKey]?.source || compositeKey.split('-')[2],
      total_count: lastTotal,
    });
  });
});

return cumulativeData;
};






const uniqueGroups = computed(() => {
  const groups: Array<{ serotype: string; country: string; source: string }> = [];
  const groupKeys = new Set<string>();
  props.serotypeData.forEach(item => {
    const key = `${item.serotype}-${item.country}-${item.source}`;
    if (!groupKeys.has(key)) {
      groupKeys.add(key);
      groups.push({
        serotype: item.serotype,
        country: item.country,
        source: item.source,
      });
    }
  });
  return groups;
});


const processedDataLinesero = computed(() => {
  return processData(props.serotypeData, selectedPeriodLinesero.value);
});

const processedDataLineseroAll = computed(() => {
  return processData(props.serotypeData, selectedPeriodLineseroAll.value);
});

const filteredGroupsLinesero = computed(() => {
  const counts: Array<{ serotype: string; country: string; source: string; total_count: number }> = [];

  processedDataLinesero.value.forEach(item => {
    const existing = counts.find(group =>
      group.serotype === item.serotype &&
      group.country === item.country &&
      group.source === item.source
    );
    if (existing) {
      existing.total_count += item.total_count;
    } else {
      counts.push({
        serotype: item.serotype,
        country: item.country,
        source: item.source,
        total_count: item.total_count,
      });
    }
  });

  const filtered = counts.filter(group => {
    return (
      (!selectedSerotypeLinesero.value || group.serotype.includes(selectedSerotypeLinesero.value)) &&
      (!selectedCountryLinesero.value || group.country.includes(selectedCountryLinesero.value)) &&
      (!selectedSourceLinesero.value || group.source.includes(selectedSourceLinesero.value))
    );
  });

  const sortedGroups = filtered.sort((a, b) => b.total_count - a.total_count);
  return sortedGroups.slice(0, topN.value);
});


const filteredGroupsLineseroAll = computed(() => {
  const counts: Array<{ serotype: string; country: string; source: string; total_count: number }> = [];

  processedDataLineseroAll.value.forEach(item => {
    const existing = counts.find(group =>
      group.serotype === item.serotype &&
      group.country === item.country &&
      group.source === item.source
    );
    if (existing) {
      existing.total_count += item.total_count;
    } else {
      counts.push({
        serotype: item.serotype,
        country: item.country,
        source: item.source,
        total_count: item.total_count,
      });
    }
  });

  // 调整 nonCumulativeTotals 的处理方式
  counts.forEach(group => {
    const key = `${group.serotype}-${group.country}-${group.source}`;
    group.total_count = nonCumulativeTotals[key] || 0;
  });

  const sortedGroups = counts.sort((a, b) => b.total_count - a.total_count);
  return sortedGroups.slice(0, topN.value);
});


const chartDataLinesero = computed(() => {
  return processedDataLinesero.value;
});

const chartDataLineseroAll = computed(() => {
  return processedDataLineseroAll.value;
});

const groupCountsLinesero = computed(() => {
  const counts: { [key: string]: number } = {};
  chartDataLinesero.value.forEach(item => {
    const groupKey = `${item.serotype}-${item.country}-${item.source}`;
    if (!counts[groupKey]) {
      counts[groupKey] = 0;
    }
    counts[groupKey] += item.total_count;
  });
  return counts;
});

const groupCountsLineseroAll = computed(() => {
  const counts: { [key: string]: number } = {};
  chartDataLineseroAll.value.forEach(item => {
    const groupKey = `${item.serotype}-${item.country}-${item.source}`;
    if (!counts[groupKey]) {
      counts[groupKey] = 0;
    }
    counts[groupKey] += item.total_count;
  });
  return counts;
});

const colorMapLinesero = ref<{ [key: string]: string }>({});
const chartOptionLinesero = ref({});
const colorMapLineseroAll = ref<{ [key: string]: string }>({});
const chartOptionLineseroAll = ref({});

watch(
[combinations, selectedPeriodLinesero, chartDataLinesero], // Watch these dependencies
([newCombinations, newPeriod, newData]) => {
  if (newCombinations.length === 0 || newData.length === 0) {
    chartOptionLinesero.value = {
      title: {
        text: 'Serotype Data (Individual)',
      },
      xAxis: {
        type: 'category',
        data: [],
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
    const groupKey = `${combination.serotype}-${combination.country}-${combination.source}`;
    const color = echarts.color.random(); // Generate a random color for each combination
    colorMapLinesero.value[groupKey] = color;
    
    return {
      name: groupKey,
      type: 'line',
      itemStyle: { color },
      data: periods.map(period => {
        const item = newData.find(data => 
          data.period === period && 
          data.serotype === combination.serotype && 
          data.country === combination.country && 
          data.source === combination.source
        );
        return item ? item.total_count : 0; // Use accumulated count for this period
      }),
    };
  });
  console.log("Series Data for Chart:", seriesData);
  chartOptionLinesero.value = {
    title: {
      text: 'Serotype Data (Individual)',
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




watch([chartDataLineseroAll, selectedPeriodLineseroAll, topN], (newValues) => {
const [newData] = newValues;

if (newData.length === 0) return;

const periods = Array.from(new Set(newData.map(item => item.period)));

const groupCountsArray = filteredGroupsLineseroAll.value;

const seriesData = groupCountsArray.map((group, index) => {
  const groupName = `${group.serotype}-${group.country}-${group.source}`;
  const color = echarts.color.random();
  colorMapLineseroAll.value[groupName] = color;
  return {
    name: groupName,
    type: 'line',
    itemStyle: { color },
    data: periods.map(period => {
      const item = newData.find(data =>
        data.period === period &&
        data.serotype === group.serotype &&
        data.country === group.country &&
        data.source === group.source
      );
      return item ? item.total_count : 0;
    }),
  };
});

chartOptionLineseroAll.value = {
  title: {
    text: 'Serotype Data (Overall)',
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


const querySearchSerotype = (queryString: string, cb: (results: any[]) => void) => {
  const results = uniqueGroups.value
    .map(group => group.serotype)
    .filter(serotype => serotype.toLowerCase().includes(queryString.toLowerCase()));
  cb([...new Set(results)].map(serotype => ({ value: serotype })));
};

const querySearchCountry = (queryString: string, cb: (results: any[]) => void) => {
  const results = uniqueGroups.value
    .map(group => group.country)
    .filter(country => country.toLowerCase().includes(queryString.toLowerCase()));
  cb([...new Set(results)].map(country => ({ value: country })));
};

const querySearchSource = (queryString: string, cb: (results: any[]) => void) => {
  const results = uniqueGroups.value
    .map(group => group.source)
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


