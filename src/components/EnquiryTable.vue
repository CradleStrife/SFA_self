<template>
    <div class="result-box">
      <!-- 创建一个表格，所有信息都在表格中展示 -->
      <el-table :data="processedResults" style="width: 100%" max-height="800px" border>
        <!-- <el-table-column type="selection" width="55"></el-table-column> -->
        <el-table-column label="Edit">
          <template #default="{ row, $index }">
            <el-button 
              size="mini" 
              type="primary"
              @click="handleEdit($index, row)">
              Edit
            </el-button>
          </template>
        </el-table-column>
        
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
              @click="openDialog('AST', row.AST)">
              View
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="SPI">
          <template #default="{ row }">
            <el-button 
              size="mini" 
              style="width: 100%; height: 100%;" 
              @click="openDialog('SPI', row.SPI)">
              View
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="AMR">
          <template #default="{ row }">
            <el-button 
              size="mini" 
              style="width: 100%; height: 100%;" 
              @click="openDialog('AMR', row.AMR)">
              View
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="Plasmid">
          <template #default="{ row }">
            <el-button 
              size="mini" 
              style="width: 100%; height: 100%;" 
              @click="openDialog('Plasmid', row.plasmid)">
              View
            </el-button>
          </template>
        </el-table-column>
        
      </el-table>
  
      <!-- 弹出框 -->
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="50%">
        <!-- 判断 dialogContent 是否为数组 -->
        <div v-if="Array.isArray(dialogContent)">
          <!-- 使用 el-table 展示，并设置最大高度和滚动条 -->
          <el-table :data="dialogContent.map(item => ({ item }))" style="width: 100%; max-height: 300px; overflow-y: auto;">
            <el-table-column label="" prop="item"></el-table-column>
          </el-table>
        </div>
        <!-- 如果不是数组，显示为文本 -->
        <div v-else>
          <!-- 创建表格 -->
          <el-table :data="formattedData" style="width: 100%; max-height: 300px; overflow-y: auto;">
            <!-- <el-table-column label="#" prop="index"></el-table-column> -->
            <el-table-column label="Name" prop="index"></el-table-column>
            <el-table-column label="Interpretation" prop="interpretation"></el-table-column>
          </el-table>
        </div>
      </el-dialog>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    props: {
      processedResults: {
        type: Array,
        required: true
      }
    },
    data() {
      return {
        dialogVisible: false,
        dialogTitle: '',
        dialogContent: ''
      };
    },
    methods: {
      // 打开弹窗并显示对应字段的完整内容
      openDialog(field, value) {
        this.dialogTitle = field; // 设置弹窗标题为字段名
        let content = value || 'No data available';
        // 尝试将字符串形式的数组转换为真正的数组
        if (typeof content === 'string') {
            // 尝试处理非标准格式，例如替换单引号为双引号
            content = this.replaceQuotes(content);
            try {
            content = JSON.parse(content);
            } catch (error) {
            console.error('Failed to parse string as array:', error);
            }
        }
        this.dialogContent = content; // 设置弹窗内容
        console.log(typeof content, content);
        this.dialogVisible = true; // 显示弹窗
      },
      replaceQuotes(str) {
        return str.replace(/'/g, '"');
      },
      
      handleSelectionChange(selection) {
        // 更新 processedResults 中的 selected 属性
        this.processedResults.forEach(item => {
          item.selected = selection.some(selectedItem => selectedItem.ID === item.ID);
        });
      },
      handleEdit(index, row) {
        // 触发父组件的 edit 事件，传递 index 和 row
        this.$emit('edit', index, row);
      }
    },
    computed: {
      formattedData() {
        return Object.keys(this.dialogContent).map(key => {
          const item = this.dialogContent[key];
          const drugName = Object.keys(item)[0];  // 药物名称
          const interpretation = item[drugName][0];  // 解释
          return {
            index: key,
            name: drugName,
            interpretation
          };
        });
      }
    },
    // mounted() {
    //   // 在组件挂载完成后，处理 processedResults 中的单引号
    //   this.processedResults.forEach(item => {
    //     for (const key in item) {
    //       if (typeof item[key] === 'string' && item[key].startsWith("['") && item[key].endsWith("']")) {
    //         item[key]=item[key].slice(2,-2)
    //       }
    //     }
    //   });
    // }
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