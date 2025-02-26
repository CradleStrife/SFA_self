import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import '~/styles/index.scss';
import 'uno.css';
import 'element-plus/theme-chalk/src/message.scss';
//1.24 larry 
//add echarts
import VChart from 'vue-echarts';
import * as echarts from 'echarts';
//

const app = createApp(App);

//1.24 larry 
// 注册全局组件 v-chart
app.component('v-chart', VChart);

async function loadConfig() {
  try {
    const response = await fetch('/config.json');
    const config = await response.json();

    const isLocal = location.href.indexOf('localhost') > 0;
    const API_HOST = isLocal ? config.local.API_HOST : config.production.API_HOST;

    console.log(`API HOST: ${API_HOST}`);

    // Set the API_HOST to a global property
    app.config.globalProperties.$apiHost = API_HOST;

    // Now that the config is loaded, mount the app
    app.use(router);
    app.mount('#app');
  } catch (error) {
    console.error('Error loading config.json:', error);
  }
}

loadConfig();
