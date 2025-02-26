<template>
    <div class="custom-table-container">
      <div class="filter-container">
        <el-select v-model="selectedPeriod" placeholder="Select Period" style="width: 200px;">
          <el-option label="Yearly" value="yearly"></el-option>
        </el-select>
      </div>
      <v-chart :option="chartOption" autoresize style="height: 500px;"></v-chart>
      <div class="legend-container">
        <el-scrollbar style="height: 150px;">
          <div v-for="group in uniqueGroups" :key="group" class="legend-item">
            <span :style="{ color: colorMap[group] }">■</span> {{ group }}: {{ groupCounts[group] }}
          </div>
        </el-scrollbar>
      </div>
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
  
  const topN = ref<number | undefined>(undefined); // To store the selected top N value
  const topNOptions = [10, 20, 30]; // Options for the top N dropdown
  
  interface MlsttypeData {
    "mlst ": string;
    count: number;
    country: string;
    source: string;
    pub_years: string;
  }
  
  interface ProcessedData {
    year: string;
    mlst: string;
    country: string;
    source: string;
    total_count: number;
  }
  
  const props = defineProps<{
    mlsttypeData: MlsttypeData[];
  }>();
  
  const selectedPeriod = ref<string>('yearly');
  
  const processData = (data: MlsttypeData[]): ProcessedData[] => {
    const periodData: { [key: string]: ProcessedData } = {};
  
    data.forEach((item: MlsttypeData) => {
      const mlst = item["mlst "] ?? "undefined";
      const count = item.count ?? 0;
      const country = item.country ?? "undefined";
      const source = item.source ?? "undefined";
      const pub_years = item.pub_years ?? "undefined";
  
      if (typeof pub_years !== 'string') {
        console.error('pub_years is not a string:', pub_years);
        return;  // Skip this item if pub_years is not a string
      }
  
      const date = dayjs(pub_years);
      const yearKey = date.year().toString(); // Extract only the year
  
      const compositeKey = `${yearKey}-${mlst}-${country}-${source}`;
  
      if (!periodData[compositeKey]) {
        periodData[compositeKey] = {
          year: yearKey,
          mlst: mlst,
          country: country,
          source: source,
          total_count: 0
        };
      }
  
      periodData[compositeKey].total_count += count;
    });
  
    // Sort in ascending order
    const result: ProcessedData[] = Object.values(periodData).sort((a, b) => {
      const dateA = dayjs(a.year);
      const dateB = dayjs(b.year);
      return dateA.diff(dateB);
    });
  
    return result;
  };
  
  const uniqueGroups = computed(() => {
    const groups = new Set<string>();
    props.mlsttypeData.forEach(item => {
      groups.add(`${item["mlst "] ?? "undefined"}-${item.country ?? "undefined"}-${item.source ?? "undefined"}`);
    });
    return Array.from(groups);
  });
  
  const processedData = computed(() => {
    return processData(props.mlsttypeData);
  });
  
  const chartData = computed(() => {
    return processedData.value;
  });
  
  const groupCounts = computed(() => {
    const counts: { [key: string]: number } = {};
    chartData.value.forEach(item => {
      const groupKey = `${item.mlst}-${item.country}-${item.source}`;
      if (!counts[groupKey]) {
        counts[groupKey] = 0;
      }
      counts[groupKey] += item.total_count;
    });
    return counts;
  });
  
  const colorMap = ref<{ [key: string]: string }>({});
  const chartOption = ref({});
  
  watch(chartData, (newData) => {
    if (newData.length === 0) return;
  
    const years = Array.from(new Set(newData.map(item => item.year))); // Get unique years
    const seriesData = uniqueGroups.value.map((group, index) => {
      const color = echarts.color.random(); // Generate a random color for each group
      colorMap.value[group] = color;
      return {
        name: group,
        type: 'line',
        itemStyle: { color },
        data: years.map(year => {
          const item = newData.find(data => data.year === year && `${data.mlst}-${data.country}-${data.source}` === group);
          return item ? item.total_count : 0;
        }),
      };
    });
  
    chartOption.value = {
      title: {
        text: 'MLST Data',
      },
      tooltip: {
      trigger: 'item',
      formatter: function (params: any) {
        return `${params.seriesName}: ${params.data}`;
      }
     },
      xAxis: {
        type: 'category',
        data: years,
      },
      yAxis: {
        type: 'value',
      },
      series: seriesData,
    };
  }, { immediate: true });
  </script>
  
  <style scoped>
  .custom-table-container {
    margin: 20px;
  }
  .filter-container {
    margin-bottom: 20px;
  }
  .legend-container {
    margin-top: 20px;
    display: flex;
    flex-wrap: wrap;
  }
  .legend-item {
    margin-right: 10px;
  }
  </style>
  