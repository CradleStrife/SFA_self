<template>
    <div class="custom-table-container">
      <div class="filter-container">
        <el-select v-model="selectedPeriod" placeholder="Select Period" style="width: 200px;">
          <el-option label="Monthly" value="monthly"></el-option>
          <el-option label="6 Monthly" value="six_monthly"></el-option>
          <el-option label="Yearly" value="yearly"></el-option>
        </el-select>
        <el-select :popper-append-to-body="false" v-model="topN" placeholder="Select Top N" style="width: 200px;">
          <el-option v-for="n in topNOptions" :key="n" :label="`Top ${n}`" :value="n" />
        </el-select>
      </div>
      <el-table :data="tableData" style="width: 100%">
        <el-table-column prop="period" label="Period" width="150">
          <template #default="scope">
            <div style="color: black;">{{ scope.row.period }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" width="185">
          <template #default="scope">
            <div style="color: red;">{{ scope.row.source }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="country" label="Country" width="180">
          <template #default="scope">
            <div style="color: orange;">{{ scope.row.country }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" width="210">
          <template #default="scope">
            <div style="color: teal;">{{ scope.row.source }}</div>
          </template>
        </el-table-column>
           </el-table>
    </div>
  </template>
  
  
  <script lang="ts" setup>
  import { ref, computed } from 'vue';
  import dayjs from 'dayjs';
  
  const topN = ref<number | undefined>(undefined); // To store the selected top N value
  const topNOptions = [10, 20, 30]; // Options for the top N dropdown
  
  interface SerotypeData {
    serotype: string;
    count: number;
    country: string;
    source: string;
    pub_years: string;
  }
  
  interface ProcessedData {
    period: string;
    serotype: string;
    country: string;
    source: string;
    count: number;
    total_count: number;
  }
  
  const props = defineProps<{
    serotypeData: SerotypeData[];
  }>();
  
  const selectedPeriod = ref<string>('monthly');
  
  const processData = (data: SerotypeData[], period: string): ProcessedData[] => {
    const periodData: { [key: string]: ProcessedData[] } = {};
  
    data.forEach((item: SerotypeData) => {
      const { serotype, count, country, source, pub_years } = item;
  
      if (typeof pub_years !== 'string') {
        console.error('pub_years is not a string:', pub_years);
        return;  // Skip this item if pub_years is not a string
      }
  
      const date = dayjs(pub_years);
      let key: string = ''; // Initialize key with an empty string
  
      // Determine the key based on the selected period
      if (period === 'monthly') {
        key = date.format('YYYY-MM-01');
      } else if (period === 'six_monthly') {
        const month = date.month();
        if (month < 6) {
          key = date.year().toString() + '-01-01';
        } else {
          key = date.year().toString() + '-07-01';
        }
      } else if (period === 'yearly') {
        key = date.startOf('year').format('YYYY-01-01');
      }
  
      // Aggregate data by period
      if (!periodData[key]) {
        periodData[key] = [];
      }
  
      periodData[key].push({
        period: key,
        serotype: serotype,
        country: country,
        source: source,
        count: count,
        total_count: 0 // Initialize total_count
      });
    });
  
    const sortedPeriods = Object.keys(periodData).sort((a, b) => {
      const dateA = dayjs(a);
      const dateB = dayjs(b);
      if (dateA.isBefore(dateB)) return 1;
      if (dateA.isAfter(dateB)) return -1;
      return 0;
    });
  
    // Flatten the grouped data for display
    const result: ProcessedData[] = [];
    sortedPeriods.forEach(period => {
      periodData[period].forEach((item, index) => {
        if (index === 0) {
          result.push(item);
        } else {
          result.push({
            ...item,
            period: ''
          });
        }
      });
    });
  
    // Calculate total_count for each serotype
    const serotypeCounts: { [key: string]: number } = {};
    result.forEach(item => {
      if (!serotypeCounts[item.serotype]) {
        serotypeCounts[item.serotype] = 0;
      }
      serotypeCounts[item.serotype] += item.count;
    });
  
    result.forEach(item => {
      item.total_count = serotypeCounts[item.serotype];
    });
  
    return result;
  };
  
  
  const tableData = computed<ProcessedData[]>(() => {
    let processedData = processData(props.serotypeData, selectedPeriod.value);
  
    // Filter top N serotypes
    if (topN.value !== undefined) {
      const topSerotypes = [...new Set(processedData.map(item => item.serotype))]
        .sort((a, b) => {
          const totalA = processedData.find(item => item.serotype === a)?.total_count ?? 0;
          const totalB = processedData.find(item => item.serotype === b)?.total_count ?? 0;
          return totalB - totalA;
        })
        .slice(0, topN.value);
  
      processedData = processedData.filter(item => topSerotypes.includes(item.serotype));
    }
  
    return processedData;
  });
  </script>
  
  
  <style scoped>
  .custom-table-container {
    margin: 20px;
  }
  .filter-container {
    margin-bottom: 20px;
  }
  .country-tag, .source-tag {
    display: inline-block;
    margin-right: 5px;
  }
  </style>
  