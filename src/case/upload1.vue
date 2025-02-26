<template>
  <div>
    <h3>Upload JSON Files</h3>
    <!-- 文件上传部分 -->
    <div 
      @dragover.prevent 
      @drop.prevent="handleDrop" 
      class="drag-and-drop-box">
      Drag and drop files here or 
      <input type="file" @change="handleFileUpload" multiple />
    </div>
    <div v-if="dropped" class="drop-success">
      <i class="fa fa-check-circle"></i> Files successfully dropped
    </div>

    <button @click="uploadFiles">Upload</button>
    <button @click="fetchTempData">Refresh Data</button>

    <div v-if="uploading">Uploading...</div>
    <div v-if="uploadSuccess">Upload Successful!</div>
    <div v-if="uploadError">{{ uploadError }}</div>

    <h3>Temporary Data (Total: {{ tempData.length }})</h3>
    

    <!-- 使用 UploadUnit 展示上传的数据 -->
    <el-row type="flex">
      <el-col :span="24">
        <el-scrollbar style="height: calc(100vh-250px)">
          <UploadTable :tempData="tempData" :apiUrl="apiUrl" />
        </el-scrollbar>
      </el-col>
    </el-row>

    <!-- 公用的 Confirm 和 Delete 按钮 -->
    <el-button
      size="mini"
      type="primary"
      icon="el-icon-check"
      plain
      @click="handleBatchConfirm"
    >
      Confirm
    </el-button>
    <el-button
      size="mini"
      type="primary"
      icon="el-icon-delete"
      plain
      @click="handleBatchDelete"
    >
      Delete
    </el-button>

    <!-- 操作结果弹窗 -->
    <el-dialog v-model="batchOperationDialogVisible" title="Batch Operation Result" width="50%">
      <div>
        <p v-if="batchSuccess.length > 0">Successfully processed messages: {{ batchSuccess.join('<br>') }}</p>
        <p v-if="batchFailure.length > 0">Failed to process messages: {{ batchFailure.join('<br>') }}</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="batchOperationDialogVisible = false">Close</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import UploadTable from '~/components/UploadTable.vue'; 
import EnquiryUnit from "../components/EnquiryUnit.vue"; // 确保路径正确


// 初始化 API 地址
const apiUrl = "http://localhost:8000"; // 替换为实际 API 地址

// 文件上传状态
const files = ref<File[]>([]);
const uploading = ref(false);
const uploadSuccess = ref(false);
const uploadError = ref<string | null>(null);
const dropped = ref(false);

// 缓存区数据
const tempData = ref<any[]>([]);
const batchOperationDialogVisible = ref(false);
const batchSuccess = ref<string[]>([]);
const batchFailure = ref<string[]>([]);


onMounted(() => {
  fetchTempData();
});

// 文件选择事件处理
const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    files.value = Array.from(target.files);
    dropped.value = true;
  }
};

// 拖拽文件事件处理
const handleDrop = (event: DragEvent) => {
  const target = event.dataTransfer;
  if (target?.files) {
    files.value = Array.from(target.files);
    dropped.value = true;
  }
};


// 上传文件到缓存区
const uploadFiles = async () => {
  if (files.value.length === 0) {
    alert('Please select files to upload.');
    return;
  }

  uploading.value = true;
  uploadSuccess.value = false;
  uploadError.value = null;

  const formData = new FormData();
  files.value.forEach(file => {
    formData.append('files', file);
  });

  try {
    const response = await axios.post(`${apiUrl}/api/upload2temp/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    if (response.status === 200) {
      uploadSuccess.value = true;
      // console.log('Files uploaded successfully:', response.data);
      fetchTempData(); // 上传成功后刷新缓存区数据
    } else {
      uploadError.value = `Upload failed with status code ${response.status}`;
    }
  } catch (error: any) {
    uploadError.value = 'An unexpected error occurred. Please try again.';
    console.error('Upload error:', error);
  } finally {
    uploading.value = false;
  }
};

// 获取缓存区数据
const fetchTempData = async () => {
  try {
    const response = await axios.get(`${apiUrl}/api/getTempData/`);
    if (response.status === 200) {
      tempData.value = response.data.results.map((item) => ({
        selected: false, // 确保添加 selected 属性
        ID: item[0],
        Source: item[1],
        Date: item[2],
        Country: item[3],
        Brand: item[4],
        Serotype: item[5],
        MLST: item[6],
        AST: item[7],
        SPI: item[8],
        AMR: item[9],
        Plasmid: item[10],
        fileName: item[11],
      }));
    } else {
      console.error("Failed to fetch temporary data:", response.status);
    }
  } catch (error) {
    console.error("Error fetching temporary data:", error);
  }
};


// 确认单条数据
const confirmResult = async (index, row) => {
  const file = tempData.value[index];
  try {
    // 确保 ID 是字符串
    const response = await axios.post(`${apiUrl}/api/confirmTemp2es/`, { ID: file.ID[0] });
    if (response.status === 200) {
      tempData.value.splice(index, 1); // 从前端移除文件
      return `File ${file.ID[0]} confirmed and uploaded successfully.`;
    } else {
      return `Error confirming file ${file.ID[0]}: File already exists or wrong format.`;
    }
  } catch (error) {
    console.error("Error confirming file:", error);
    return `Error confirming file ${file.ID[0]}: An unexpected error occurred.`;
  }
};


// 删除单条数据
const deleteResult = async (index, row) => {
  console.log('deleteResult');
  const file = tempData.value[index];
  try {
    await axios.post(`${apiUrl}/api/deleteTempData/`, { ID: file.ID[0] });
    tempData.value.splice(index, 1); // 刪除後移除
    return `File ${file.ID[0]} deleted successfully.`;
  } catch (error) {
    console.error('Error deleting file:', error);
    console.error('Error response data:', error.response? error.response.data : 'No response data');
    console.error('Error response status:', error.response? error.response.status : 'No response status');
    console.error('Error response headers:', error.response? error.response.headers : 'No response headers');
    return `Error deleting file ${file.ID[0]}: An unexpected error occurred.`;
  }
};


// 批量确认数据
const handleBatchConfirm = async () => {
  console.log('handleBatchConfirm');
  batchSuccess.value = [];
  batchFailure.value = [];
  const selectedItems = tempData.value.filter(item => item.selected);
  console.log('selectedItems:', selectedItems);
  for (let i = 0; i < selectedItems.length; i++) {
    const index = tempData.value.indexOf(selectedItems[i]);
    const row = selectedItems[i];
    const result = await confirmResult(index, row);
    if (result.includes('successfully')) {
      batchSuccess.value.push(result);
    } else {
      batchFailure.value.push(result);
    }
  }
  batchOperationDialogVisible.value = true;
};


// 批量删除数据
const handleBatchDelete = async () => {
  console.log('handleBatchDelete');
  console.log('tempData:', tempData.value);
  batchSuccess.value = [];
  batchFailure.value = [];
  const selectedItems = tempData.value.filter(item => item.selected);
  console.log('selectedItems:', selectedItems);
  if (selectedItems.length === 0) {
    alert('Please select at least one item to delete.');
    return;
  }
  for (let i = 0; i < selectedItems.length; i++) {
    const index = tempData.value.indexOf(selectedItems[i]);
    const row = selectedItems[i];
    const result = await deleteResult(index, row);
    if (result.includes('successfully')) {
      batchSuccess.value.push(result);
    } else {
      batchFailure.value = batchFailure.value.concat(result);
    }
  }
  batchOperationDialogVisible.value = true;
};
</script>

<style scoped>
.drag-and-drop-box {
  border: 2px dashed #ccc;
  border-radius: 5px;
  padding: 20px;
  text-align: center;
  margin-bottom: 10px;
  cursor: pointer;
}

.drag-and-drop-box:hover {
  background-color: #f9f9f9;
}

.drop-success {
  color: green;
  font-size: 1.2em;
  margin-bottom: 20px;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-box {
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 5px;
}

.el-scrollbar {
  max-height: 400px;
  overflow-y: auto;
}

.confirm-all {
  margin-top: 20px;
  margin-bottom: 20px;
  text-align: center;
}

.confirm-all-btn {
  background-color: #28a745;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.confirm-all-btn:hover {
  background-color: #218838;
}
</style>