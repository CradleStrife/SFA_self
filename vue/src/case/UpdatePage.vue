


<!------------------------------------------------- For LOCAL DATA SET -------------------------------------------------->
<template>
  <el-container>
    <el-main>
      <el-row type="flex" style="height: 100%;">
        <el-row type="flex" style="padding: 1em;">
          <el-col>
            <el-page-header @back="goBack" title="Back"></el-page-header>
          </el-col>
        </el-row>
        <el-row type="flex" style="width: 100%; padding: 1em;">
          <el-col :span="24">
            <div v-if="result">
              <el-form :model="result" label-width="150px">
                <el-form-item label="ID">
                  <el-input v-model="result.ID" style="width: 100%;"></el-input>
                </el-form-item>
                <el-form-item label="Source">
                  <el-input v-model="result.Source" style="width: 100%;"></el-input>
                </el-form-item>
                <el-form-item label="Date">
                  <el-input v-model="result.Date" style="width: 100%;"></el-input>
                </el-form-item>
                <el-form-item label="Country">
                  <el-input v-model="result.Country" style="width: 100%;"></el-input>
                </el-form-item>
                <el-form-item label="Brand">
                  <el-input v-model="result.Brand" style="width: 100%;"></el-input>
                </el-form-item>
                <el-form-item label="Serotype">
                  <el-input v-model="result.Serotype" style="width: 100%;"></el-input>
                </el-form-item>
                <el-form-item label="MLST">
                  <el-input v-model="result.MLST" style="width: 100%;"></el-input>
                </el-form-item>
                <el-form-item label="AST">
                  <el-input v-model="astString" style="width: 100%;" ></el-input>
                    <el-button type="danger" @click="clearAST">Clear AST</el-button>
                    <el-button type="info" @click="showHelp">Help</el-button>
                </el-form-item>
                <el-form-item label="SPI">
                  <el-input v-model="result.SPI" style="width: 100%;"></el-input>
                </el-form-item>
                <el-form-item label="AMR">
                  <el-input v-model="result.AMR" style="width: 100%;"></el-input>
                </el-form-item>
                <el-form-item label="PLASMID">
                  <el-input v-model="result.plasmid" style="width: 100%;"></el-input>
                </el-form-item>
                <!-- Add other form items as needed -->
                <el-form-item>
                  <el-button type="primary" @click="saveChanges">Save</el-button>
                </el-form-item>
              </el-form>
            </div>
            <div v-else>
              <p>Loading data...</p>
            </div>
          </el-col>
        </el-row>
      </el-row>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, getCurrentInstance } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';

const instance = getCurrentInstance();
if (!instance) {
  throw new Error("Failed to get current instance");
}

const apiUrl = instance.proxy?.$apiHost;
if (!apiUrl) {
  throw new Error("API URL not found");
}

// Define the result ref with all the necessary properties
const result = ref<{
  ID: string;
  Source: string;
  Date: string;
  Country: string;
  Brand: string;
  Serotype: string;
  MLST: string;
  AST: any;  // Changed to any to accommodate the object
  SPI: string;
  AMR: string;
  plasmid: string;
} | null>(null);

const route = useRoute();
const router = useRouter();

onMounted(() => {
  const storedResult = sessionStorage.getItem('selectedResult');
  if (storedResult) {
    result.value = JSON.parse(storedResult);
    console.log("Result:", result.value);
  } else {
    ElMessage.error('No data found to update.');
    router.push({ name: 'result-ListView' });
  }
});

const astString = computed({
  get() {
    return result.value ? JSON.stringify(result.value.AST, null, 2) : '';
  },
  set(value) {
    if (result.value) {
      result.value.AST = JSON.parse(value);
    }
  }
});
const clearAST = () => {
  if (result.value) {
    result.value.AST = {};  // Clear AST field
  }
};

const showHelp = () => {
  ElMessageBox.alert('Please enter the AST field in JSON format. Example: { "input" : ["input"], "input" : ["input"] }', 'AST Field Help', {
    confirmButtonText: 'OK',
    type: 'info',
  });
};
const saveChanges = async () => {
  if (result.value) {
    try {
      // Validate and parse the AST field before saving
      result.value.AST = JSON.parse(astString.value);
    } catch (error) {
      ElMessage.error('Invalid JSON format for AST, please enter it in this format, { "input" : ["input"] },{ "input" : ["input"] }');
      return;  // Exit the function if the JSON is invalid
    }

    try {
      const response = await axios.post(`${apiUrl}/api/update_document/`, result.value);
      if (response.data.status === 'success') {
        ElMessage.success('Changes saved successfully!');
        router.push({ name: 'result-ListView', query: { updatedResult: JSON.stringify(result.value) } });
      } else {
        ElMessage.error('Failed to save changes.');
      }
    } catch (error) {
      ElMessage.error('An error occurred while saving changes.');
    }
  }
};

const goBack = () => {
  router.back();
};
</script>




<!------------------------------------ For Assay information  ----------------------------------------------------------->
<!-- <template>
  <el-container>
    <el-main>
      <el-row type="flex" style="height: 100%;">
        <el-row type="flex" style="padding: 1em;">
          <el-col>
            <el-page-header @back="goBack" title="Back to Menu"></el-page-header>             
          </el-col>
        </el-row>
      <el-row type="flex" style="width: 100%; padding: 1em;">
        <el-col :span="24">
        <div v-if="result">
          <el-form :model="result" label-width="150px">
            <el-form-item label="Title">
              <el-input v-model="result.title" style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="Pub_Country">
              <el-input v-model="result.pub_country" style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="Pub_Year">
              <el-input v-model="result.pub_year"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="Keywords">
              <el-input v-model="result.keywords"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="Source">
              <el-input v-model="result.source"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="Date">
              <el-input v-model="result.date"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="Country">
              <el-input v-model="result.country"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="Serotype">
              <el-input v-model="result.serotype"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="MLST">
              <el-input v-model="result.mlst"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="AST">
              <el-input v-model="result.ast"  style="width: 100%;" placeholder='Please indicate your input in this format if not you will not be able to saved it = { "input" : "input" } for example, {"NA":"NA"}'></el-input>
            </el-form-item>
            <el-form-item label="SPI">
              <el-input v-model="result.spi"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="AMR">
              <el-input v-model="result.amr"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="PLASMID">
              <el-input v-model="result.plasmid"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="SNP">
              <el-input v-model="result.snp"  style="width: 100%;"></el-input>
            </el-form-item>
            <el-form-item label="VIRULENCE_GENES">
              <el-input v-model="result.virulence_genes"  style="width: 100%;"></el-input>
            </el-form-item>
            Add other form items as needed
            <!-- <el-form-item>
              <el-button type="primary" @click="saveChanges">Save</el-button>
            </el-form-item>
          </el-form>
        </div>
        <div v-else>
          <p>Loading data...</p>
        </div>
        </el-col>
      </el-row>
    </el-row>
    </el-main>
  </el-container> 
</template>

<script lang="ts" setup>
import { ref, onMounted, getCurrentInstance } from 'vue';  
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import axios from 'axios';

const instance = getCurrentInstance();
if (!instance) {
  throw new Error("Failed to get current instance");
}

const apiUrl = instance.proxy?.$apiHost;
if (!apiUrl) {
  throw new Error("API URL not found");
}

// Define the result ref with all the necessary properties
const result = ref<{
  title: string;
  country: string;
  description: string;
  pmcid: string;
  abstract: string;
  url: string;
  pub_country: string;
  pub_year: string;
  doi: string;
  case: string;
  keywords: string;
  id: string;
  source: string;
  date: string;
  brand: string;
  serotype: string;
  mlst:  string;
  ast:  string;
  spi:  string;
  amr:  string;
  plasmid:  string;
  snp:  string;
  virulence_genes:  string;
} | null>(null);

const route = useRoute();
const router = useRouter();

onMounted(() => {
  const storedResult = sessionStorage.getItem('selectedResult');
  if (storedResult) {
    result.value = JSON.parse(storedResult);
    console.log("Result:", result.value);
  } else {
    ElMessage.error('No data found to update.');
    router.push({ name: 'result-ListView' });
  }
});

const saveChanges = async () => {
  if (result.value) {
    try {
      const response = await axios.post(`${apiUrl}/api/update_document/`, result.value);
      if (response.data.status === 'success') {
        ElMessage.success('Changes saved successfully!');
        router.push({ name: 'result-ListView', query: { updatedResult: JSON.stringify(result.value) } });
      } else {
        ElMessage.error('Failed to save changes.');
      }
    } catch (error) {
      ElMessage.error('An error occurred while saving changes.');
    }
  }
};

const goBack = () => {
  router.back();
};
</script> --> -->
