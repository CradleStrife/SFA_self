<template>
  <div>
    <h3>Serovar Monitoring</h3>
    <div v-if="sortedSerotypeRecords.length > 0">
      <div class="table-container">
        <table>
          <!-- <thead>
            <tr>
              <th>Serotype</th>
              <th>Initial Count</th>
              <th>Final Count</th>
              <th>Increase</th>
            </tr>
          </thead> -->
          <thead>
            <tr>
              <th @click="setSortField('name')" class="sortable-header">
                Serotype
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
              v-for="record in sortedSerotypeRecords"
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
      No records found for the selected year range.
    </div>
  </div>
</template>

<script lang="ts" setup>
import { defineProps, ref, watch, computed, defineEmits ,onMounted } from 'vue';
import { ElMessage } from 'element-plus';

interface Record {
  ID: string[];
  Date: string[];
  Serotype: string[];
}

//laiyi
const emit = defineEmits<{
  (e: 'row-click', row: { name: string; initialCount: number; finalCount: number; increase: number }): void
}>();


const props = defineProps<{ seroData: Record[], startYear: number | null, endYear: number | null }>();

const userInputYear = ref<string | null>(null);
const selectedYears = ref<number | null>(null);
const selectedSortOption = ref<string>('increase');
const filteredRecords = ref<Record[]>([]);
const serotypeCounts = ref<{ [key: string]: number }>({});
const serotypeIncreaseRecords = ref<{ name: string, initialCount: number, finalCount: number, increase: number }[]>([]);

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

const sortedSerotypeRecords = computed(() => {
  if (!serotypeIncreaseRecords.value || serotypeIncreaseRecords.value.length === 0) return [];
  
  return [...serotypeIncreaseRecords.value].sort((a, b) => {
    let comparison = 0;
    
    if (sortField.value === 'name') {
      comparison = String(a.name).localeCompare(String(b.name));
    } else {
      comparison = a[sortField.value] - b[sortField.value];
    }
    
    return sortOrder.value === 'asc' ? comparison : -comparison;
  }).slice(0, 10); // 保留只显示前10条的逻辑
});


const validateYear = () => {
  if (userInputYear.value) {
    const selectedDate = new Date(`${userInputYear.value}-01-01`);
    if (isNaN(selectedDate.getTime())) {
      ElMessage.error('Invalid year format. Please enter a valid year.');
      userInputYear.value = null;
      return;
    }
    if (startYear.value && endYear.value) {
      if (selectedDate < startYear.value || selectedDate > endYear.value) {
        ElMessage.error(`Year out of range. Please select a year between ${startYear.value.getFullYear()} and $ endYear.value.getFullYear()}.`);
        userInputYear.value = null;
      }
    }
  }
};

const applyFilters = (startYear: Date, endYear: Date) => {
  serotypeCounts.value = {};
  filteredRecords.value = [];

  props.seroData.forEach(record => {
    // Ensure that record.Date is always treated as an array, regardless of whether it's a single date or a list of dates.
    const dates = Array.isArray(record.Date) ? record.Date : [record.Date];
    let withinRange = false;

    // Iterate over all dates in the list
    for (const dateString of dates) {
      const recordDate = new Date(dateString);  // Convert each date string to a Date object
      const recordYear = recordDate.getFullYear();
      // Check if this date falls within the range
      const startYearValue = startYear.getFullYear();  // Extract year from startYear
      const endYearValue = endYear.getFullYear();      // Extract year from endYear

      // Compare only the years
      if (recordYear >= startYearValue && recordYear <= endYearValue) {
        console.log(`Year within range: ${recordYear}`);
        withinRange = true;
        break;  // Stop checking once we find a valid year in range
      }
    }

    // If any date was within the range, process the record
    if (withinRange) {
      // First, check if Serotype is ['NA'] or 'NA' and skip those records
      if (Array.isArray(record.Serotype) && record.Serotype.length === 1 && record.Serotype[0] === 'NA') {
        console.log(`Skipping record with ['NA'] Serotype: ${record.ID}`);
        return; // Skip this record
      } else if (typeof record.Serotype === 'string' && record.Serotype === 'NA') {
        console.log(`Skipping record with 'NA' Serotype: ${record.ID}`);
        return; // Skip this record
      }

      // If Serotype contains multiple elements, process each element
      if (Array.isArray(record.Serotype) && record.Serotype.length > 1) {
        record.Serotype.forEach(serotype => {
          if (!serotypeCounts.value[serotype]) {
            serotypeCounts.value[serotype] = 0;
          }
          serotypeCounts.value[serotype] += 1;
        });
      } else if (Array.isArray(record.Serotype) && record.Serotype.length === 1) {
        // If there's only one element in Serotype
        const serotype = record.Serotype[0];
        if (serotype !== 'NA') {  // Optional: skip invalid Serotype values
          if (!serotypeCounts.value[serotype]) {
            serotypeCounts.value[serotype] = 0;
          }
          serotypeCounts.value[serotype] += 1;
        }
      }

      // Add the record to filteredRecords
      filteredRecords.value.push(record);
    }
  });
  calculateSerotypeIncreases(startYear, endYear);
};

const calculateSerotypeIncreases = (startYear: Date, endYear: Date) => {
  const initialCounts: { [key: string]: number } = {};
  const finalCounts: { [key: string]: number } = {};
  const startOfNextYear = new Date(startYear.getFullYear() + 1, 0, 1);
  // Use filteredRecords instead of props.seroData
  filteredRecords.value.forEach(record => {
    const recordDate = new Date(record.Date[0]);


    if (recordDate >= startYear && recordDate < startOfNextYear) {
    // Loop through all Serotype values in the array for initial counts
    record.Serotype.forEach(serotypeValue => {
      if (serotypeValue !== 'NA') {  // Optional: skip invalid Serotype values
        initialCounts[serotypeValue] = (initialCounts[serotypeValue] || 0) + 1;
      }
    });
  }

  // Final counts for the end date
  if (recordDate >= startYear && recordDate <= endYear) {
    // Loop through all Serotype values in the array for final counts
    record.Serotype.forEach(serotypeValue => {
      if (serotypeValue !== 'NA') {  // Optional: skip invalid Serotype values
        finalCounts[serotypeValue] = (finalCounts[serotypeValue] || 0) + 1;
      }
    });
  }
});
    // Final counts for records within the date range
 

  // Calculate increase and filter records with an increase
  serotypeIncreaseRecords.value = Object.keys(finalCounts).map(serotype => ({
    name: serotype,
    initialCount: initialCounts[serotype] || 0,
    finalCount: finalCounts[serotype],
    increase: finalCounts[serotype] - (initialCounts[serotype] || 0)
  })).filter(record => record.increase > 0);
};

// Watch for changes to startYear and endYear props
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
  () => props.seroData.length,
  (newLength, oldLength) => {
    if (newLength !== oldLength && startYear.value && endYear.value) {
      console.log("seroData length changed from", oldLength, "to", newLength, ", re-applying filters");
      applyFilters(startYear.value, endYear.value);
    }
  }
);

const resetFilters = () => {
  userInputYear.value = props.endYear ? props.endYear.toString() : null;
  selectedYears.value = props.endYear && props.startYear ? props.endYear - props.startYear : null;
  startYear.value = props.startYear ? new Date(`${props.startYear}-01-01`) : null;
  endYear.value = props.endYear ? new Date(`${props.endYear}-12-28`) : null;
  console.log("Resetting filters.");
  if (startYear.value && endYear.value) {
    applyFilters(startYear.value, endYear.value);
  }
};

const applyYearFilter = () => {
  if (userInputYear.value) {
    const selectedYear = parseInt(userInputYear.value, 10);
    if (!isNaN(selectedYear)) {
      const filterStartDate = new Date(`${selectedYear}-01-01`);
      const filterEndDate = new Date(`${selectedYear}-12-31`);
      applyFilters(filterStartDate, filterEndDate);
    }
  }
};

//laiyi 3.14 注释掉
// const sortedSerotypeRecords = computed(() => {
//   if (selectedSortOption.value === 'increase') {
//     return serotypeIncreaseRecords.value.sort((a, b) => b.increase - a.increase).slice(0, 10);
//   } else if (selectedSortOption.value === 'finalCount') {
//     return serotypeIncreaseRecords.value.sort((a, b) => b.finalCount - a.finalCount).slice(0, 10);
//   } else {
//     return serotypeIncreaseRecords.value;
//   }
// });

const formattedstartYear = computed(() => {
  if (userInputYear.value && selectedYears.value !== null) {
    const startYear = parseInt(userInputYear.value) - selectedYears.value;
    return startYear.toString();
  } else {
    return props.startYear ? props.startYear.toString() : '';
  }
});

const formattedEndDate = computed(() => {
  return userInputYear.value ? userInputYear.value.toString() : props.endYear ? props.endYear.toString() : '';
});


onMounted(() => {
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

th {
  cursor: pointer;
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
