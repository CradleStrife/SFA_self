<template>
    <div v-loading="isLoading" class="word-cloud-container" :style="{ width: '100%', height: '400px' }">
      <div ref="wordCloud" style="width: 100%; height: 100%;"></div>
    </div>
  </template>
  
  <script lang="ts" setup>
  import { ref, onMounted, watch } from 'vue';
  import * as echarts from 'echarts';
  import 'echarts-wordcloud';
  //1/22:添加路由依赖
  import { useRouter } from 'vue-router';
  
  const props = defineProps<{
    processdata: { name: string, value: number }[]
  }>();
  
  const isLoading = ref(true);
  const wordCloud = ref<HTMLDivElement | null>(null);
  
  const colorPalette = ['#FF5733', '#33FF57', '#3357FF', '#FF33A6', '#A633FF', '#FFC300', '#581845', '#DAF7A6', '#FF5733', '#C70039'];
  let colorIndex = 0;
  
  const getNextColor = () => {
    colorIndex = (colorIndex + 1) % colorPalette.length;
    return colorPalette[colorIndex];
  };
  
  const isDataEmpty = (data: { name: string, value: number }[]) => {
    return data.length === 0 || data.every(item => !item.name || item.value === 0);
  };
  
  const getChartData = () => {
    if (isDataEmpty(props.processdata)) {
      console.log('Data is empty, displaying "Not Found"');
      return [{ name: 'Not Found', left: 'center', top: 'center', value: 100, textStyle: { fontSize: 19, color: '#131111' } }];
    }
    return props.processdata;
  };

  //1/22:实现handleKeywordClick方法
  const handleKeywordClick = (keyword: string) => {
    let reqBody;
    if (sessionStorage.getItem('index_type') && sessionStorage.getItem('index_type') !== 'local') {
      reqBody={
        name: "enquiry_assay",
        query: { keyword },
      }
    } else {
      reqBody={
        name: 'enquiry', // 路由名称
        query: { keyword }, // 传递关键字作为查询参数
      }
      console.log("request body:",reqBody);
    }
    router.push(reqBody);
  };

  //1/22:引入路由依赖
  const router = useRouter();


  
  const initChart = () => {
    if (wordCloud.value) {
      const startTime = performance.now();
   
      const chart = echarts.init(wordCloud.value);
      isLoading.value = true;
      const option = {
        tooltip: {},
        animation: false,
        series: [{
          type: 'wordCloud',
          keepAspect: true,
          gridSize: 10,
          sizeRange: [20, 30],
          rotationRange: [0, 20],
          shape: 'circle',
          width: '100%',
          height: '100%',
          drawOutOfBound: true,
          layoutAnimation: false,
          textStyle: {
            fontWeight: 'bold',
            color: () => getNextColor()
          },
          emphasis: {
            focus: 'self',
            textStyle: {
              textShadowBlur: 10,
            }
          },
          data: getChartData()
        }]
      };
      chart.setOption(option);

        // 1/22:添加点击事件监听
      chart.on('click', (params) => {
        if (params.name) {
          handleKeywordClick(params.name); // 传递点击的关键字
        }
      });

      const endTime = performance.now();
      console.log(`WordCloud render time: ${endTime - startTime} ms`);
  
      isLoading.value = false; // Hide the loading state
    }
  };
  
  onMounted(() => {
    initChart();
  });
  
  watch(() => props.processdata, () => {
    initChart();
  });
  </script>
  
  <style scoped>
  .word-cloud-container {
    border: 1px solid rgb(211, 208, 208);
    border-radius: 5px;
    padding: 10px;
    box-sizing: border-box;
    width: 100%;
    height: 600px; /* Adjusted height to utilize more space */
  }
  </style>
  