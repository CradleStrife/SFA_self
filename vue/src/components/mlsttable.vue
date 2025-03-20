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
      <!-- 设置表格布局为固定布局 -->
      <el-table 
        :data="tableData" 
        style="width: 100%;" 
        :style="{ tableLayout: 'fixed' }"
        @sort-change="handleSortChange">
        <!-- 移除了 width 属性 -->
        <el-table-column prop="period" label="Period" header-align="center" align="center">
          <template #default="scope">
            <!-- 使用 <span> 标签，并添加类名 -->
            <span class="period-cell">{{ scope.row.period }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="mlst" label="MLST" header-align="center" align="center">
          <template #default="scope">
            <span class="mlst-cell">{{ scope.row.mlst }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="country" label="Country" header-align="center" align="center">
          <template #default="scope">
            <span class="country-cell">{{ scope.row.country }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" header-align="center" align="center">
          <template #default="scope">
            <span class="source-cell">{{ scope.row.source }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_count" label="Total Count" header-align="center" align="center" sortable="custom">
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
interface MlsttypeData {
  "mlst ": string;
  count: number;
  country: string;
  source: string;
  pub_years: string;
}

interface ProcessedData {
  period: string;
  mlst: string;
  country: string;
  source: string;
  total_count: number;
}

const props = defineProps<{
  mlsttypeData: MlsttypeData[];
}>();

const selectedPeriod = ref<string>('monthly');

const processData = (data: MlsttypeData[], period: string): ProcessedData[] => {
  const periodData: { [key: string]: ProcessedData } = {};

  data.forEach((item: MlsttypeData) => {
    const mlst = item["mlst "] ?? "undefined";
    const count = item.count ?? 0;
    const country = item.country ?? "undefined";
    const source = item.source ?? "undefined";
    const pub_years = item.pub_years ?? "undefined";

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

    const compositeKey = `${periodKey}-${mlst}-${country}-${source}`;

    if (!periodData[compositeKey]) {
      periodData[compositeKey] = {
        period: periodKey,
        mlst: mlst,
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
// const tableData = computed<ProcessedData[]>(() => {
//   let processedData = processData(props.mlsttypeData, selectedPeriod.value);

//   if (topN.value !== undefined) {
//     const topmlsttypes = [...new Set(processedData.map(item => item.mlst))]
//       .sort((a, b) => {
//         const totalA = processedData.find(item => item.mlst === a)?.total_count ?? 0;
//         const totalB = processedData.find(item => item.mlst === b)?.total_count ?? 0;
//         return totalB - totalA;
//       })
//       .slice(0, topN.value);

//     processedData = processedData.filter(item => topmlsttypes.includes(item.mlst));
//   }

//   return processedData;
// });
//用新的tableData
const tableData = computed<ProcessedData[]>(() => {
  let processedData = processData(props.mlsttypeData, selectedPeriod.value);

  if (topN.value !== undefined) {
    const topmlsttypes = [...new Set(processedData.map(item => item.mlst))]
      .sort((a, b) => {
        const totalA = processedData.find(item => item.mlst === a)?.total_count ?? 0;
        const totalB = processedData.find(item => item.mlst === b)?.total_count ?? 0;
        return totalB - totalA;
      })
      .slice(0, topN.value);

    processedData = processedData.filter(item => topmlsttypes.includes(item.mlst));
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
      case 'mlst':
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


</script>

<style scoped>
.custom-table-container {
  margin: 25px;
}

.filter-container {
  display: flex;
  justify-content: center;
  gap: 10px; /* Ensures consistent spacing between filter elements */
  margin-bottom: 20px;
}

.el-scrollbar {
  width: 100%;
}

.el-table {
  width: 100%;
  /* 设置表格布局为固定 */
  table-layout: fixed;
}

/* 表格单元格样式 */
.period-cell {
  color: black;
}

.mlst-cell {
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

/* 排序表头样式 */
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
