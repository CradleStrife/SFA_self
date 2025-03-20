<template>
  <div>
    <h3>MLST cases Monitoring</h3>
    <div v-if="sortedMLSTRecords.length > 0">
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th @click="setSortField('name')" class="sortable-header">
                MLST
                <span class="sort-icon" v-if="sortField === 'name'">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th @click="setSortField('initialCount')" class="sortable-header">
                Initial Count
                <span class="sort-icon" v-if="sortField === 'initialCount'">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th @click="setSortField('finalCount')" class="sortable-header">
                Final Count
                <span class="sort-icon" v-if="sortField === 'finalCount'">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
              <th @click="setSortField('increase')" class="sortable-header">
                Increase
                <span class="sort-icon" v-if="sortField === 'increase'">
                  {{ sortOrder === 'asc' ? '▲' : '▼' }}
                </span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="record in sortedMLSTRecords"
              :key="record.name"
              @click="handleMLSTClick(record.name)"
              style="cursor: pointer; color: blue;"
            >
              <td>{{ record.name }}</td>
              <td>{{ record.initialCount }}</td>
              <td>{{ record.finalCount }}</td>
              <td>{{ record.increase }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div>
        Date from {{ formattedStartDate }} to {{ formattedEndDate }}
      </div>
    </div>
    <div v-else>
      No records found for the selected date.
    </div>
    <div v-if="lineChartData">
      <h4>Trend for {{ selectedMLST }}</h4>
      <v-chart :option="lineChartOption" autoresize style="height: 400px;"></v-chart>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { defineProps, ref, watch, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

interface Record {
  ID: string[];
  Date: string[];
  MLST: string[];
}

//1.22 larry
// 新增变量，并定义时间范围保证一定会显示图表
const dateRange = ref<[Date, Date]>([
  new Date(1900, 0, 1), // 从 1900 年 1 月 1 日开始
  new Date(), // 当前日期
]);


//1.22
// 当Year Range变化时触发
const onDateRangeChange = (newDateRange: [Date, Date]) => {
  if (newDateRange && newDateRange.length === 2) {
    const [start, end] = newDateRange;
    startDate.value = start;
    endDate.value = end;
    applyFilters(start, end); // 应用过滤逻辑
  }
};

//1.24 larry
// 当前选中的 MLST 类型
const selectedMLST = ref('');

// 图表数据和配置
const lineChartData = ref<{ date: string; count: number }[] | null>(null);
const lineChartOption = ref({});

//1.24 larry
// 处理 MLST 点击逻辑
const handleMLSTClick = (mlst: string) => {
  selectedMLST.value = mlst;

  // 筛选出与当前 MLST 对应的数据
  const dataForMLST = props.mlstData
    .filter((record) => record.MLST[0] === mlst)
    .map((record) => ({
      date: record.Date[0], // 获取日期
      count: 1, // 假设每条记录计数为 1，根据需求修改
    }));

  // 按日期聚合数据
  const aggregatedData = dataForMLST.reduce((acc, { date, count }) => {
    if (!acc[date]) {
      acc[date] = 0;
    }
    acc[date] += count;
    return acc;
  }, {} as Record<string, number>);

  // 转换为图表需要的格式
  lineChartData.value = Object.entries(aggregatedData).map(([date, count]) => ({
    date,
    count,
  }));

  // 更新图表配置
  updateLineChart();
};

//1.24 larry
//更新图表配置
const updateLineChart = () => {
  if (!lineChartData.value || lineChartData.value.length === 0) {
    lineChartOption.value = {
      title: {
        text: 'No Data Available',
        left: 'center',
      },
    };
    return;
  }

  lineChartOption.value = {
    title: {
      text: `Trend for ${selectedMLST.value}`,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: lineChartData.value.map((item) => item.date),
      axisLabel: {
        rotate: 45,
      },
    },
    yAxis: {
      type: 'value',
      name: 'Total Count',
    },
    series: [
      {
        type: 'line',
        data: lineChartData.value.map((item) => item.count),
        smooth: true,
        lineStyle: {
          color: '#007BFF',
        },
        areaStyle: {
          opacity: 0.1,
        },
      },
    ],
  };
};




const props = defineProps<{ mlstData: Record[], startDate: Date | null, endDate: Date | null }>();

const userInputDate = ref<string | null>(null);
const selectedYears = ref<number | null>(null);
const selectedMonths = ref<number | null>(null);
const selectedSortOption = ref<string>('increase');
const filteredRecords = ref<Record[]>([]);
const mlstCounts = ref<{ [key: string]: number }>({});
const mlstIncreaseRecords = ref<{ name: string, initialCount: number, finalCount: number, increase: number }[]>([]);

const startDate = ref<Date | null>(null);
const endDate = ref<Date | null>(null);

//laiyi 3.14
// 添加排序状态变量
const sortField = ref('increase'); // 默认按increase排序
const sortOrder = ref('desc'); // 默认降序排序

// 排序字段设置函数
const setSortField = (field) => {
  if (sortField.value === field) {
    // 如果点击的是当前排序字段，则切换排序顺序
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    // 如果点击的是新字段，则设置为默认降序
    sortField.value = field;
    sortOrder.value = 'desc';
  }
};

// 替换原来的sortedMLSTRecords计算属性
const sortedMLSTRecords = computed(() => {
  return [...mlstIncreaseRecords.value].sort((a, b) => {
    let comparison = 0;
    
    if (sortField.value === 'name') {
      comparison = String(a.name).localeCompare(String(b.name));
    } else {
      comparison = a[sortField.value] - b[sortField.value];
    }
    
    return sortOrder.value === 'asc' ? comparison : -comparison;
  }).slice(0, 10); // 保留只取前10条的逻辑
});


const validateDate = () => {
  if (userInputDate.value) {
    const selectedDate = new Date(userInputDate.value);
    if (isNaN(selectedDate.getTime())) {
      ElMessage.error('Invalid date format. Please enter a valid date.');
      userInputDate.value = null;
      return;
    }
    if (startDate.value && endDate.value) {
      if (selectedDate < startDate.value || selectedDate > endDate.value) {
        ElMessage.error(`Date out of range. Please select a date between ${startDate.value.toISOString().split('T')[0]} and ${endDate.value.toISOString().split('T')[0]}.`);
        userInputDate.value = null;
      }
    }
  }
};

const calculateDateRange = (date: Date, months: number) => {
  const end = new Date(date);
  const start = new Date(date);
  start.setMonth(start.getMonth() - months);
  console.log('Calculated range:', { start, end });
  return { start, end };
};

const calculateMLSTIncreases = (startDate: Date, endDate: Date) => {
  const initialCounts: { [key: string]: number } = {};
  const finalCounts: { [key: string]: number } = {};

  const startOfNextMonth = new Date(startDate.getFullYear(), startDate.getMonth() + 1, 1);

  props.mlstData.forEach(record => {
    const recordDate = new Date(record.Date[0]);

    // Initial counts from the start date to the end of the start month
    if (recordDate >= startDate && recordDate < startOfNextMonth) {
      initialCounts[record.MLST[0]] = (initialCounts[record.MLST[0]] || 0) + 1;
    }

    // Final counts for the end date
    if (recordDate >= startDate && recordDate <= endDate) {
      finalCounts[record.MLST[0]] = (finalCounts[record.MLST[0]] || 0) + 1;
    }
  });

  mlstIncreaseRecords.value = Object.keys(finalCounts).map(mlst => ({
    name: mlst,
    initialCount: initialCounts[mlst] || 0,
    finalCount: finalCounts[mlst],
    increase: finalCounts[mlst] - (initialCounts[mlst] || 0),
  })).filter(record => record.increase > 0);

  console.log('MLST Increase Records:', mlstIncreaseRecords.value);
};

//1.22 larry：修改applyFilters，注意要初始化提前
// 2. 定义 applyFilters 方法（必须在 watch 之前）
const applyFilters = (startDate: Date, endDate: Date) => {
  mlstCounts.value = {};
  filteredRecords.value = [];
  console.log('Applying filters with startDate:', startDate, 'endDate:', endDate);

  props.mlstData.forEach(record => {
    const recordDate = new Date(record.Date[0]);
    if (recordDate >= startDate && recordDate <= endDate) {
      if (!mlstCounts.value[record.MLST[0]]) {
        mlstCounts.value[record.MLST[0]] = 0;
      }
      mlstCounts.value[record.MLST[0]] += 1;
      filteredRecords.value.push(record);
    }
  });

  console.log('Filtered Records:', filteredRecords.value);
  calculateMLSTIncreases(startDate, endDate);
};


//1.22 larry：修改watch以保证和trendAnalysis.vue中同步，同时注意要修改applyFilters位置保证其在watch的上方
// 定义 watch
watch(
  () => [props.mlstData, props.startDate, props.endDate],
  ([newMlstData, newStartDate, newEndDate]) => {
    if (newStartDate && newEndDate) {
      startDate.value = new Date(newStartDate);
      endDate.value = new Date(newEndDate);

      // 当 props.mlstData 更新时，重新应用过滤
      if (newMlstData && newMlstData.length > 0) {
        applyFilters(startDate.value, endDate.value);
      }
    }
  },
  { immediate: true } // 页面加载时立即触发
);




const resetFilters = () => {
  userInputDate.value = null;
  selectedYears.value = null;
  selectedMonths.value = null;
  startDate.value = props.startDate ? new Date(props.startDate) : null;
  endDate.value = props.endDate ? new Date(props.endDate) : null;
  console.log("Resetting filters.");
  if (startDate.value && endDate.value) {
    applyFilters(startDate.value, endDate.value);
  }
};

const applyDateFilter = () => {
  if (userInputDate.value) {
    const selectedDate = new Date(userInputDate.value);
    if (!isNaN(selectedDate.getTime())) {
      if (selectedYears.value !== null) {
        selectedYears.value = selectedYears.value * 12;
        if (selectedMonths.value !== null) {
          const final = selectedMonths.value + selectedYears.value;
          const { start, end } = calculateDateRange(selectedDate, final);
          console.log('Selected date:', selectedDate, 'Range:', final, 'Calculated start:', start, 'Calculated end:', end);
          applyFilters(start, end);
          startDate.value = start;
          endDate.value = end;
          selectedYears.value = selectedYears.value / 12;
        } else {
          const final = 0 + selectedYears.value;
          const { start, end } = calculateDateRange(selectedDate, final);
          console.log('Selected date:', selectedDate, 'Range:', final, 'Calculated start:', start, 'Calculated end:', end);
          applyFilters(start, end);
          startDate.value = start;
          endDate.value = end;
          selectedYears.value = selectedYears.value / 12;
        }
      } else if (selectedMonths.value !== null) {
        const { start, end } = calculateDateRange(selectedDate, selectedMonths.value);
        console.log('Selected date:', selectedDate, 'Range:', selectedMonths.value, 'Calculated start:', start, 'Calculated end:', end);
        applyFilters(start, end);
        startDate.value = start;
        endDate.value = end;
      } else {
        applyFilters(selectedDate, selectedDate);
        startDate.value = selectedDate;
        endDate.value = selectedDate;
      }
    } else {
      console.log('Invalid input date:', userInputDate.value);
    }
  }
};


//laiyi 3.14 注释掉
// const sortedMLSTRecords = computed(() => {
//   if (selectedSortOption.value === 'increase') {
//     return mlstIncreaseRecords.value.sort((a, b) => b.increase - a.increase).slice(0, 10);
//   } else if (selectedSortOption.value === 'finalCount') {
//     return mlstIncreaseRecords.value.sort((a, b) => b.finalCount - a.finalCount).slice(0, 10);
//   } else {
//     return mlstIncreaseRecords.value;
//   }
// });

const formattedStartDate = computed(() => startDate.value ? startDate.value.toISOString().split('T')[0] : '');
const formattedEndDate = computed(() => endDate.value ? endDate.value.toISOString().split('T')[0] : '');

onMounted(() => {
  console.log("Component mounted.");
  // 设置默认时间范围
  if (props.startDate && props.endDate) {
    startDate.value = new Date(props.startDate);
    endDate.value = new Date(props.endDate);
    applyFilters(startDate.value, endDate.value);
  }
});
</script>

<style scoped>
.table-container {
  display: block;
  max-height: 400px;
  overflow-y: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
  position: sticky;
  top: 0;
  z-index: 1;
}

tbody tr {
  display: table;
  width: 100%;
  table-layout: fixed;
}

thead, tbody {
  display: table;
  width: 100%;
  table-layout: fixed;
}

/* 添加排序相关样式 */
.sortable-header {
  cursor: pointer;
  position: relative;
  user-select: none;
  padding-right: 25px; /* 为排序图标留出空间 */
}

.sortable-header:hover {
  background-color: #f0f0f0;
}

.sort-icon {
  position: absolute;
  right: 8px;
  color: #1890ff;
}
</style>
