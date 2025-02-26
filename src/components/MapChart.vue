<template>
  <div>
    <div v-if="isMapDataEmpty" class="not-found-message">Not Found</div>
    <div v-else :key="chartKey" ref="chart" class="word-cloud-container" :style="{ width: '100%', height: '400px' }"></div>
  </div>
</template>



<script lang="ts" setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue';
import * as echarts from 'echarts/core';
import { MapChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  GeoComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { EChartsType } from 'echarts/core';
import axios from 'axios';

// Register the necessary components
echarts.use([
  TitleComponent,
  TooltipComponent,
  VisualMapComponent,
  GeoComponent,
  MapChart,
  CanvasRenderer
]);

const props = defineProps({
  mapData: {
    type: Object,
    required: true
  },
  enableClick: {
    type: Boolean,
    default: false
  }
});

const chart = ref<HTMLDivElement | null>(null);
let chartInstance: EChartsType | null = null;
const chartKey = ref(0);

const loadMapData = async () => {
  const response = await axios.get('/worldmap.json');
  return response.data;
};

const initChart = async () => {
  if (chartInstance) {
    chartInstance.dispose();
  }
  if (chart.value) {
    chartInstance = echarts.init(chart.value);

    const geoJson = await loadMapData();
    echarts.registerMap('world', geoJson);

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c}'
      },
      visualMap: {
        min: 0,
        max: Math.max(...Object.values(props.mapData)),
        left: 'right',
        top: 'bottom',
        text: ['High', 'Low'],
        calculable: true
      },
      geo: {
        map: 'world',
        roam: true,
        label: {
          show: false, // Do not show labels by default
          emphasis: {
            show: true // Show labels on hover
          }
        },
        itemStyle: {
          borderColor: '#000',
          borderWidth: 1
        }
      },
      series: [{
        type: 'map',
        map: 'world',
        geoIndex: 0,
        data: Object.entries(props.mapData).map(([name, value]) => ({ name, value }))
      }]
    };
    
    chartInstance.setOption(option);

    if (props.enableClick) {
      chartInstance.on('click', (params) => {
        if (params.componentType === 'series') {
          alert(`You clicked on: ${params.name}`);
        }
      });
    }
  }
};

const isMapDataEmpty = computed(() => {
  return Object.keys(props.mapData).length === 0;
});

watch(() => props.mapData, async (newData) => {
  if (Object.keys(newData).length > 0) {
    chartKey.value += 1; // Force re-render
    await nextTick(); // Wait for the DOM to update
    await initChart();
  }
});

onMounted(async () => {
  if (!isMapDataEmpty.value) {
    await initChart();
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

.not-found-message {
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

