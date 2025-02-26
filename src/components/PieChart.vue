<template>
    <div ref="chart" :style="{ width: '100%', height: '400px' }"></div>
  </template>
  
  <script lang="ts" setup>
  import { ref, onMounted, watch } from 'vue';
  import * as echarts from 'echarts';
  
  const props = defineProps<{
    data: { name: string; value: number }[];
  }>();
  console.log(props.data)
  const chart = ref<HTMLDivElement | null>(null);
  
  const initChart = () => {
  if (chart.value) {
    const myChart = echarts.init(chart.value);
    const option = {
      title: {
        text: 'Country Distribution',
        left: 'center',
      },
      tooltip: {
        trigger: 'item',
      },
      legend: {
        type: 'scroll', // Enable scroll for the legend
        orient: 'vertical',
        left: 'left',
        top: 20, // Add some top margin
        bottom: 20, // Add some bottom margin for the scroll bar
      },
      series: [
        {
          name: 'Countries',
          type: 'pie',
          radius: '70%',
          data: props.data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
          },
        },
      ],
    };
    myChart.setOption(option);
  }
};

  
  onMounted(() => {
    initChart();
  });
  
  watch(() => props.data, initChart, { deep: true });
  </script>
  
  <style scoped>
  .chart {
    width: 100%;
    height: 400px;
  }
  </style>
  