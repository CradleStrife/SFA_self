<template>
<el-table :data="tableData" style="width: 100%" max-height="800px" border>
    <el-table-column label="Field" prop="label"></el-table-column>
    <el-table-column label="Value" prop="content"></el-table-column>
</el-table>
</template>

<script setup>
import { onMounted, ref } from 'vue'

// 定义 props
const props = defineProps({
dataObject: {
    type: Object, // 这里修改为 Object 类型，因为要展示单个对象
    required: true,
}
})
// 引用传入的 dataObject
const dataObject = ref(props.dataObject)

// 定义列配置
const tableData = ref([
{ label: 'Isolate Source', prop: 'isolate_source', content: null },
{ label: 'Isolate Date', prop: 'isolate_date', content: null }, 
{ label: 'Isolate Country', prop: 'isolate_country', content: null},
{ label: 'Serotype', prop: 'serotype', content: null },
{ label: 'MLST', prop: 'mlst', content: null },
{ label: 'AST Data', prop: 'ast_data', content: null },
{ label: 'SPI', prop: 'spi', content: null },
{ label: 'AMR', prop: 'amr', content: null },
{ label: 'Plasm ID', prop: 'plasmid', content: null },
{ label: 'SNP', prop: 'snp', content: null },
{ label: 'Virulence Genes', prop: 'virulence_genes', content: null },
{ label: 'Location', prop: 'location', content: null },
{ label: 'Location Official Name', prop: 'location_official_name', content: null }
])

onMounted(() => {
    for (let i = 0; i < tableData.value.length; i++) {
        if (tableData.value[i].prop === 'location') {
            tableData.value[i].content=`lat: ${dataObject.value.location.lat}, lon: ${dataObject.value.location.lon}`
        } else {
            tableData.value[i].content=dataObject.value[tableData.value[i].prop]
        }
    }
    console.log(tableData.value)
})


</script>

<style scoped>
/* 表格样式 */
.el-table {
width: 100%;
table-layout: fixed;
}

.el-table-column {
min-width: 150px;
word-wrap: break-word;
}
</style>