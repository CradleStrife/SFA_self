// src/router/index.ts
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import enquiry from '../View/enquiry.vue';
import Home from '../View/Home.vue';
import list from '../case/list.vue';
import trendAnalysis from '../case/trendAnalysis.vue';
import UpdatePage from '../case/UpdatePage.vue'
import GeographicalDistribution from '../case/GeographicalDistribution.vue'
import upload from '../case/upload.vue'
import Geo_assay from '../case/Geo_assay.vue'
import upload_assay from '~/case/upload_assay.vue';
import trend_assay from '~/case/trend_assay.vue';
import enquiry_assay from '~/View/enquiry_assay.vue';
import list_assay from '~/case/list_assay.vue';
import clustering from '../case/clustering.vue';


const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/enquiry',
    name: 'enquiry',
    component: enquiry ,
  },
  {
    path: '/list',
    name: 'result-ListView',
    component: list,
  },
  {
    path: '/list_assay',
    name: 'result-ListView_assay',
    component: list_assay,
  },
  {
    path: '/list/update/',
    name: 'UpdatePage',
    component: UpdatePage,
  },
  {
  path: '/trendAnalysis',
  name: 'trendAnalysis',
  component: trendAnalysis,
  },
  {
    path: '/GeographicalDistribution',
    name: 'GeographicalDistribution',
    component: GeographicalDistribution,
  },
  {
    path: '/upload',
    name: 'upload',
    component: upload,
  },
  {
    path: '/Geo_assay',
    name: 'Geo_assay',
    component: Geo_assay,
},
{
    path: '/enquiry_assay',
    name: 'enquiry_assay',
    component: enquiry_assay,
},
{
    path: '/trend_assay',
    name: 'trend_assay',
    component: trend_assay,
},
{
    path: '/upload_assay',
    name: 'upload_assay',
    component: upload_assay,
},
{
  path: '/clustering',  // 添加新的 clustering 路由
  name: 'clustering',
  component: clustering,
}
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
