<template>
  <div class="custom-table-container" >
    <div class="filter-container" > 
        <input v-model="serotypeFilter" placeholder="Filter by Serotype"  style="height: 24px" />
        <el-select :popper-append-to-body="false" v-model="topN" placeholder="Select Top N" style="width: 200px; ">
          <el-option v-for="n in topNOptions" :key="n" :label="`Top ${n}`" :value="n" />
        </el-select>
      <el-button @click="clearFilter">Reset All Filters</el-button>
    </div>
    <el-table :data="sortedData" style="width: 100%">
      <el-table-column type="index" label="Index" width="100"></el-table-column>
      <el-table-column prop="serotype" label="Serotype" width="200"></el-table-column>
      <el-table-column prop="count" label="Count" sortable width="100"></el-table-column>
      <el-table-column prop="mlst" label="MLST" width="100"></el-table-column>
      <el-table-column></el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import { ElTable, ElTableColumn, ElButton, ElSelect, ElOption } from 'element-plus';

const props = defineProps<{
  seroMLSTData: { serotype: string, count: number, mlst: { mlst: string, count: number }[] }[]
}>();

const serotypeFilter = ref('');
const currentSortField = ref('count');
const isAscending = ref(true);
const topN = ref<number | undefined>(undefined); // To store the selected top N value
const topNOptions = [10, 15, 20]; // Options for the top N dropdown

// Computed property to filter and sort data
const sortedData = computed(() => {
  let data = props.seroMLSTData;
  // console.log(data);
  // console.log(typeof(data[0].serotype[0]))
  // Filter by serotype if filter is applied
  if (serotypeFilter.value) {
    data = data.filter(item => {
      let serotypeString:string=item.serotype[0]
      if (typeof(serotypeString)==="string") {
        console.log(serotypeString,"isstring")
        serotypeString=serotypeString.toLowerCase()
        return serotypeString.includes(serotypeFilter.value.toLowerCase())
      }
      else return false;
    });
  }

  // Sorting logic: sort based on the currentSortField
  if (currentSortField.value === 'count') {
    data = data.sort((a, b) => b.count - a.count);
  }

  // Filter to top N serotypes if topN is selected
  if (topN.value !== undefined) {
    data = data.slice(0, topN.value);
  }

  return data;
});

const clearFilter = () => {
  serotypeFilter.value = '';
  topN.value = undefined;
};
</script>

<style scoped>
.custom-table-container {
  width: 100%;
}

.filter-container {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 10px;
}


.mlst-tag {
  display: inline-block;
  background-color: #e0f7fa;
  padding: 2px 0px;
  margin: 2px;
  border-radius: 1px;
}

.el-select .el-input__inner {
  height: 100% !important;
  width: 150px !important; /* Ensure the input width is set */
  padding: 0 10px !important;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
