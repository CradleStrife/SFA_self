<template>
    <el-table :data="dataList" style="width: 100%" max-height="800px" border>
        <el-table-column label="Isolate ID" prop="isolate_id"></el-table-column>
        <el-table-column label="Isolate Source" prop="isolate_source"></el-table-column>
        <el-table-column label="Isolate Date" prop="isolate_date"></el-table-column>    
        <el-table-column label="Isolate Country" prop="isolate_country"></el-table-column>    
        <el-table-column label="Serotype" prop="serotype"></el-table-column>
        <el-table-column label="MLST" prop="mlst"></el-table-column>
        <el-table-column label="AST Data" prop="ast_data"></el-table-column>
        <el-table-column label="SPI" prop="spi"></el-table-column>
        <el-table-column label="AMR" prop="amr"></el-table-column>
        <el-table-column label="Plasm ID" prop="plasmid"></el-table-column>
        <el-table-column label="SNP" prop="snp"></el-table-column>
        <el-table-column label="Virulence Genes" prop="virulence_genes"></el-table-column>
        <el-table-column label="Location">
            <template #default="{ row }">
                <!-- 使用双大括号渲染表达式 -->
                {{ row.location? `lat:${row.location.lat},lon:${row.location.lon}` : 'N/A' }}
            </template>
        </el-table-column>
        <el-table-column label="Location Official Name" prop="location_official_name"></el-table-column>

    </el-table>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const props=defineProps({
    dataList: {
        type: Array,
    }
})

const dataList=ref(props.dataList)







</script>