<template>
  <div>
    <h3>MLST cases Monitoring</h3>
    <div v-if="sortedMLSTRecords.length > 0">
      <div class="table-container">
        <table>
          <!-- <thead>
            <tr>
              <th>MLST</th>
              <th>Initial Count</th>
              <th>Final Count</th>
              <th>Increase</th>
            </tr>
          </thead> -->
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
            @click="emitRowClick(record)"
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
        Year from {{ formattedstartYear }} to {{ formattedEndDate }}
      </div>
    </div>
    <div v-else>
      No records found for the selected date.
    </div>
  </div>
</template>

<script lang="ts" setup>
import { defineProps, ref, watch, defineEmits,computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

interface Record {
  ID: string[];
  Date: string[];
  MLST: string[];
}

//LAIYI
const emit = defineEmits<{
  // 这里的 row 类型要和你在父组件 handleMLSTClick(row) 时所需的类型匹配
  (e: 'row-click', row: { name: string; initialCount: number; finalCount: number; increase: number }): void
}>();


const props = defineProps<{ mlstData: Record[], startYear: number | null, endYear: number | null }>();

const userInputDate = ref<string | null>(null);
const selectedYears = ref<number | null>(null);
const selectedMonths = ref<number | null>(null);
const selectedSortOption = ref<string>('increase');
const filteredRecords = ref<Record[]>([]);
const mlstCounts = ref<{ [key: string]: number }>({});
const mlstIncreaseRecords = ref<{ name: string, initialCount: number, finalCount: number, increase: number }[]>([]);

const startYear = ref<Date | null>(null);
const endYear = ref<Date | null>(null);

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


const sortedMLSTRecords = computed(() => {
  if (!mlstIncreaseRecords.value || mlstIncreaseRecords.value.length === 0) return [];
  
  return [...mlstIncreaseRecords.value].sort((a, b) => {
    let comparison = 0;
    
    if (sortField.value === 'name') {
      comparison = String(a.name).localeCompare(String(b.name));
    } else {
      comparison = a[sortField.value] - b[sortField.value];
    }
    
    return sortOrder.value === 'asc' ? comparison : -comparison;
  }).slice(0, 10); // 保留只显示前10条的逻辑
});


const validateDate = () => {
  if (userInputDate.value) {
    const selectedDate = new Date(userInputDate.value);
    if (isNaN(selectedDate.getTime())) {
      ElMessage.error('Invalid date format. Please enter a valid date.');
      userInputDate.value = null;
      return;
    }
    if (startYear.value && endYear.value) {
      if (selectedDate < startYear.value || selectedDate > endYear.value) {
        ElMessage.error(`Date out of range. Please select a date between ${startYear.value.toISOString().split('T')[0]} and ${endYear.value.toISOString().split('T')[0]}.`);
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

const applyFilters = (startYear: Date, endYear: Date) => {
  mlstCounts.value = {};
  filteredRecords.value = [];
  console.log('Applying filters with startYear:', startYear, 'endYear:', endYear);


  props.mlstData.forEach(record => {
  const dates = Array.isArray(record.Date) ? record.Date : [record.Date];
  let withinRange = false;

  console.log(`Processing record ID: ${record.ID}, MLST: ${record.MLST}, Dates:`, dates);

  // Check each date to see if it falls within the startYear and endYear range
  for (const dateString of dates) {
    const recordDate = new Date(dateString);
    const recordYear = recordDate.getFullYear();  // Extract the year only

    console.log(`Checking year: ${recordYear} (original string: ${dateString})`);

    if (isNaN(recordDate.getTime())) {
      console.error('Invalid date found:', dateString);
      continue;  // Skip invalid dates
    }

    const startYearValue = startYear.getFullYear();  // Extract year from startYear
    const endYearValue = endYear.getFullYear();      // Extract year from endYear

    // Compare only the years
    if (recordYear >= startYearValue && recordYear <= endYearValue) {
      console.log(`Year within range: ${recordYear}`);
      withinRange = true;
      break;  // Stop checking once we find a valid year in range
    }
  }

  // If any year was within the range, process the record
  if (withinRange) {
    // First, check if MLST is ['NA'] or 'NA' and skip those records
    if (Array.isArray(record.MLST) && record.MLST.length === 1 && record.MLST[0] === 'NA') {
      console.log(`Skipping record with ['NA'] MLST: ${record.ID}`);
      return; // Skip this record
    } else if (typeof record.MLST === 'string' && record.MLST === 'NA') {
      console.log(`Skipping record with 'NA' MLST: ${record.ID}`);
      return; // Skip this record
    }

    // If MLST contains multiple elements, process each element
    if (Array.isArray(record.MLST) && record.MLST.length > 1) {
      record.MLST.forEach(mlstValue => {
        if (mlstValue !== 'NA') {
          if (!mlstCounts.value[mlstValue]) {
            mlstCounts.value[mlstValue] = 0;
          }
          mlstCounts.value[mlstValue] += 1;
        }
      });
    } else if (Array.isArray(record.MLST) && record.MLST.length === 1) {
      // If there's only one element in MLST
      const mlstValue = record.MLST[0];
      if (mlstValue !== 'NA') {
        if (!mlstCounts.value[mlstValue]) {
          mlstCounts.value[mlstValue] = 0;
        }
        mlstCounts.value[mlstValue] += 1;
      }
    }

    // Add the record to filteredRecords
    filteredRecords.value.push(record);
  } else {
    console.log(`Record ID: ${record.ID} was not within the year range.`);
  }
});


  console.log('Filtered Records:', filteredRecords.value);

  calculateMLSTIncreases(startYear, endYear);
};

const calculateMLSTIncreases = (startYear: Date, endYear: Date) => {
  const initialCounts: { [key: string]: number } = {};
  const finalCounts: { [key: string]: number } = {};

  // Adjusted to calculate until the end of the year
  const startOfNextYear = new Date(startYear.getFullYear() + 1, 0, 1);

  // Use filteredRecords instead of props.mlstData
  filteredRecords.value.forEach(record => {
    const recordDate = new Date(record.Date[0]);

    // Initial counts from the start date to the end of the year
    if (recordDate >= startYear && recordDate < startOfNextYear) {
    // Loop through all MLST values in the array for initial counts
    record.MLST.forEach(mlstValue => {
      if (mlstValue !== 'NA') {  // Optional: skip invalid MLST values
        initialCounts[mlstValue] = (initialCounts[mlstValue] || 0) + 1;
      }
    });
  }

  // Final counts for the end date
  if (recordDate >= startYear && recordDate <= endYear) {
    // Loop through all MLST values in the array for final counts
    record.MLST.forEach(mlstValue => {
      if (mlstValue !== 'NA') {  // Optional: skip invalid MLST values
        finalCounts[mlstValue] = (finalCounts[mlstValue] || 0) + 1;
      }
    });
  }
});

  // Calculate increase and filter records with an increase
  mlstIncreaseRecords.value = Object.keys(finalCounts).map(mlst => ({
    name: mlst,
    initialCount: initialCounts[mlst] || 0,
    finalCount: finalCounts[mlst],
    increase: finalCounts[mlst] - (initialCounts[mlst] || 0)
  })).filter(record => record.increase > 0);

  console.log('MLST Increase Records:', mlstIncreaseRecords.value);
};

watch(
  () => [props.startYear, props.endYear],
  ([newstartYear, newEndDate]) => {
    if (newstartYear) {
      startYear.value = new Date(`${newstartYear}-01-01`);
    }
    if (newEndDate) {
      endYear.value = new Date(`${newEndDate}-12-28`);
    }
    console.log("startYear:", startYear.value);
    console.log("endYear:", endYear.value);
    if (startYear.value && endYear.value) {
      applyFilters(startYear.value, endYear.value);
    }
  },
  { immediate: true }
);

// 新增：监听 mlstData 数量变化
watch(
  () => props.mlstData.length,
  (newLength, oldLength) => {
    if (newLength !== oldLength && startYear.value && endYear.value) {
      console.log("mlstData length changed from", oldLength, "to", newLength, ", re-applying filters");
      applyFilters(startYear.value, endYear.value);
    }
  }
);


const resetFilters = () => {
  userInputDate.value = props.endYear ? props.endYear.toString() : null;
  selectedYears.value = props.endYear && props.startYear ? props.endYear - props.startYear : null;
  startYear.value = props.startYear ? new Date(`${props.startYear}-01-01`) : null;
  endYear.value = props.endYear ? new Date(`${props.endYear}-12-28`) : null;
  console.log("Resetting filters.");
  if (startYear.value && endYear.value) {
    applyFilters(startYear.value, endYear.value);
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
          startYear.value = start;
          endYear.value = end;
          selectedYears.value = selectedYears.value / 12;
        } else {
          const final = 0 + selectedYears.value;
          const { start, end } = calculateDateRange(selectedDate, final);
          console.log('Selected date:', selectedDate, 'Range:', final, 'Calculated start:', start, 'Calculated end:', end);
          applyFilters(start, end);
          startYear.value = start;
          endYear.value = end;
          selectedYears.value = selectedYears.value / 12;
        }
      } else if (selectedMonths.value !== null) {
        const { start, end } = calculateDateRange(selectedDate, selectedMonths.value);
        console.log('Selected date:', selectedDate, 'Range:', selectedMonths.value, 'Calculated start:', start, 'Calculated end:', end);
        applyFilters(start, end);
        startYear.value = start;
        endYear.value = end;
      } else {
        applyFilters(selectedDate, selectedDate);
        startYear.value = selectedDate;
        endYear.value = selectedDate;
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

const formattedstartYear = computed(() => {
  if (userInputDate.value && selectedYears.value !== null) {
    const startYear = parseInt(userInputDate.value) - selectedYears.value;
    return startYear.toString();
  } else {
    return props.startYear ? props.startYear.toString() : '';
  }
});

const formattedEndDate = computed(() => {
  return userInputDate.value ? userInputDate.value.toString() : props.endYear ? props.endYear.toString() : '';
});


onMounted(() => {
  console.log("Component mounted.");
  if (startYear.value && endYear.value) {
    applyFilters(startYear.value, endYear.value);
  }
});

function emitRowClick(row: { name: string; initialCount: number; finalCount: number; increase: number }) {
  emit('row-click', row);
}

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

/* laiyi 3.14：添加排序相关样式 */
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
