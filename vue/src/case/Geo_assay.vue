<template>
    <el-container>
      <el-main>
        <el-row type="flex">
          <el-col :span="24">
            <el-page-header @back="goBack" title="Back"></el-page-header>
          </el-col>
        </el-row>
        <!-------------------------------------- Start of layer  ------------------------------------------->
        <el-row type="flex">
          <el-col :span="20" :offset="2">
            <b>Geographical_Distribution</b>
          </el-col>
        </el-row>
        <select v-model="selected_index" @change="fetchCountryData">
          <option v-for="option in index_options" :value="option">{{ option }}</option>
        </select>
        <button @click="fetchCountryData">Reload Data</button>
        <!-------------------------------------- Second layer  ------------------------------------------->
        <el-row type="flex" style="left: 20%;">
          <el-checkbox v-model="useDateFilter">Use Date Filter</el-checkbox>
        </el-row>
        <el-row type="flex">
          <el-col :span="6" :offset="2">
            <el-date-picker
              v-if="useDateFilter"
              v-model="dateRange"
              type="daterange"
              unlink-panels
              range-separator="To"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              :shortcuts="shortcuts"
            />
          </el-col>
          <el-col :span="6">
            <el-autocomplete
              v-model="newSerotype"
              :fetch-suggestions="querySearchSerotype"
              placeholder="Enter Serotype"
              @select="addSerotype"
              clearable
              >
              <template #append>
                <el-button @click="addSerotype">Add</el-button>
              </template>
            </el-autocomplete>
            <div>
              <el-tag
                v-for="item in serotype"
                :key="item"
                closable
                @close="removeSerotype(item)"
                style="margin: 5px 0"
              >
                {{ item }}
              </el-tag>
            </div>
          </el-col>
          <el-col :span="2">
            <el-select v-model="serotypeConditionType" placeholder="Select Serotype Condition Type">
              <el-option label="Match" value="must"></el-option>
              <el-option label="Mix" value="should"></el-option>
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-autocomplete
              v-model="newSource"
              :fetch-suggestions="querySearchSource"
              placeholder="Enter Source"
              @select="addSource"
              clearable
               >
              <template #append>
                <el-button @click="addSource">Add</el-button>
              </template>
            </el-autocomplete>
            <div>
              <el-tag
                v-for="item in source"
                :key="item"
                closable
                @close="removeSource(item)"
                style="margin: 5px 0"
              >
                {{ item }}
              </el-tag>
            </div>
          </el-col>
          <el-col :span="2">
            <el-select v-model="sourceConditionType" placeholder="Select Source Condition Type">
              <el-option label="Match" value="must"></el-option>
              <el-option label="Mix" value="should"></el-option>
            </el-select>
          </el-col>
        </el-row>
  
        <!------------------------------------ World Map  ------------------------------------------->
       <el-row type="flex">
          <el-col :span="24">
            <div style="display: inline-block;"></div>
            <!-- <pre>{{ mapChartData }}</pre> -->
            <MapChart :mapData="mapChartData" />
          </el-col>
          <div style="clear:both"></div>
      </el-row>
       <!-------------------------------------- Pie Chart  ------------------------------------------->
      <el-row type="flex">
        <el-col :span="24">
          <PieChart :data="countryDataForPieChart" />
        </el-col>
      </el-row>
      </el-main>
   </el-container>
  </template>
  
  <script lang="ts" setup>
  import { ref, onMounted, watch, getCurrentInstance } from 'vue';
  import { useRouter } from 'vue-router';
  import axios from 'axios';
  import MapChart from '../components/MapChart.vue';
  import PieChart from '../components/PieChart.vue';
  import {assay_types,sub_types,index_names} from '../index_names';
  
  const router = useRouter();
  const dateRange = ref<[Date, Date] | undefined>(undefined);
  const mapChartData = ref({});
  const serotype = ref<string[]>([]);
  const newSerotype = ref<string>('');
  const serotypesuggest = ref<string[]>([]); // Suggestions for serotypes
  const source = ref<string[]>([]);
  const newSource = ref<string>('');
  const sourcesuggest = ref<string[]>([]); // Suggestions for sources
  const countryDataForPieChart = ref<{ name: string; value: number }[]>([]);
  const serotypeConditionType = ref<string>('must');
  const sourceConditionType = ref<string>('must');

  const index_options=ref(assay_types);
  const selected_index=ref(index_options.value[0])

  const useDateFilter=ref(false)

  const instance = getCurrentInstance();
  if (!instance) {
    throw new Error("Failed to get current instance");
  }
  
  const apiUrl = (instance.proxy as any).$apiHost;
  if (!apiUrl) {
    throw new Error("API URL not found");
  }
  
  const goBack = () => {
    console.log('go back');
    router.back();
  };
    // Function to log performance timing
    const logPerformance = (startTime: number, message: string) => {
          const endTime = performance.now();
          console.log(`${message}: ${endTime - startTime} ms`);
        };
        
  const fetchCountryData = async () => {
      const [startDate, endDate] = dateRange.value || [];
      try {
        const startDateParam = (useDateFilter.value===true && startDate) ? startDate.toISOString().split('T')[0] : '1000-01-01';
        const endDateParam = (useDateFilter.value===true && endDate) ? endDate.toISOString().split('T')[0] : '3000-01-01';
        const serotypeParam = serotype.value.join(',');
        const sourceParam = source.value.join(',');

        const requiredData = ['geo_location_a', 'serotype', 'isolate_source'].join(',');
        // console.log("assay_index_name", index_names[selected_index.value]["assay"])
        const index_name = index_names[selected_index.value]["assay"]
        const response = await axios.get(`${apiUrl}/api/search/`, {
          params: {
            start_date: startDateParam,
            end_date: endDateParam,
            serotype: serotypeParam,
            isolate_source: sourceParam,
            serotype_condition: serotypeConditionType.value,
            source_condition: sourceConditionType.value,
            required_data: requiredData,
            index: "assay",
            assay_index_name: index_name,
          }
        });
        console.log('API Response:', response.data);
        serotypesuggest.value = response.data.serotype || [];
        sourcesuggest.value = response.data.isolate_source || [];
        mapChartData.value= response.data["geo_location_a"] || {};
        // Extract lat/lon data for the map
        console.log("aa",mapChartData)
        console.log("bb",mapChartData.value)
        countryDataForPieChart.value = Object.entries(mapChartData.value).map(([name, value]) => ({
          name,
          value: Number(value),
        }));
        console.log("countryDataForPieChart",countryDataForPieChart.value);
      } catch (error) {
        console.error('Error fetching country data:', error);
      }
    };

  
  // Serotype autocomplete suggestion function
  const querySearchSerotype = (queryString: string, cb: (results: any[]) => void) => {
    const results = serotypesuggest.value
      .filter(serotype => typeof serotype.name === 'string' && serotype.name.toLowerCase().includes(queryString.toLowerCase()));
    cb(results.map(serotype => ({ value: serotype.name })));
  };
  
  const querySearchSource = (queryString: string, cb: (results: any[]) => void) => {
    const results = sourcesuggest.value
      .filter(isolate_source => typeof isolate_source.name === 'string' && isolate_source.name.toLowerCase().includes(queryString.toLowerCase()));
    cb(results.map(isolate_source => ({ value: isolate_source.name })));
  };
  
  
  const addSerotype = () => {
    if (newSerotype.value && !serotype.value.includes(newSerotype.value)) {
      serotype.value.push(newSerotype.value);
      newSerotype.value = '';
      fetchCountryData();
    }
  };
  
  const removeSerotype = (item: string) => {
    const index = serotype.value.indexOf(item);
    if (index !== -1) {
      serotype.value.splice(index, 1);
      fetchCountryData();
    }
  };
  
  const addSource = () => {
    if (newSource.value && !source.value.includes(newSource.value)) {
      source.value.push(newSource.value);
      newSource.value = '';
      fetchCountryData();
    }
  };
  
  const removeSource = (item: string) => {
    const index = source.value.indexOf(item);
    if (index !== -1) {
      source.value.splice(index, 1);
      fetchCountryData();
    }
  };
  
  watch([dateRange, serotype, source, serotypeConditionType, sourceConditionType], async () => {
    await fetchCountryData();
  }, { deep: true });
  
  onMounted(async () => {
    try {
      const startYear = 1900;
      const endYear = 2024;
      dateRange.value = [new Date(`${startYear}-01-01`), new Date(`${endYear}-12-31`)] as [Date, Date];
      const startTime = performance.now();
      await fetchCountryData();
      logPerformance(startTime, "Initial data fetch and processing time");
  
    } catch (error) {
      console.error('Error fetching available years:', error);
    }
  });
  
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
  </script>
  