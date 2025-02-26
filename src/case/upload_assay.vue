<template>
    <div>
      <h3>Upload JSON Files</h3>
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
      <div v-if="uploading">Uploading...</div>
      <div v-if="uploadSuccess">Upload Successful!</div>
      <div v-if="uploadError">{{ uploadError }}</div>
      <h3>Existing Files</h3>
      <button @click="fetchFiles">Refresh List</button>
      <el-row>
        <el-col :span="15" :offset="4">
          <el-scrollbar style="height: 700px;">
            <table class="file-table">
              <thead>
                <tr>
                  <th>Filename</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="file in existingFiles" :key="file">
                  <td>{{ file }}</td>
                </tr>
              </tbody>
            </table>
          </el-scrollbar>
        </el-col>
      </el-row>
    </div>
  </template>
  
  
  
  <script lang="ts" setup>
  import { ref, getCurrentInstance, onMounted } from 'vue';
  import axios from 'axios';
  
  const instance = getCurrentInstance();
  if (!instance) {
    throw new Error("Failed to get current instance");
  }
  
  const apiUrl = instance.proxy?.$apiHost;
  if (!apiUrl) {
    throw new Error("API URL not found");
  }
  
  const files = ref<File[]>([]);
  const uploading = ref(false);
  const uploadSuccess = ref(false);
  const uploadError = ref<string | null>(null);
  const existingFiles = ref<string[]>([]);
  const dropped = ref(false);
  
  const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    files.value = Array.from(target.files);
    dropped.value = true;
  }
};

  const handleDrop = (event: DragEvent) => {
  const target = event.dataTransfer;
  if (target?.files) {
    files.value = Array.from(target.files);
    dropped.value = true;
  }
};
  
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
      const response = await axios.post(`${apiUrl}/api/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      if (response.status === 200) {
        uploadSuccess.value = true;
        fetchFiles(); // Refresh the file list after a successful upload
      } else {
        uploadError.value = `Upload failed with status code ${response.status}`;
      }
    } catch (error: any) {
      if (error.response && error.response.data && error.response.data.error) {
        uploadError.value = error.response.data.error;
      } else {
        uploadError.value = 'An unexpected error occurred. Please try again.';
      }
    } finally {
      uploading.value = false;
    }
  };
  
  const fetchFiles = async () => {
    try {
      const response = await axios.get(`${apiUrl}/api/list/`);
      if (response.status === 200) {
        existingFiles.value = response.data.files;
      } else {
        console.error('Failed to fetch files:', response.status);
      }
    } catch (error: any) {
      console.error('Failed to fetch files:', error);
    }
  };
  
  onMounted(() => {
    fetchFiles();
  });
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

.file-table {
  width: 100%; /* Use the full width of the column */
  border-collapse: collapse;
  margin: auto; /* Center the table within the column */
}

.file-table th,
.file-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.file-table th {
  background-color: #f2f2f2;
}

.el-scrollbar {
  max-height: 700px; /* Adjust the height as needed */
}
</style>

  

  