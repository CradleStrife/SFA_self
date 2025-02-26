<template>
    <div class="result-box">
      <el-table :data="processedResults" style="width: 100%" max-height="800px" border @selection-change="handleSelectionChange">
        <el-table-column label="PMCID" prop="pmcid"></el-table-column>
        <el-table-column label="Isolates with Linking">
            <template #default="{ row }">
                <el-button v-if="isUnemptyArray(row.isolates_with_linking)"
                size="mini" 
                style="width: 100%; height: 100%;" 
                @click="openDialog('Isolates with Linking', row.isolates_with_linking)">
                View
                </el-button>
            </template>
        </el-table-column>
        <el-table-column label="No Isolates Only Assay Information">
            <template #default="{ row }">
                <el-button v-if="isUnemptyObject(row.no_isolates_only_assayinformation)"
                size="mini" 
                style="width: 100%; height: 100%;" 
                @click="openDialog('No Isolates Only Assay Information', row.no_isolates_only_assayinformation)">
                View
                </el-button>
            </template>
        </el-table-column>
        <el-table-column label="Merge Accession Number">
            <template #default="{ row }">
                <el-button v-if="isUnemptyArray(row.merge_accession_number)"
                size="mini" 
                style="width: 100%; height: 100%;" 
                @click="openDialog('Merge Accession Number', row.merge_accession_number)">
                View
                </el-button>
            </template>
        </el-table-column>
        
      </el-table>
  
      <!-- 弹出框 -->
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="50%">
        <div v-if="dialogTitle === 'Isolates with Linking' && contentType === 'Array'">
            <IsolatesWithLinkingTable :dataList="dialogContent" />
        </div>
        <div v-else-if="dialogTitle === 'No Isolates Only Assay Information' && contentType === 'Object'">
            <NoIsolatesOnlyAssayInformationTable :dataObject="dialogContent" />
        </div>
        <div v-else>
            <pre>{{ dialogContent }}</pre>
        </div>
      </el-dialog>
    </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';
import axios from 'axios';
import IsolatesWithLinkingTable from './IsolatesWithLinkingTable.vue';
import NoIsolatesOnlyAssayInformationTable from './NoIsolatesOnlyAssayInformationTable.vue';

// 定义 props
const props = defineProps({
    processedResults: {
        type: Array,
        required: true
    }
});

// 定义 emits
const emits = defineEmits(['edit']);

// 定义响应式数据
const dialogVisible = ref(false);
const dialogTitle = ref('');
const dialogContent = ref('');
const contentType = ref('');

// 定义方法
const openDialog = (field, value) => {
    dialogTitle.value = field;
    let content = value || 'No data available';
    if (Array.isArray(content)) {
        contentType.value = 'Array';
    } else if (typeof content === 'string') {
        contentType.value = 'String';
    } else {
        contentType.value = 'Object';
    }
    console.log("contentType:", contentType.value);
    dialogContent.value = content;
    console.log(typeof content, ":", content);
    console.log("dialogVisible:", dialogVisible.value);
    dialogVisible.value = true;
    console.log("dialogVisible:", dialogVisible.value);
};

const replaceQuotes = (str) => {
    return str.replace(/'/g, '"');
};

const handleSelectionChange = (selection) => {
    props.processedResults.forEach(item => {
        item.selected = selection.some(selectedItem => selectedItem.ID === item.ID);
    });
};

const handleEdit = (index, row) => {
    emits('edit', index, row);
};

const isEmptyArray = (arr) => {
    return Array.isArray(arr) && arr.length === 0;
};

const isUnemptyArray = (arr) => {
    return Array.isArray(arr) && arr.length > 0;
};

const isEmptyObject = (obj) => {
    return typeof obj === 'object' && obj!== null && Object.keys(obj).length === 0;
};

const isUnemptyObject = (obj) => {
    return typeof obj === 'object' && obj!== null && Object.keys(obj).length > 0;
};

// 定义计算属性
const formattedData = () => {
    return Object.keys(dialogContent.value).map(key => {
        const item = dialogContent.value[key];
        const drugName = Object.keys(item)[0];  // 药物名称
        const interpretation = item[drugName][0];  // 解释
        return {
            index: key,
            name: drugName,
            interpretation
        };
    });
};
</script>

<style scoped>
.result-box {
    border: 1px solid #ddd;
    padding: 10px;
    margin-bottom: 10px;
}

/* 表格样式 */
.el-table {
    width: 100%;
    table-layout: fixed; /* 固定宽度，保证表格列不自适应 */
}

/* 保证每列有适当宽度 */
.el-table-column {
    min-width: 150px;
    word-wrap: break-word;
}

/* 弹窗样式 */
.el-dialog.el-button {
    margin-right: 10px;
}

/* 使按钮填充单元格 */
.el-table-column.el-button {
    display: block; /* 让按钮成为块级元素 */
    width: 100%; /* 宽度占满整个单元格 */
    height: 100%; /* 高度占满整个单元格 */
}
</style>