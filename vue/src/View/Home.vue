<template>
    <el-container>
        <el-main>

          <!-------------------------------------- Start of layer  ------------------------------------------->
          <el-row type="flex" justify="center">
            <el-col :span="20">
              <el-card class="overview-card" shadow="always">
                <template #header>
                  <h2 class="section-title">Overall View</h2>
              </template>
              <p style="text-align: center;">This section contains overall data visualization and summaries.</p>
              <el-button @click="reloadData" type="primary">Reload Data</el-button>  
            </el-card>
              <div class="section-divider"></div>
            </el-col>
          </el-row>
        <!-------------------------------------- Serovar layer  ------------------------------------------------>
        <el-row type="flex">
            <el-col :span="7" :offset="1">
              <el-card class="overview-card" shadow="always">
              <template #header>
                <h2 class="section-title">Top occurred Serovar</h2>
              </template>
               <el-date-picker
                    v-model="serovarDateRange"
                    type="daterange"
                    unlink-panels
                    range-separator="To"
                    start-placeholder="Start Date"
                    end-placeholder="End Date"
                    :shortcuts="shortcuts"
                    :span ="7"
                   />

                   <el-select v-model="topNsero" placeholder="Select Top N" style="width: 200px; margin-bottom: 20px;">
                     <el-option v-for="n in topNOptions" :key="n" :label="`Top ${n}`" :value="n" />
                  </el-select>
               <wordcloudserotype :processdata="filteredSerovarData" />
              </el-card>
          </el-col>
        <!-------------------------------------- Food layer  ------------------------------------------------>
          <el-col :span="7" :offset="1">
            <el-card class="overview-card" shadow="always">
              <template #header>
                <h2 class="section-title">Top occurred Salmonella detection</h2>
              </template>
                    <el-date-picker
                        v-model="foodDateRange"
                        type="daterange"
                        unlink-panels
                        range-separator="To"
                        start-placeholder="Start Date"
                        end-placeholder="End Date"
                        :shortcuts="shortcuts"
                        :span ="7"
                    />
                    <el-select v-model="topNsource" placeholder="Select Top N" style="width: 200px; margin-bottom: 20px;">
                     <el-option v-for="n in topNOptions" :key="n" :label="`Top ${n}`" :value="n" />
                  </el-select>
                <WordCloud :processdata="filteredsourceData" />
            </el-card>
          </el-col>
         <!-------------------------------------- MLST layer  ------------------------------------------------>
          <el-col :span="7" :offset="1">
            <el-card class="overview-card" shadow="always">
              <template #header>
                <h2 class="section-title">Top occurred MLST</h2>
              </template>
                    <el-date-picker
                        v-model="MLSTRange"
                        type="daterange"
                        unlink-panels
                        range-separator="To"
                        start-placeholder="Start Date"
                        end-placeholder="End Date"
                        :shortcuts="shortcuts"
                        :span ="7"
                    />
                <el-select v-model="topNmlst" placeholder="Select Top N" style="width: 200px; margin-bottom: 20px;">
                    <el-option v-for="n in topNOptions" :key="n" :label="`Top ${n}`" :value="n" />
                </el-select>
                <wordcloudmlst :processdata="filteredMLSTData" />
            </el-card>      
          </el-col>
        </el-row>
      <!-------------------------------------- Sero line layer  ------------------------------------------------>  
      <el-row type="flex" justify="center">
        <el-col :span="20">
          <el-card class="overview-card" shadow="always">
            <template #header>
              <h2 class="section-title">Serotype Trend</h2>
            </template>
            <linesero :serotypeData="tableData" />
          </el-card>
          <div class="section-divider"></div>
        </el-col>
      </el-row>
<!-------------------------------------- MLST line layer  ------------------------------------------------>  
          <el-row type="flex" justify="center">
            <el-col :span="20">
              <el-card class="overview-card" shadow="always">
                <template #header>
                  <h2 class="section-title">MLST Trend</h2>
                </template>
                <lineMLST :mlsttypeData="mlsttableData" />
              </el-card>
              <div class="section-divider"></div>
            </el-col>
          </el-row>
<!-------------------------------------- Table layer  ------------------------------------------------>  
          <el-row type="flex" justify="center">
            <el-col :span="10">
              <el-card class="overview-card" shadow="always">
                <template #header>
                  <h2 class="section-title">Serotype Table</h2>
                </template>
                <serotable :serotypeData="tableData" />
              </el-card>
            </el-col>
            <el-col :span="10">
              <el-card class="overview-card" shadow="always">
                <template #header>
                  <h2 class="section-title">MLST Table</h2>
                </template>
                <mlsttable :mlsttypeData="mlsttableData" />
              </el-card>
            </el-col>
          </el-row>
        </el-main>
    </el-container>
</template>
      <!-------------------------------------- Script layer  ------------------------------------------------>  
      <script lang="ts" setup>
      import { ref, computed, onMounted, watch, getCurrentInstance } from 'vue';
      import axios from 'axios';
      import WordCloud from '../components/wordcloud.vue';
      import wordcloudserotype from '../components/wordcloudserotype.vue';
      import wordcloudmlst from '../components/wordcloudmlst.vue';
      import serotable from '../components/serotable.vue';
      import mlsttable from '../components/mlsttable.vue';
      import linesero from '../components/linesero.vue';
      import lineMLST from '../components/lineMLST.vue';
      import { debounce } from 'lodash';
      
      interface SerotypeData {
        name: string;
        value: number;
      }
      
      interface mlsttypeData {
        name: string;
        value: number;
      }
      
      interface sourcetypeData {
        name: string;
        value: number;
      }
      
      const foodData = ref<sourcetypeData[]>([]);
      const serovarData = ref<SerotypeData[]>([]);
      const MLSTData = ref<mlsttypeData[]>([]);
      const topNsero = ref<number>(10); 
      const topNsource = ref<number>(10);
      const topNmlst = ref<number>(10);
      const topNOptions = [10, 20, 30];
      const serovarDateRange = ref<[Date, Date] | undefined>(undefined);
      const foodDateRange = ref<[Date, Date] | undefined>(undefined);
      const MLSTRange = ref<[Date, Date] | undefined>(undefined);
      const tableData = ref([]);
      const mlsttableData = ref([]);
      
      let isInitialLoad = true;
      
      const instance = getCurrentInstance();
      if (!instance) {
        throw new Error("Failed to get current instance");
      }
      
      const apiUrl = (instance.proxy as any).$apiHost;
      if (!apiUrl) {
        throw new Error("API URL not found");
      }
      
      // Utility functions for session storage
      const storeDataInSessionStorage = (key: string, data: any) => {
        sessionStorage.setItem(key, JSON.stringify(data));
      };

      // Helper function to retrieve data from session storage
      const getDataFromSessionStorage = (key: string) => {
        const data = sessionStorage.getItem(key);
        return data ? JSON.parse(data) : null;
      };
      
      // Function to log performance timing
      const logPerformance = (startTime: number, message: string) => {
        const endTime = performance.now();
        console.log(`${message}: ${endTime - startTime} ms`);
      };
      
      // <!-------------------------------------- serovar layer  ------------------------------------------------>  
      const fetchSerovarData = async () => {
        const startTime = performance.now();  // Start timing

        const [startDate, endDate] = serovarDateRange.value || [];
        const sessionKey = `serovar_${startDate}_${endDate}`;
        const cachedData = getDataFromSessionStorage(sessionKey);

        if (cachedData) {
          serovarData.value = cachedData.serovarData || [];
          tableData.value = cachedData.tableData || [];
        } else {
          try {
            const startDateParam = startDate ? startDate.toISOString().split('T')[0] : null;
            const endDateParam = endDate ? endDate.toISOString().split('T')[0] : null;

            const requiredData = ['serotypes', 'process_country_sourcedata'].join(',');
                
            const response = await axios.get(`${apiUrl}/api/search/`, {
                params: {
                  start_date: startDateParam,
                  end_date: endDateParam,
                  required_data: requiredData
                }
              });
          
          serovarData.value = response.data.serotypes || [];
          tableData.value = response.data.process_country_sourcedata || [];

          storeDataInSessionStorage(sessionKey, {
            serovarData: serovarData.value,
            tableData: tableData.value
          });
          
              logPerformance(startTime, "Serovar data fetch and processing time");
          
            } catch (error) {
                  console.error('Error fetching serovar data:', error);
                }
              }

              logPerformance(startTime, "Serovar data fetch and processing time");
            };

            const filteredSerovarData = computed(() => {
              const sortedData = [...serovarData.value].sort((a, b) => b.value - a.value);
              
              if (topNsero.value !== undefined) {
                return sortedData.slice(0, topNsero.value);
              }
              return sortedData;
            });
      
      // <!-------------------------------------- MLST layer  ------------------------------------------------>
      const fetchMLSTData = async () => {
        const startTime = performance.now();  // Start timing

        const [startDate, endDate] = MLSTRange.value || [];
        const sessionKey = `mlst_${startDate}_${endDate}`;
        const cachedData = getDataFromSessionStorage(sessionKey);

        if (cachedData) {
          MLSTData.value = cachedData.MLSTData || [];
          mlsttableData.value = cachedData.mlsttableData || [];
        } else {
          try {
            const startDateParam = startDate ? startDate.toISOString().split('T')[0] : null;
            const endDateParam = endDate ? endDate.toISOString().split('T')[0] : null;

            const requiredData = ['mlst', 'process_mlst_tabledata'].join(',');

            const response = await axios.get(`${apiUrl}/api/search/`, {
              params: {
                start_date: startDateParam,
                end_date: endDateParam,
                required_data: requiredData
              }
            });
            MLSTData.value = response.data.mlst || [];
            mlsttableData.value = response.data.process_mlst_tabledata || [];

            storeDataInSessionStorage(sessionKey, {
              MLSTData: MLSTData.value,
              mlsttableData: mlsttableData.value
            });

          } catch (error) {
            console.error('Error fetching MLST data:', error);
          }
        }

        logPerformance(startTime, "MLST data fetch and processing time");
      };

      const filteredMLSTData = computed(() => {
        const sortedData = [...MLSTData.value].sort((a, b) => b.value - a.value);
        
        if (topNmlst.value !== undefined) {
          return sortedData.slice(0, topNmlst.value);
        }
        return sortedData;
      });
      
      // <!-------------------------------------- Food layer  ------------------------------------------------>
      const fetchFoodData = async () => {
          const startTime = performance.now();  // Start timing

          const [startDate, endDate] = foodDateRange.value || [];
          const sessionKey = `food_${startDate}_${endDate}`;
          // console.log("date rage:",sessionKey)
          // sessionStorage.clear()
          const cachedData = getDataFromSessionStorage(sessionKey);

          if (cachedData) {
            foodData.value = cachedData.foodData || [];
          } else {
            try {
              const startDateParam = startDate ? startDate.toISOString().split('T')[0] : '1000';
              const endDateParam = endDate ? endDate.toISOString().split('T')[0] : '3000';
              
              const requiredData = ['sourcetype'].join(',');

              const response = await axios.get(`${apiUrl}/api/search/`, {
                params: {
                  start_date: startDateParam,
                  end_date: endDateParam,
                  required_data: requiredData
                }
              });
              foodData.value = response.data.sourcetype || [];

              storeDataInSessionStorage(sessionKey, { foodData: foodData.value });
            } catch (error) {
              console.error('Error fetching food data:', error);
            }
          }

          logPerformance(startTime, "Food data fetch and processing time");
        };

        const filteredsourceData = computed(() => {
          const sortedData = [...foodData.value].sort((a, b) => b.value - a.value);
          
          if (topNsource.value !== undefined) {
            return sortedData.slice(0, topNsource.value);
          }
          return sortedData;
        });

        const debouncedFetchSerovarData = debounce(async () => {
          console.log('Fetching Serovar Data', new Date().toISOString());
          await fetchSerovarData();
        }, 300);  // Adjust debounce time as needed

        const debouncedFetchFoodData = debounce(async () => {
          console.log('Fetching Food Data', new Date().toISOString());
          await fetchFoodData();
        }, 300);

        const debouncedFetchMLSTData = debounce(async () => {
          console.log('Fetching MLST Data', new Date().toISOString());
          await fetchMLSTData();
        }, 300);

      
      // <!-------------------------------------- watch layer  ------------------------------------------------>
      
      watch(serovarDateRange, async (newVal, oldVal) => {
        console.log('Watcher triggered for Serovar Date Range', new Date().toISOString());
        if (newVal && newVal.length === 2 && !isInitialLoad) {
          debouncedFetchSerovarData();
        }
      }, { immediate: false });
      
      watch(foodDateRange, async (newVal, oldVal) => {
        console.log('Watcher triggered for Food Date Range', new Date().toISOString());
        if (newVal && newVal.length === 2 && !isInitialLoad) {
          debouncedFetchFoodData();
        }
      }, { immediate: false });
      
      watch(MLSTRange, async (newVal, oldVal) => {
        console.log('Watcher triggered for MLST Date Range', new Date().toISOString());
        if (newVal && newVal.length === 2 && !isInitialLoad) {
          debouncedFetchMLSTData();
        }
      }, { immediate: false });
      
      
async function reloadData() {
  sessionStorage.clear();
  await Promise.all([
      fetchSerovarData(),
      fetchFoodData(),
      fetchMLSTData(),
  ]);
}

// <!-------------------------------------- Parallel Processing in onMounted ------------------------------------------------>

onMounted(async () => {
  try {
    console.log('Initial data load started', new Date().toISOString());
    const startYear = 1900;
    const endYear = 2024;
    serovarDateRange.value = [new Date(`${startYear}-01-01`), new Date(`${endYear}-12-31`)] as [Date, Date];
    foodDateRange.value = [new Date(`${startYear}-01-01`), new Date(`${endYear}-12-31`)] as [Date, Date];
    MLSTRange.value = [new Date(`${startYear}-01-01`), new Date(`${endYear}-12-31`)] as [Date, Date];

    const startTime = performance.now();  // Start timing for initial data fetch

    // Fetch data in parallel
    await Promise.all([
      fetchSerovarData(),
      fetchFoodData(),
      fetchMLSTData(),
    ]);
    console.log('Initial data load completed', new Date().toISOString());
    isInitialLoad = false;  // Reset the flag after initial load
    logPerformance(startTime, "Initial data fetch and processing time");

  } catch (error) {
    console.error('Error fetching initial data:', error);
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
      
<style scoped>
.table-box {
  border-right: 1px solid #ddd;
}

.table-box:last-child {
  border-right: none;
}

/*添加头部样式，增加层次感*/
.custom-header {
  background: linear-gradient(to right, #4facfe, #00f2fe);
  color: white;
  padding: 15px;
  font-size: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/*添加卡片悬停阴影效果*/
.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
.info-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

/*统一卡片间距*/
.section-row {
  margin: 30px 0;
}

/*增强标题和卡片头部样式*/
.card-header {
  font-size: 18px;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/*小幅优化页面加载动画*/
.el-main {
  animation: fade-in 0.5s ease;
}
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/*增强标题样式和区域分隔线*/
.section-title {
  font-size: 22px !important;
  font-weight: bold;
  text-align: center;
  margin-bottom: 10px;
  color: #333 !important;
}

/* 添加区域分隔线 */
.section-divider {
  border-top: 2px solid #ddd !important;
  margin: 20px 0 !important;
}

/* 卡片悬停效果 */
/* 卡片悬停阴影效果 */
.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

</style>