<template>
    <div class="result-box">
        <div v-if="loading">Loading...</div>
        <el-table
            v-else
            :data="tableData"
            style="width: 100%"
            max-height="800px"
            border
            @selection-change="handleSelectionChange"
        >
            <el-table-column
                v-for="(column, index) in columns"
                :key="index"
                :label="column.label"
            >
                <template #default="{ row, $index }">
                    <div v-if="column.prop === 'merge_accession_number' && row[column.prop].length>0">
                        {{ expandedRows[$index + '_' + column.prop] ? row[column.prop] : getDisplayText(row[column.prop]) }}
                        <el-button
                            size="mini"
                            @click="toggleExpand($index, column.prop)"
                        >
                            {{ expandedRows[$index + '_' + column.prop] ? 'Collapse' : 'Expand' }}
                        </el-button>
                        <el-button 
                            size="mini"
                            style="width: 100%; height: 100%;"
                            @click="openDialog(column.label, row[column.prop])"
                        >
                            View
                        </el-button>
                    </div>
                    <div v-else-if="isEmpty(row[column.prop])"></div>
                    <span v-else-if="isPrimitive(row[column.prop])">
                        <span v-if="shouldShowExpand(row[column.prop])">
                            {{ expandedRows[$index + '_' + column.prop] ? row[column.prop] : getDisplayText(row[column.prop]) }}
                            <el-button
                                size="mini"
                                @click="toggleExpand($index, column.prop)"
                            >
                                {{ expandedRows[$index + '_' + column.prop] ? 'Collapse' : 'Expand' }}
                            </el-button>
                        </span>
                        <span v-else>{{ row[column.prop] }}</span>
                    </span>
                    <span v-else-if="isSinglePrimitiveArray(row[column.prop])">
                        <span v-if="shouldShowExpand(row[column.prop][0])">
                            {{ expandedRows[$index + '_' + column.prop] ? row[column.prop][0] : getDisplayText(row[column.prop][0]) }}
                            <el-button
                                size="mini"
                                @click="toggleExpand($index, column.prop)"
                            >
                                {{ expandedRows[$index + '_' + column.prop] ? 'Collapse' : 'Expand' }}
                            </el-button>
                        </span>
                        <span v-else>{{ row[column.prop][0] }}</span>
                    </span>
                    <el-button
                        v-else
                        size="mini"
                        style="width: 100%; height: 100%;"
                        @click="openDialog(column.label, row[column.prop])"
                    >
                        View
                    </el-button>
                </template>
            </el-table-column>
        </el-table>

        <!-- 弹出框 -->
        <el-dialog v-model="dialogVisible" :title="dialogTitle" width="50%">
            <RecursiveTable v-if="!loading" :processedResults="dialogContent" />
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, defineProps, onMounted, watch,getCurrentInstance } from 'vue';
import { ElTable, ElTableColumn, ElButton, ElDialog } from 'element-plus';
import RecursiveTable from './RecursiveTable.vue';
import {assay_types,sub_types,index_names} from '../index_names';
import axios from 'axios';


const instance = getCurrentInstance();
const apiUrl = (instance.proxy).$apiHost;



// 定义 props
const props = defineProps({
    processedResults: {
        type: [Array, Object],
        required: true
    }
});

// 定义响应式数据
const tableData = ref([]);
const columns = ref([]);
const dialogVisible = ref(false);
const dialogTitle = ref('');
const dialogContent = ref(null);
const loading = ref(true);
const expandedRows = ref({});
const stringLimit=50;

// 判断是否为空值（空、空列表、空对象）
const isEmpty = (value) => {
    if (Array.isArray(value)) {
        return value.length === 0;
    }
    if (typeof value === 'object' && value!== null) {
        return Object.keys(value).length === 0;
    }
    return!value;
};

// 判断是否为基本类型（数或字符串）
const isPrimitive = (value) => {
    return typeof value === 'number' || typeof value === 'string';
};

// 判断是否为仅包含一个基本类型元素的数组
const isSinglePrimitiveArray = (value) => {
    return Array.isArray(value) && value.length === 1 && isPrimitive(value[0]);
};

// 判断是否应该显示展开按钮
const shouldShowExpand = (str) => {
    return typeof str === 'string' && str.length > stringLimit;
};

// 获取要显示的文本
const getDisplayText = (str) => {
    if(typeof(str)!=='string') {
        str=JSON.stringify(str);
    }
    return str.slice(0, stringLimit);
};

// 切换展开状态
const toggleExpand = (rowIndex, prop) => {
    const key = rowIndex + '_' + prop;
    expandedRows.value[key] =!expandedRows.value[key];
};

// 打开弹窗
const openDialog = async (field, value) => {
    console.log(typeof(value))
    let replaced_accession_objects=value
    if (field==="merge_accession_number") {
        replaced_accession_objects=await fetchAccession(value);
    }
    dialogTitle.value = field;
    dialogContent.value = replaced_accession_objects;
    dialogVisible.value = true;
};

const fetchAccession=async (value)=>{
    let replaced_accession_objects=[]
    for (const acnum of value) {
        console.log('acnum:', acnum);
        const strings=acnum.split('[');
        const ac=strings[0]
        const subType=strings[1].split(']')[0];
        const indexType=sessionStorage.getItem('index_type')
        const indexName=index_names[indexType][subType]
        let response=await axios.get(`${apiUrl}/api/simple_search/`,{
            params:{
            index_name:indexName,
            field_name:"Filename",
            field_value:ac
            }
        })
        let results=response.data.results;
        if (results.length==0) {
            response=await axios.get(`${apiUrl}/api/simple_search/`,{
            params:{
                index_name:indexName,
                field_name:"filename",
                field_value:ac
            }
            })
            results=response.data.results;
        }
        if (results.length>0) {
            replaced_accession_objects.push({
            accession_number:ac,
            sub_type:subType,
            results:results
            })
        }
    }
    return replaced_accession_objects;
}

// 处理表格选择变化
const handleSelectionChange = (selection) => {
    // 这里可以添加处理表格选择变化的逻辑
};

const sortColumns = (keys) => {
    const idKeys = [];
    const otherKeys = [];
    keys.forEach((key) => {
        if (key.endsWith('id')) {
            idKeys.push(key);
        } else {
            otherKeys.push(key);
        }
    });
    return [...idKeys, ...otherKeys];
};

const initTable = () => {
    if (Array.isArray(props.processedResults)) {
        if (props.processedResults.every(item => typeof item === 'string')) {
            // 如果列表元素都是字符串，将列表转换为一列的表格数据
            tableData.value = props.processedResults.map(item => ({ value: item }));
            columns.value = [{ label: 'Value', prop: 'value' }];
        } else {
            // 如果是数组，将数组作为表格数据
            tableData.value = props.processedResults;
            // 从数组第一个元素提取字段名作为列标签
            if (tableData.value.length > 0) {
                const keys = Object.keys(tableData.value[0]);
                const sortedKeys = sortColumns(keys);
                columns.value = sortedKeys.map((prop) => ({
                    label: prop,
                    prop
                }));
            }
        }
    } else {
        // 如果是对象，将对象转换为表格数据格式
        tableData.value = Object.entries(props.processedResults).map(([key, value]) => ({
            key,
            value
        }));
        const keys = ['key', 'value'];
        const sortedKeys = sortColumns(keys);
        columns.value = sortedKeys.map((prop) => ({
            label: prop === 'key' ? 'Field' : 'Value',
            prop
        }));
    }
    loading.value = false;
};

onMounted(() => {
    initTable();
});

watch(() => props.processedResults, () => {
    initTable();
});
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
    table-layout: fixed;
}

/* 保证每列有适当宽度 */
.el-table-column {
    min-width: 150px;
    word-wrap: break-word;
}

/* 弹窗样式 */
.el-dialog .el-button {
    margin-right: 10px;
}

/* 使按钮填充单元格 */
.el-table-column .el-button {
    display: block;
    width: 100%;
    height: 100%;
}
</style>