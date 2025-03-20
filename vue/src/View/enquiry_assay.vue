<template>
    <el-container>
      <el-main>
        <!--------------------------------------------------First  layer-------------------------------------------------->
  
        <el-row type="flex">
          <el-col :span="24">
            <el-page-header @back="goBack" title="Back">              
            </el-page-header>
            <h2>Isolates</h2>
            <select v-model="selected_index">
              <option v-for="option in index_options" :value="option">{{ option }}</option>
            </select>
          </el-col>
        </el-row>
        <!--------------------------------------------------second  layer Date Picker----------------------------------->
  
        <el-row type="flex">
          <el-col :span="16">
              <tr>
                <td class="label-cell">
                  <b>Date Filter</b>
                  
                </td>
                <td>
                  <el-checkbox v-model="useDateFilter">Use Date Filter</el-checkbox>
                </td>
                
              </tr>
              <tr>
                <td></td>
                <td class="input-cell" v-if="useDateFilter">
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
   <!--------------------------------------------------pmcID-------------------------------------------------->
  
              <tr v-if="eventType == 'All' || eventType == ''">
                <td class="label-cell">
                  <b>pmcID</b>
                </td>
                <td class="input-cell">
                  <el-input
                    placeholder="Please enter the pmcID"
                    v-model="pmcid"
                    style="width: 100%;"
                    @keyup.enter="newSubmit"
                  ></el-input>
                </td>
              </tr>
  <!--------------------------------------------------PMID -------------------------------------------------->
  
              <tr v-if="eventType == 'All' || eventType == ''">
                <td class="label-cell">
                  <b>Isolate ID</b>
                </td>
                <td class="input-cell">
                  <el-input
                    placeholder="Please enter the Isolate ID"
                    v-model="isolate_id"
                    style="width: 100%;"
                    @keyup.enter="newSubmit"
                  ></el-input>
                </td>
              </tr> 
   <!---------------------------------------------------  Isolate source  -------------------------------------------------->
   <!--------------------------------------------------  Isolate source  -------------------------------------------------->
  
              <tr v-if="eventType == 'All' || eventType == ''">
                <td class="label-cell">
                  <b>Isolate Source</b>
                </td>
                <td class="input-cell">
                  <el-input
                    placeholder="Please enter the Source"
                    v-model="isolate_source"
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
   <!--------------------------------------------------  ISOLATE Country   -------------------------------------------------->
  
              <tr v-if="eventType == 'All' || eventType == ''">
                <td class="label-cell">
                  <b>Isolate country</b>
                </td>
                <td class="input-cell">
                  <el-input
                    placeholder="Please enter the Country"
                    v-model="isolate_country"
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
                    placeholder="Please enter the Serotype"
                    v-model="serotype"
                    style="width: 100%;"
                    @keyup.enter="newSubmit"
                  ></el-input>
                </td>
              </tr>


              <tr v-if="eventType == 'All' || eventType == ''">
                <td class="label-cell">
                  <b>MLST</b>
                </td>
                <td class="input-cell">
                  <el-input
                    placeholder="Please enter the MLST"
                    v-model="mlst"
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
  import { ref, getCurrentInstance,onMounted } from 'vue';
  import axios from 'axios';
  import { useRouter } from 'vue-router';
  import {assay_types,sub_types,index_names} from '../index_names';
  import { use } from 'echarts';
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
  const isolate_id = ref('');
  const pmcid = ref('');
  const isolate_source = ref('');
  const isolate_country = ref('');
  const serotype = ref('');
   
  const mlst=ref('')

  const hits = ref<any[]>([]);
  const loading = ref(false);
  
  const year = ref<[Date, Date]>([
    new Date('1800-01-01'),
    new Date('2024-12-31')
  ]);

  const index_options=ref(assay_types);
  const selected_index=ref(index_options.value[0])
  
  const useDateFilter=ref(false)

  const yearWithinRange=(pubYear:number,start:Date,end:Date)=> {
    return pubYear >= start.getFullYear() && pubYear <= end.getFullYear()
  }

  const newSubmit = async () => {
    loading.value = true;
    try {
      const params = {
        isolate_id: isolate_id.value,
        pmcid: pmcid.value,
        isolate_source: isolate_source.value,
        isolate_country: isolate_country.value,
        serotype: serotype.value,

        mlst: mlst.value,

        index: 'assay_data',
        assay_index_name: index_names[selected_index.value]["assay"],
      };
      
      console.log('Sending request with params:', params);
  
      const response = await axios.get(`${apiUrl}/api/search/`, {
        params: params
      });
      // console.log('Responses:', response.data.results);
      let results: any[] = response.data.results;
      // console.log('Processed Results:', results);
      let pubYear: number;
      for (let hit of results) {
        if (hit.clean_text) {
          delete hit.clean_text;
        }
        if (hit.abstract) {
          delete hit.abstract;
        }
        if (hit.no_isolates_only_assayinformation.isolate_date) {
          pubYear = new Date(hit.no_isolates_only_assayinformation.isolate_date).getFullYear();
          if (pubYear===1850) {
            hit.no_isolates_only_assayinformation.isolate_date = ['NaT'];
          }
        }
        if (hit.isolates_with_linking && Array.isArray(hit.isolates_with_linking)) { 
          try {
            for (const isolate of hit.isolates_with_linking) {
              if (isolate.isolate_date) {
                pubYear = new Date(isolate.isolate_date).getFullYear();
                if (pubYear===1850) {
                  isolate.isolate_date = ['NaT'];
                }
              }
            }
          } catch (e) {
            console.error('Error processing isolates:', e);
          }
        }
      }


      if (year.value && useDateFilter.value===true) {
        const [start, end] = year.value;
        results = results.filter((hit: any) => {
          let pubYear;
          let withinRange=false;
          if (hit.no_isolates_only_assayinformation.isolate_date) {
            if (hit.no_isolates_only_assayinformation.isolate_date==='NaT') {
              return false;
            }
            pubYear = new Date(hit.no_isolates_only_assayinformation.isolate_date).getFullYear();
            // if (pubYear===1850) {
            //   hit.no_isolates_only_assayinformation.isolate_date = ['NaT'];
            //   return false;
            // }
            return yearWithinRange(pubYear, start, end);
          }
          if (hit.isolates_with_linking && Array.isArray(hit.isolates_with_linking)) { 
            try {
              withinRange=false;
              for (const isolate of hit.isolates_with_linking) {
                if (isolate.isolate_date) {
                  if (isolate.isolate_date==='NaT') {
                    continue;
                  }
                  pubYear = new Date(isolate.isolate_date).getFullYear();
                  // if (pubYear===1850) {
                  //   isolate.isolate_date = ['NaT'];
                  //   continue;
                  // }
                  if (yearWithinRange(pubYear, start, end)) {
                    withinRange=true;
                  }
                }
              }
              return withinRange;
            } catch (e) {
              return true;
            }
          }
          return false;
        });
      }
      
      
      // let response2=await axios.get(`${apiUrl}/api/simple_search/`,{
      //   params:{
      //     index_name:index_names[selected_index.value]["SRA"],
      //     field_name:"Filename",
      //     field_value:"DRA000568"
      //   }
      // })
      // results=response2.data.results
      


      hits.value = results;
      sessionStorage.clear();
      // sessionStorage.setItem('searchResults', JSON.stringify(hits.value));
      saveSearchResultsToSessionStorage(results)
      sessionStorage.setItem('index_type',selected_index.value)
      // console.log('Stored results in sessionStorage:', sessionStorage.getItem('searchResults'));
  
      router.push({ name: 'result-ListView_assay' });
      console.log('Navigation to /list triggered');
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      loading.value = false;
    }
  };
  
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

  onMounted(() => {
  const currentRoute = router.currentRoute.value; // 获取当前路由
  const serovarkeyword = currentRoute.query.keyword as string; // 获取 serovar 参数
  const sourceKeyword = currentRoute.query.source as string; // 获取 source 参数
  const mlstKeyword = currentRoute.query.mlst as string; // 获取 mlst 参数

  selected_index.value=sessionStorage.getItem('index_type') || index_options.value[0]
  if (serovarkeyword) {
    serotype.value = serovarkeyword; // 将 keyword 填入 Serotype 字段
    console.log(`Received keyword: ${serovarkeyword}`);
    newSubmit(); // 自动触发查询
  }
  if (sourceKeyword) {
    isolate_source.value = sourceKeyword; // 将关键词填充到 Source 字段
    console.log(`Received source: ${sourceKeyword}`);
    newSubmit(); // 自动触发查询
  }
  if (mlstKeyword) {
    mlst.value = mlstKeyword; // 填充到 MLST 字段
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
  