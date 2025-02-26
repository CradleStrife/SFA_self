<template>
    <div>
      <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <el-select v-model="selectedFilter" placeholder="Select Filter" style="margin-right: 10px;">
          <el-option label="All" value="all"></el-option>
          <el-option label="Top 10" value="above10"></el-option>
        </el-select>
      </div>
      <div ref="chart" v-if="hasData" class="chart-container" :style="{ width: '100%', height: '600px' }"></div>
      <div v-else class="no-data-container">Not Found</div>
      <div v-if="hasData" class="total-label-container">Total MLST: {{ totalMLST }}</div>
    </div>
  </template>
  
  <script lang="ts" setup>
  import { ref, onMounted, watch, computed, nextTick } from 'vue';
  import * as echarts from 'echarts/core';
  import { BarChart } from 'echarts/charts';
  import {
    TitleComponent,
    TooltipComponent,
    GridComponent,
    DatasetComponent,
    TransformComponent
  } from 'echarts/components';
  import { CanvasRenderer } from 'echarts/renderers';
  import { ElSelect, ElOption } from 'element-plus';
  
  // Register the required components
  echarts.use([
    TitleComponent,
    TooltipComponent,
    GridComponent,
    DatasetComponent,
    TransformComponent,
    BarChart,
    CanvasRenderer
  ]);
  
  interface Record {
    ID: string[];
    Date: string[];
    MLST: string[];
  }
  
  const props = defineProps<{
    chartData: Record[];
  }>();
  
  const chart = ref<HTMLElement | null>(null);
  let chartInstance: echarts.ECharts | null = null;
  const selectedFilter = ref('all');
  
  const hasData = computed(() => props.chartData.length > 0);
  
  const normalizeMLST = (mlst: any): string[] => {
    if (Array.isArray(mlst)) {
      if (mlst.length === 1 && Array.isArray(mlst[0])) {
        return mlst[0];
      }
      return mlst;
    }
    return [mlst];
  };
  
  const totalMLST = ref(0);
  
  const filterData = (mlstCounts: { [key: string]: number }) => {
    let filteredData = Object.entries(mlstCounts).sort((a, b) => b[1] - a[1]);
    const counts = Object.values(mlstCounts).sort((a, b) => a - b);
    const median = counts[Math.floor(counts.length / 2)];
    filteredData = filteredData.filter(([mlst, count]) => count >= median);
  
    if (selectedFilter.value === 'above10') {
      filteredData=filteredData.sort((a, b) => b[1] - a[1]).slice(0, 10);
    } else {
      return filteredData;
    }
  
    return filteredData;
  };
  
  const initChart = () => {
  nextTick(() => {
    if (chartInstance) {
      chartInstance.dispose();
    }
    if (chart.value) {
      chartInstance = echarts.init(chart.value);

      // Flatten the MLST data and exclude 'NA' values
      const mlstCounts = props.chartData.reduce((acc: { [key: string]: number }, record: Record) => {
        const normalizedMLST = normalizeMLST(record.MLST);
        normalizedMLST.forEach(mlst => {
          if (mlst !== 'NA') {  // Exclude 'NA' values
            acc[mlst] = (acc[mlst] || 0) + 1;
          }
        });
        return acc;
      }, {});
  
        // Filter the data
        const filteredData = filterData(mlstCounts);
  
        // Prepare data for histogram
        
        const histogramData = filteredData.map(([mlst, count]) => ({ name: mlst, value: count }));
  
        // Update the total MLST count
        totalMLST.value = histogramData.length;
  
        const option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            },
            formatter: function (params: any) {
              const item = histogramData[params[0].dataIndex];
              return `${item.name}: ${item.value}`;
            }
          },
          xAxis: {
            type: 'category',
            data: histogramData.map(item => ''), // Empty labels to hide individual bar labels
            axisLabel: {
              rotate: 0,
              interval: 0,
              textStyle: {
                fontSize: 12,
                fontWeight: 'bold'
              }
            },
            axisLine: {
              lineStyle: {
                color: '#333'
              }
            },
            axisTick: {
              show: false
            }
          },
          yAxis: {
            type: 'value',
            name: 'Count'
          },
          series: [
            {
              name: 'Count',
              type: 'bar',
              data: histogramData.map(item => item.value),
              itemStyle: {
                color: '#5470C6'
              },
              label: {
                show: false // Hide the values above the bars
              }
            }
          ]
        };
        chartInstance.setOption(option);
      }
    });
  };
  
  onMounted(() => {
    if (hasData.value) {
      initChart();
    }
  });
  
  watch([() => props.chartData, selectedFilter], () => {
    if (hasData.value) {
      initChart();
    }
  });
  </script>
  
  <style scoped>
  .chart-container {
    border: 1px solid rgb(211, 208, 208);
    border-radius: 5px;
    padding: 10px;
    box-sizing: border-box;
  }
  .no-data-container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 400px;
    border: 1px solid rgb(211, 208, 208);
    border-radius: 5px;
    color: #131111;
    font-size: 20px;
    font-weight: bold;
  }
  .total-label-container {
    text-align: center;
    font-size: 16px;
    font-weight: bold;
    margin-top: 10px;
  }
  </style>
  