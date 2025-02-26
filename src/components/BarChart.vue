<template>
  <div>
    <div ref="chart" v-if="hasData" class="word-cloud-container" :style="{ width: '100%', height: '400px' }"></div>
    <div v-else class="no-data-container">Not Found</div>
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

const props = defineProps({
  chartData: {
    type: Object,
    required: true
  }
});

const chart = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const hasData = computed(() => Object.keys(props.chartData).length > 0);

const initChart = () => {
  nextTick(() => {
    if (chartInstance) {
      chartInstance.dispose();
    }
    if (chart.value) {
      chartInstance = echarts.init(chart.value);

      let sortedData = Object.entries(props.chartData).sort((a, b) => b[1] - a[1]);

      // Ensure only the top 10 countries are displayed
      // if (sortedData.length > 10) {
      //   sortedData = sortedData.slice(0, 10);
      // }


      // Extract the keys and values from the sorted array
      const sortedKeys = sortedData.map(item => item[0]);
      const sortedValues = sortedData.map(item => item[1]);

      const option = {
        tooltip: {},
        grid: {
          left: 150, // Increase the left margin to make space for labels
        },
        xAxis: {
          type: 'value'
        },
        yAxis: {
          type: 'category',
          data: sortedKeys.reverse(), // Reverse the order to have the highest count on top
          axisLabel: {
            interval: 0, // Show all labels
            formatter: function (value: string) {
              return `{value|${value}}`; // Use rich text formatter
            },
            rich: {
              value: {
                width: 140, // Adjust width to fit long labels
                overflow: 'break', // Ensure word break instead of truncation
                height: 40 // Adjust height if necessary
              }
            }
          }
        },
        series: [{
          type: 'bar',
          data: sortedValues.reverse() // Reverse the order to match the reversed y-axis
        }]
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

watch(() => props.chartData, (newData) => {
  if (hasData.value) {
    initChart();
  }
});
</script>

<style scoped>
/* Add any custom styles here */
.word-cloud-container {
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
  font-weight:'bold';
}
</style>
