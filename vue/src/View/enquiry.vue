<template>
  <el-container>
    <el-main>
      <!--------------------------------------------------First  layer-------------------------------------------------->

      <el-row type="flex">
        <el-col :span="24">
          <el-page-header @back="goBack" title="Back">              
          </el-page-header>
          <h2>Serotype Case Study</h2>
        </el-col>
      </el-row>
      <!--------------------------------------------------second  layer Date Picker----------------------------------->

      <el-row type="flex">
        <el-col :span="16">
            <tr>
              <td class="label-cell">
                <b>Date</b>
              </td>
              <td>
                <el-checkbox v-model="useDateFilter">Use Date Filter</el-checkbox>
              </td>
            </tr>
            <tr v-if="useDateFilter">
              <td></td>
              <td class="input-cell">
                <el-date-picker
                  v-model="year"
                  type="daterange"
                  unlink-panels
                  range-separator="To"
                  start-placeholder="Start Date"
                  end-placeholder="End Date"
                  :shortcuts="shortcuts"/>
              </td>
            </tr>
  <!--------------------------------------------------Title -------------------------------------------------->

            <tr v-if="eventType == 'All' || eventType == ''">
              <td class="label-cell">
                <b>ID</b>
              </td>
              <td class="input-cell">
                <el-input
                  placeholder="Please enter the ID"
                  v-model="ID"
                  style="width: 100%;"
                  @keyup.enter="newSubmit"
                ></el-input>
              </td>
            </tr>
 <!--------------------------------------------------pmcID-------------------------------------------------->

            <tr v-if="eventType == 'All' || eventType == ''">
              <td class="label-cell">
                <b>Source</b>
              </td>
              <td class="input-cell">
                <el-input
                  placeholder="Please enter the source"
                  v-model="Source"
                  style="width: 100%;"
                  @keyup.enter="newSubmit"
                ></el-input>
              </td>
            </tr>
 <!--------------------------------------------------   source    -------------------------------------------------->

            <tr v-if="eventType == 'All' || eventType == ''">
              <td class="label-cell">
                <b>Brand</b>
              </td>
              <td class="input-cell">
                <el-input
                  placeholder="Please enter the brand"
                  v-model="Brand"
                  style="width: 100%;"
                  @keyup.enter="newSubmit"
                ></el-input>
              </td>
            </tr>
 <!--------------------------------------------------   Keyword  -------------------------------------------------->
<!-- ASSAY information set
            <tr v-if="eventType == 'All' || eventType == ''">
              <td class="label-cell">
                <b>Keyword</b>
              </td>
              <td class="input-cell">
                <el-input
                  placeholder="Please enter the Keyword"
                  v-model="keyword"
                  style="width: 100%;"
                  @keyup.enter="newSubmit"
                ></el-input>
              </td>
            </tr> -->
 <!--------------------------------------------------   Country   -------------------------------------------------->

            <tr v-if="eventType == 'All' || eventType == ''">
              <td class="label-cell">
                <b>Country</b>
              </td>
              <td class="input-cell">
                <el-input
                  placeholder="Please enter the country"
                  v-model="Country"
                  style="width: 100%;"
                  @keyup.enter="newSubmit"
                ></el-input>
              </td>
            </tr>
 <!--------------------------------------------------    Serotype     -------------------------------------------------->

            <tr v-if="eventType == 'All' || eventType == ''">
              <td class="label-cell">
                <b>Serotype</b>
              </td>
              <td class="input-cell">
                <el-input
                  placeholder="Please enter the serotype"
                  v-model="Serotype"
                  style="width: 100%;"
                  @keyup.enter="newSubmit"
                ></el-input>
              </td>
            </tr>
        </el-col>
      </el-row>
      <!--------------------------------------------------Third  layer Enquire------------------------------------------>

      <el-row type="flex">
        <el-col :span="24">
          <el-button type="primary" color="#626aef" style="padding: 10px" @click="newSubmit()">Enquire</el-button>
        </el-col>
      </el-row>

      <!--------------------------------------------------Fourth  layer-------------------------------------------------->

      <el-row type="flex">
        <el-col :span="24">
          <div v-if="loading">Loading...</div>
          <ul v-else>
            <li v-for="(hit, index) in hits" :key="index">
              {{ hit[0] }} - {{ hit[21] }} <!-- Assuming index 0 for title and 6 for pub_year -->
            </li>
          </ul>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

 <!--------------------------------------------------Script  layer-------------------------------------------------->

 <script lang="ts" setup>
 

 //1.22 Larry： 添加了onMounted 
import { ref, getCurrentInstance,onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { saveSearchResultsToSessionStorage, getSearchResultsFromSessionStorage} from '../splitStorage'
const instance = getCurrentInstance();
if (!instance) {
  throw new Error("Failed to get current instance");
}

const apiUrl = (instance.proxy as any).$apiHost;
if (!apiUrl) {
  throw new Error("API URL not found");
}


console.log('API URL:', apiUrl);

const goBack = () => {
  console.log('go back');
  router.back();
};

const router = useRouter();
const eventType = ref('All');
const ID = ref('');
const Source = ref('');
const Brand = ref('');
const Country = ref('');
const Serotype = ref('');
//1.22 Larry： 添加了MLST字段
const MLST = ref('');

const useDateFilter = ref(false);

// [-----assay information ----]
// const title = ref('');   
// const pmcID = ref('');
// const source = ref('');
// const keyword = ref('');
// const country = ref('');
// const serotype = ref('');

const hits = ref<any[]>([]);
const loading = ref(false);

const year = ref<[Date, Date]>([
  new Date('1900-01-01'),
  new Date('2024-12-31')
]);

const newSubmit = async () => {
  loading.value = true;
  try {
    const params = {

      
      ID: ID.value,
      Brand: Brand.value,
      Source: Source.value,
      Country: Country.value,
      Serotype: Serotype.value,
      //1.22 Larry： 添加了MLST字段
      MLST: MLST.value,

      //[---- assay information ---]
      // title: title.value,
      // pmcid: pmcID.value,
      // source: source.value,
      // country: country.value,
      // serotype: serotype.value,
      // keyword: keyword.value,

    };
    
    console.log('Sending request with params:', params);

    const response = await axios.get(`${apiUrl}/api/search/`, {
      params: params
    });
    // console.log('Responses:', response.data.results);
    let results: any[] = response.data.results;
    // console.log('Processed Results:', results);

    for (let hit of results) {
      if (hit[2]==='1900-01-01') {
        hit[2]='NaT';
      }
    }

    if (year.value && useDateFilter.value===true) {
      const [start, end] = year.value;
      results = results.filter((hit: any[]) => {
        if (hit[2]==='NaT') {
          return false;
        }
        const pubYear = new Date(hit[2]).getFullYear();
        return pubYear >= start.getFullYear() && pubYear <= end.getFullYear();
      });
    }
    // -----assay information set----
    // if (year.value) {
    //   const [start, end] = year.value;
    //   results = results.filter((hit: any[]) => {
    //     const pubYear = new Date(hit[6]).getFullYear();
    //     return pubYear >= start.getFullYear() && pubYear <= end.getFullYear();
    //   });
    // }
    
    hits.value = results;
    // console.log("hit",hits.value)
    sessionStorage.clear();
    // sessionStorage.setItem('searchResults', JSON.stringify(hits.value));
    saveSearchResultsToSessionStorage(results)
    // console.log('Stored results in sessionStorage:', sessionStorage.getItem('searchResults'));

    router.push({ name: 'result-ListView' });
    console.log('Navigation to /list triggered');
  } catch (error) {
    console.error('Error fetching data:', error);
  } finally {
    loading.value = false;
  }
};

// const saveSearchResultsToSessionStorage = (results: any[]) => {
//   for (let i = 0; i < results.length; i+=500) {
//     if (i+100 > results.length) {
//       sessionStorage.setItem(`searchResults${i}`, JSON.stringify(results.slice(i, results.length)));
//     } else {
//     sessionStorage.setItem(`searchResults${i}`, JSON.stringify(results.slice(i, i+100)));
//     }
//   }
// }

// const getSearchResultsFromSessionStorage = () => {
//   const results: any[] = [];
//   let i=0;
//   while (sessionStorage.getItem(`searchResults${i}`)) {
//     results.push(...JSON.parse(sessionStorage.getItem(`searchResults${i}`)!));
//     i+=500;
//   }
//   return results;
// }
const shortcuts = [
  {
    text: 'This month',
    value: [new Date(), new Date()],
  },
  {
    text: 'This year',
    value: () => {
      const end = new Date();
      const start = new Date(new Date().getFullYear(), 0);
      return [start, end];
    },
  },
  {
    text: 'Last 6 months',
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setMonth(start.getMonth() - 6);
      return [start, end];
    },
  },
];

//1.22 Larry：
// 监听路由参数并处理 keyword
onMounted(() => {
  const currentRoute = router.currentRoute.value; // 获取当前路由
  const serovarkeyword = currentRoute.query.keyword as string; // 获取 serovar 参数
  const sourceKeyword = currentRoute.query.source as string; // 获取 source 参数
  const mlstKeyword = currentRoute.query.mlst as string; // 获取 mlst 参数
  if (serovarkeyword) {
    Serotype.value = serovarkeyword; // 将 keyword 填入 Serotype 字段
    console.log(`Received keyword: ${serovarkeyword}`);
    newSubmit(); // 自动触发查询
  }
  if (sourceKeyword) {
    Source.value = sourceKeyword; // 将关键词填充到 Source 字段
    console.log(`Received source: ${sourceKeyword}`);
    newSubmit(); // 自动触发查询
  }
  if (mlstKeyword) {
    MLST.value = mlstKeyword; // 填充到 MLST 字段
    console.log(`Received MLST: ${mlstKeyword}`);
    newSubmit(); // 自动触发查询
  }
});

</script>


 <!--------------------------------------------------style layer-------------------------------------------------->
 
<style scoped>
p {
  padding: 2px 0;
}

div {
  padding: 5px 0px;
}
input {
  width: 98%;
  height: 30px;
  display: block;
  margin: 2px 0;
}

.inputText {
  text-align: center;
  padding: 0 0 0 10%;
}

.el-col {
  align-self: center;
  justify-content: flex-end;
}

h2 {
  text-align: center; /* Centering the h2 text */
  margin-top: -20px; /* Adjust this value to move the h2 up */
}
.el-page-header {
  padding-top: 0; /* Remove padding at the top if any */
  margin-top: -15px;
}

.styled-table {
  width: 100%;
  text-align: left;
}

.label-cell {
  width: 25%;
  padding-left: 10px;
  padding-right: 100px; /* Add space between label and input */
}

.input-cell {
  width: 75%;
}
</style>
