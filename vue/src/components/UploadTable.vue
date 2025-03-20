<template>
  <div class="result-box">
    <!-- 创建一个表格，所有信息都在表格中展示 -->
    <el-table
      ref="tableRef"
      :data="currentPageData"
      style="width: 100%"
      max-height="800px"
      border
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55">
        <template #header>
          <el-checkbox
            :indeterminate="isIndeterminate"
            :checked="isAllSelected"
            @change="handleAllSelectChange"
          ></el-checkbox>
        </template>
      </el-table-column>
      <el-table-column label="fileName" prop="fileName"></el-table-column>
      <el-table-column label="ID" prop="ID"></el-table-column>
      <el-table-column label="Date" prop="Date"></el-table-column>
      <el-table-column label="Serotype" prop="Serotype"></el-table-column>
      <el-table-column label="Source" prop="Source"></el-table-column>
      <el-table-column label="Country" prop="Country"></el-table-column>
      <el-table-column label="Brand" prop="Brand"></el-table-column>
      <el-table-column label="MLST" prop="MLST"></el-table-column>

      <el-table-column label="AST">
        <template #default="{ row }">
          <el-button
            size="mini"
            style="width: 100%; height: 100%;"
            @click="openDialog('AST', row.AST)"
          >
            View
          </el-button>
        </template>
      </el-table-column>

      <el-table-column label="SPI">
        <template #default="{ row }">
          <el-button
            size="mini"
            style="width: 100%; height: 100%;"
            @click="openDialog('SPI', row.SPI)"
          >
            View
          </el-button>
        </template>
      </el-table-column>

      <el-table-column label="AMR">
        <template #default="{ row }">
          <el-button
            size="mini"
            style="width: 100%; height: 100%;"
            @click="openDialog('AMR', row.AMR)"
          >
            View
          </el-button>
        </template>
      </el-table-column>

      <el-table-column label="Plasmid">
        <template #default="{ row }">
          <el-button
            size="mini"
            style="width: 100%; height: 100%;"
            @click="openDialog('Plasmid', row.Plasmid)"
          >
            View
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页组件 -->
    <el-pagination
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-sizes="[50, 100, 150]"
      :page-size="pageSize"
      layout="total, sizes, prev, pager, next, jumper"
      :total="tempData.length"
    >
    </el-pagination>

    <!-- 全选按钮 -->
    <el-checkbox
      :indeterminate="isAllDataIndeterminate"
      :checked="isAllDataSelected"
      @change="handleAllDataSelectChange"
    >
      Select All in All Pages
    </el-checkbox>

    <!-- 弹出框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="50%">
      <!-- 判断 dialogContent 是否为数组 -->
      <div v-if="Array.isArray(dialogContent)">
        <!-- 使用 el-table 展示，并设置最大高度和滚动条 -->
        <el-table
          :data="dialogContent.map((item) => ({ item }))"
          style="width: 100%; max-height: 300px; overflow-y: auto;"
        >
          <el-table-column label="" prop="item"></el-table-column>
        </el-table>
      </div>
      <!-- 如果不是数组，显示为文本 -->
      <div v-else>
        <!-- 创建表格 -->
        <el-table
          :data="formattedData"
          style="width: 100%; max-height: 300px; overflow-y: auto;"
        >
          <el-table-column label="#" prop="index"></el-table-column>
          <el-table-column label="Name" prop="name"></el-table-column>
          <el-table-column label="Interpretation" prop="interpretation"></el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import axios from 'axios';

// 定义 props
const props = defineProps({
  tempData: {
    type: Array as () => any[],
    required: true
  },
  apiUrl: {
    type: String,
    required: true
  }
});

// 定义 emits
const emits = defineEmits(['selectionChange']);

// 定义响应式数据
const dialogVisible = ref(false);
const dialogTitle = ref('');
const dialogContent = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const selectedRows = ref<any[]>([]);
const tableRef = ref<InstanceType<typeof ElTable> | null>(null);
const isDataLoaded = ref(false); // 新增状态标记数据是否加载完成

// 模拟数据加载完成
// 在实际应用中，这里可以根据数据获取的逻辑来更新 isDataLoaded
// 例如使用 axios 获取数据，在请求成功的回调中设置 isDataLoaded 为 true
isDataLoaded.value = true;

// 计算当前页数据
const currentPageData = computed(() => {
  if (!isDataLoaded.value) return [];
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return props.tempData.slice(start, end);
});

// 计算单页全选状态
const isAllSelected = computed(() => {
  if (!isDataLoaded.value) return false;
  return selectedRows.value.length === currentPageData.value.length && currentPageData.value.length > 0;
});

// 计算单页部分选中状态
const isIndeterminate = computed(() => {
  if (!isDataLoaded.value) return false;
  return selectedRows.value.length > 0 && selectedRows.value.length < currentPageData.value.length;
});

// 计算全量数据全选状态
const isAllDataSelected = computed(() => {
  if (!isDataLoaded.value) return false;
  return selectedRows.value.length === props.tempData.length && props.tempData.length > 0;
});


// 计算全量数据部分选中状态
const isAllDataIndeterminate = computed(() => {
  if (!isDataLoaded.value) return false;
  return selectedRows.value.length > 0 && selectedRows.value.length < props.tempData.length;
});

// 格式化弹窗内容数据
const formattedData = computed(() => {
  if (!isDataLoaded.value) return [];
  return Object.keys(dialogContent.value).map((key) => {
    const item = dialogContent.value[key];
    const drugName = Object.keys(item)[0];
    const interpretation = item[drugName][0];
    return {
      index: key,
      name: drugName,
      interpretation
    };
  });
});

// 打开弹窗
const openDialog = (field: string, value: any) => {
  dialogTitle.value = field;
  dialogContent.value = value || 'No data available';
  dialogVisible.value = true;
};

// 处理表格行选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection;
  emits('selectionChange', selection);
};

// 处理单页全选
const handleAllSelectChange = (checked: boolean) => {
  if (checked) {
    tableRef.value?.toggleAllSelection();
  } else {
    tableRef.value?.clearSelection();
  }
};

// 处理全量数据全选
const handleAllDataSelectChange = (checked: boolean) => {
  if (checked) {
    selectedRows.value = [...props.tempData];
  } else {
    selectedRows.value = [];
    // 清除当前页的选中状态
    tableRef.value?.clearSelection();
  }
  emits('selectionChange', selectedRows.value);
};

// 处理每页显示数量变化
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize;
};

// 处理页码变化
const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage;
  // 切换页码时清除当前页选中状态
  tableRef.value?.clearSelection();
  selectedRows.value = [];
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