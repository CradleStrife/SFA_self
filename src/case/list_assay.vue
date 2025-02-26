<template>
  <el-container>
    <el-main>
      <!--------------------------------------------- First layer ----------------------------------------------------->
      <el-row type="flex" style="height: 100%;">
          <el-row type="flex" style="padding: 1em;">
            <el-col>
              <el-page-header @back="goBack" title="Back">
              </el-page-header>
              <h1>We found {{ processedResults.length }} result{{ processedResults.length !== 1 ? 's' : '' }} for your search</h1>
            </el-col>
        </el-row>

      <!--------------------------------------------- Search Results ------------------------------------------------->
      <el-row type="flex">
        <el-col :span="24">
          <el-scrollbar style="height: calc(100vh-210px);">
            <RecursiveTable 
              :processedResults="processedResults"
            />
          </el-scrollbar>
        </el-col>
      </el-row>
      </el-row>
    </el-main>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MapChart from '../components/MapChart.vue';
import EnquiryAssayTable from '../components/EnquiryAssayTable.vue';
import RecursiveTable from '../components/RecursiveTable.vue';
const logPerformance = (startTime: number, message: string) => {
const endTime = performance.now();
console.log(`${message}: ${endTime - startTime} ms`);
};

// const processedResults = ref<Array<{
// pmid: string;
// pmcid: string;
// title: string;
// abstract: string;
// authors: string;
// journal: string;
// year: string;
// url: string;
// doi: string;
// key_words: string;
// filename: string; 
// isolate_id: string; 
// isolate_source: string; 
// isolate_date: string; 
// isolate_country: string; 
// serotype: string; 
// mlst: string; 
// ast_data: string; 
// spi: string; 
// amr: string; 
// plasmid: string; 
// snp: string; 
// 'virulence genes': string; 
// 'accession numbers': string; 
// final_cleaned_text: string; 
// 'accession numbers_merge': string; 
// countryname: string
// }>>([]);

// Add showMore as a ref for managing state
const processedResults=ref<Array<any>>([]);

const showMore = ref<Array<boolean>>([]);

// Method to toggle the showMore state
const toggleShowMore = (index: number) => {
showMore.value[index] = !showMore.value[index];
};

// Function to truncate text to 20 words
const truncatedText = (text: string) => {
const words = text.split(' ');
if (words.length > 20) {
  return words.slice(0, 20).join(' ') + '...';
}
return text;
};

const mapChartData = ref<{ [key: string]: number }>({});
const delimiterPattern = /\s*(?:and|,|;)\s*/;
const router = useRouter();
const route = useRoute();

onMounted(() => {
const startTime = performance.now();
const storedResults = sessionStorage.getItem('searchResults');

console.log('storedResults', storedResults);

const updatedResult = route.query.updatedResult ? JSON.parse(route.query.updatedResult as string) : null;

if (storedResults) {
  const rawResults = JSON.parse(storedResults);
  // processedResults.value = rawResults.map((tuple: any) => ({
  //   pmid: tuple[0],
  //   pmcid: tuple[1],
  //   title: tuple[2],
  //   abstract: tuple[3],
  //   authors: tuple[4],
  //   journal: tuple[5],
  //   year: tuple[6],
  //   url: tuple[7],
  //   doi: tuple[8],
  //   key_words: tuple[9],
  //   filename: tuple[10],
  //   isolate_id: tuple[11],
  //   isolate_source: tuple[12],
  //   isolate_date: tuple[13],
  //   isolate_country: tuple[14],
  //   serotype: tuple[15],
  //   mlst: tuple[16],
  //   ast_data: tuple[17],
  //   spi: tuple[18],
  //   amr: tuple[19],
  //   plasmid: tuple[20],
  //   snp: tuple[21],
  //   'virulence genes': tuple[22],
  //   'accession numbers': tuple[23],
  //   final_cleaned_text: tuple[24],
  //   'accession numbers_merge': tuple[25],
  //   countryname: tuple[26]
  // }));
  processedResults.value=rawResults;


  showMore.value = Array(processedResults.value.length).fill(false);

  if (updatedResult) {
    const index = processedResults.value.findIndex(item => item.pmcid === updatedResult.pmcid);
    if (index !== -1) {
      processedResults.value[index] = updatedResult;
    }
  }

  // Process map data
  const countryCounts: { [key: string]: number } = {};
  processedResults.value.forEach(result => {
    if (result.countryname) {
      const countries = result.countryname.split(delimiterPattern);
      countries.forEach(countryname => {
        if (!countryCounts[countryname]) {
          countryCounts[countryname] = 0;
        }
        countryCounts[countryname] += 1;
      });
    }
  });

  mapChartData.value = countryCounts;
}
logPerformance(startTime, "Processing stored results and map data");
});

const handleUpdate = (index: number) => {
const selectedResult = processedResults.value[index];
sessionStorage.setItem('selectedResult', JSON.stringify(selectedResult));
router.push({ name: 'UpdatePage' });
};

const goBack = () => {
router.back();
};
</script>

<style scoped>
.result-box {
border: 1px solid #ddd;
padding: 10px;
margin-bottom: 10px;
text-align: left;
background-color: rgb(231, 231, 231);
}
</style>
