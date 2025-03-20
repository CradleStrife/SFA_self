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
    <el-scrollbar style="height: 500px;">
      <el-table 
        :data="tableData" 
        style="width: 100%;" 
        :style="{ tableLayout: 'fixed' }"
        @sort-change="handleSortChange">
        <el-table-column prop="period" label="Period" align="center">
          <template #default="scope">
            <span class="period-cell">{{ scope.row.period }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="serotype" label="Serotype" align="center">
          <template #default="scope">
            <span class="serotype-cell">{{ scope.row.serotype }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="country" label="Country" align="center">
          <template #default="scope">
            <span class="country-cell">{{ scope.row.country }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" align="center">
          <template #default="scope">
            <span class="source-cell">{{ scope.row.source }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_count" label="Total Count" align="center" sortable="custom">
          <template #header>
            <div class="sort-header">
              Total Count
              <span class="sort-icon" v-if="sortProp === 'total_count'">
                {{ sortOrder === 'ascending' ? '▲' : '▼' }}
              </span>
            </div>
          </template>
          <template #default="scope">
            <span class="total-count-cell">{{ scope.row.total_count }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-scrollbar>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import dayjs from 'dayjs';

const topN = ref<number | undefined>(undefined); // To store the selected top N value
const topNOptions = [10, 20, 30]; // Options for the top N dropdown

//laiyi 3.14
// 添加排序状态变量
const sortProp = ref('total_count'); // 默认按total_count排序
const sortOrder = ref('descending'); // 默认降序排序

// 处理排序变化
const handleSortChange = ({ column, prop, order }) => {
  if (prop) {
    sortProp.value = prop;
    sortOrder.value = order || 'descending';
  } else {
    // 如果排序被取消，恢复默认排序
    sortProp.value = 'total_count';
    sortOrder.value = 'descending';
  }
};


//

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
  total_count: number;
}

const props = defineProps<{
  serotypeData: SerotypeData[];
}>();

const selectedPeriod = ref<string>('monthly');

const processData = (data: SerotypeData[], period: string): ProcessedData[] => {
  const periodData: { [key: string]: ProcessedData } = {};

  data.forEach((item: SerotypeData) => {
    const { serotype, count, country, source, pub_years } = item;

    if (typeof pub_years !== 'string') {
      console.error('pub_years is not a string:', pub_years);
      return;  // Skip this item if pub_years is not a string
    }

    const date = dayjs(pub_years);
    let periodKey: string = '';

    // Determine the periodKey based on the selected period
    if (period === 'monthly') {
      periodKey = date.format('YYYY-MM-01');
    } else if (period === 'six_monthly') {
      const month = date.month();
      if (month < 6) {
        periodKey = date.year().toString() + '-01-01';
      } else {
        periodKey = date.year().toString() + '-07-01';
      }
    } else if (period === 'yearly') {
      periodKey = date.startOf('year').format('YYYY-01-01');
    }

    const compositeKey = `${periodKey}-${serotype}-${country}-${source}`;

    if (!periodData[compositeKey]) {
      periodData[compositeKey] = {
        period: periodKey,
        serotype: serotype,
        country: country,
        source: source,
        total_count: 0
      };
    }

    periodData[compositeKey].total_count += count;
  });

  const result: ProcessedData[] = Object.values(periodData).sort((a, b) => {
    const dateA = dayjs(a.period);
    const dateB = dayjs(b.period);
    if (dateA.isBefore(dateB)) return 1;
    if (dateA.isAfter(dateB)) return -1;
    return 0;
  });

  return result;
};


//laiyi 3.14
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

  // 应用排序
  return processedData.sort((a, b) => {
    let comparison = 0;
    
    switch (sortProp.value) {
      case 'period':
        const dateA = dayjs(a.period);
        const dateB = dayjs(b.period);
        comparison = dateA.isBefore(dateB) ? -1 : dateA.isAfter(dateB) ? 1 : 0;
        break;
      case 'serotype':
      case 'country':
      case 'source':
        comparison = String(a[sortProp.value]).localeCompare(String(b[sortProp.value]));
        break;
      case 'total_count':
      default:
        comparison = a.total_count - b.total_count;
        break;
    }
    
    return sortOrder.value === 'ascending' ? comparison : -comparison;
  });
});


// const tableData = computed<ProcessedData[]>(() => {
//   let processedData = processData(props.serotypeData, selectedPeriod.value);

//   // Filter top N serotypes
//   if (topN.value !== undefined) {
//     const topSerotypes = [...new Set(processedData.map(item => item.serotype))]
//       .sort((a, b) => {
//         const totalA = processedData.find(item => item.serotype === a)?.total_count ?? 0;
//         const totalB = processedData.find(item => item.serotype === b)?.total_count ?? 0;
//         return totalB - totalA;
//       })
//       .slice(0, topN.value);

//     processedData = processedData.filter(item => topSerotypes.includes(item.serotype));
//   }

//   return processedData;
// });
</script>

<style scoped>
.custom-table-container {
  margin: 20px;
}
.filter-container {
  margin-bottom: 20px;
}

/* 定义单元格样式 */
.period-cell {
  color: black;
}
.serotype-cell {
  color: red;
}
.country-cell {
  color: orange;
}
.source-cell {
  color: teal;
}
.total-count-cell {
  color: blue;
}

/* laiyi：3.14：排序表头样式 */
.sort-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.sort-icon {
  margin-left: 5px;
  font-weight: bold;
  color: #1890ff;
}
</style>
