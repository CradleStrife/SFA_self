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
import { TitleComponent, TooltipComponent, VisualMapComponent, GeoComponent } from 'echarts/components';
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
  CanvasRenderer,
]);

interface TooltipParams {
  name: string;
  value: [number, number]; // [country name, value]
}

interface CountryEntry {
  name: string;
  value: number;
}
interface MapEntry {
  name: string;  // Country name
  value: number; // Value or count for the country
}
const props = defineProps<{
  mapData: Record<string, number>; // Country names with values
  enableClick?: boolean;
}>();

const chart = ref<HTMLDivElement | null>(null);
let chartInstance: EChartsType | null = null;
const chartKey = ref(0);

// Load the world map data (GeoJSON)
const loadMapData = async () => {
  const response = await axios.get('/worldmap.json'); // Load worldmap.json
  return response.data;
};

// Initialize the chart
const initChart = async () => {
  if (chartInstance) {
    chartInstance.dispose(); // Dispose of any previous instances
  }
  if (chart.value) {
    chartInstance = echarts.init(chart.value);

    const geoJson = await loadMapData(); // Load worldmap.json
    echarts.registerMap('world', geoJson); // Register the map
    console.log('Map Registered:', geoJson);

    // Prepare data from country names with values
    const mapData = Array.isArray(props.mapData) 
  ? props.mapData.map(({ name, value }: CountryEntry) => ({
      name,
      value,
    }))
  : [];

    console.log('Map Data:', mapData);

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: (params: TooltipParams) => `${params.name}: ${params.value[1]}`, // Tooltip shows country name and value
      },
      geo: {
        map: 'world', // Use the registered world map
        roam: true, // Enable zooming and panning
        label: {
          show: false,
          emphasis: {
            show: true,
          },
        },
        itemStyle: {
          borderColor: '#000', // Set map border color
          borderWidth: 1,
        },
      },
      visualMap: {
        min: 0,
        max: Math.max(...Object.values(props.mapData)), // Scale based on data values
        left: 'right',
        top: 'bottom',
        text: ['High', 'Low'],
        calculable: true,
      },
      series: [
        {
          name: 'Countries',
          type: 'map', // Map type
          map: 'world', // Use the registered world map
          data: mapData, // Pass the country data
          emphasis: {
            itemStyle: {
              areaColor: '#FF6F61', // Highlight color
            },
          },
        },
      ],
    };

    chartInstance.setOption(option);

    console.log('ECharts Option Set:', option);

    if (props.enableClick) {
      chartInstance.on('click', (params) => {
        if (params.componentType === 'series') {
          alert(`You clicked on: ${params.name}`);
        }
      });
    }
  }
};

// Computed property to check if map data is empty
const isMapDataEmpty = computed(() => {
  return Object.keys(props.mapData).length === 0;
});
console.log('Is Map Data Empty:', isMapDataEmpty.value);

// Watch for changes in map data and reinitialize the chart
watch(() => props.mapData, async (newData) => {
  console.log('Received mapData in map_assay.vue:', newData);
  if (Object.keys(newData).length > 0) {
    chartKey.value += 1; // Force re-render
    await nextTick(); // Wait for DOM to update
    await initChart();
  }
});

// Initialize the chart when the component is mounted
onMounted(async () => {
  console.log('map_assay component mounted');
  if (!isMapDataEmpty.value) {
    await initChart();
  }
});
</script>

<style scoped>
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
  font-weight: bold;
}
</style>
