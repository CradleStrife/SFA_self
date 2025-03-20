<template>
  <el-scrollbar style="height: 400px;">
    <el-table :data="serocountryData" style="width: 100%;" border>
      <!-- Custom header slot for the Serotype column -->
      <el-table-column prop="name" label="Serotype" width="200">
        <template #header>
          <div class="custom-header">Serotype</div>
        </template>
        <template #default="{ row }">
          <div class="custom-cell">{{ row.name }}</div>
        </template>
      </el-table-column>
      <el-table-column label="Countries">
        <template #header>
          <div class="custom-header2">Countries</div>
        </template>
        <template #default="{ row }">
          <span>{{ getCountriesList(row.countries) }}</span>
        </template>
      </el-table-column>
    </el-table>
  </el-scrollbar>
</template>

<script lang="ts" setup>
import { defineProps } from 'vue';

const props = defineProps<{
  serocountryData: { name: string; countries: { country: string }[] }[]
}>();

const getCountriesList = (countries: { country: string }[]) => {
  return countries.map(countryObj => countryObj.country).join(', ');
};
</script>

<style scoped>
.custom-header {
  background-color: #9d67f5; /* Your desired background color */
  padding: 10px;
  font-weight: bold;
  color: #08040e; /* Font color */
}

.custom-header2 {
  background-color: #9d67f5; /* Your desired background color */
  padding: 10px;
  font-weight: bold;
  color: black; /* Font color */
}
</style>
