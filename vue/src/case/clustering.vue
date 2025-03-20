<template>
  <div
    style="
      display: flex;
      flex-direction: column;
      height: 400vh;
      overflow-y: scroll;
    "
  >
    <!-- New Section -->
    <div class="settings-section">
      <div class="three-settings">
        <!-- Left Side: Attributes for clustering -->
        <div style="flex: 1; margin-right: 5px">
          <h2 style="text-align: center; margin-bottom: 10px">
            Attributes for clustering
          </h2>
          <!-- Content for Attributes for clustering -->
          <div
            style="
              background-color: #ffffff;
              padding: 20px;
              border-radius: 8px;
              box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            "
          >
            <label>Choose any of 'AST, SPI, AMR, or plasmid' as input:</label>
            <el-checkbox-group v-model="selectedAttributesForClustering">
              <el-checkbox label="AST"></el-checkbox>
              <el-checkbox label="SPI"></el-checkbox>
              <el-checkbox label="AMR"></el-checkbox>
              <el-checkbox label="plasmid"></el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
        <!-- Middle: General data filter -->
        <div style="flex: 1; margin-left: 10px">
          <h2 style="text-align: center; margin-bottom: 10px">
            General data filter
          </h2>
          <!-- Filters -->
          <div
            style="
              background-color: #ffffff;
              padding: 20px;
              border-radius: 8px;
              box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            "
          >
            <!-- First row: Datastore filter -->
            <div style="margin-bottom: 20px">
              <label>Datastore:</label>
              <el-select
                v-model="selectedDatastoreMultiple"
                placeholder="Select Datastore"
                style="width: 100%"
                multiple
              >
                <el-option
                  v-for="index_name in allIndexNames"
                  :value="index_name"
                ></el-option>
              </el-select>
            </div>
            <!-- Second row: Date Range filter -->
            <div style="margin-bottom: 20px">
              <label>Date Range:</label>
              <el-date-picker
                v-model="selectedDateRange"
                type="daterange"
                unlink-panels
                range-separator="To"
                start-placeholder="Start Date"
                end-placeholder="End Date"
                style="width: 100%"
              >
              </el-date-picker>
            </div>
            <!-- Third row: Attribute and Value filters -->
            <div>
              <label>Attributes filtering</label>
              <div
                v-for="(filter, index) in attributeFilters"
                :key="index"
                style="display: flex; align-items: center; margin-bottom: 10px"
              >
                <!-- Select Attribute -->
                <el-select
                  v-model="filter.attribute"
                  placeholder="Select Attribute"
                  style="flex: 1; margin-right: 10px"
                  @change="onAttributeChange(index)"
                >
                  <el-option
                    v-for="attr in attributes"
                    :key="attr"
                    :label="attr"
                    :value="attr"
                  ></el-option>
                </el-select>
                <!-- Select Value -->
                <el-select
                  v-model="filter.value"
                  placeholder="Select Value"
                  style="flex: 1; margin-right: 10px"
                >
                  <el-option
                    v-for="val in filter.values"
                    :key="val"
                    :label="val"
                    :value="val"
                  ></el-option>
                </el-select>
                <!-- Remove Filter Button with Text -->
                <el-button icon="el-icon-minus" @click="removeFilter(index)">
                  remove
                </el-button>
              </div>
              <!-- Add Filter Button -->
              <el-button type="primary" icon="el-icon-plus" @click="addFilter">
                Add Filter
              </el-button>
            </div>
          </div>
        </div>
        <!-- Right Side: Highlighted data filter (multiple clustering) -->
        <div style="flex: 1; margin-right: 10px">
          <h2 style="text-align: center; margin-bottom: 10px">
            Highlighted data filter (multiple clustering)
          </h2>
          <!-- Filters for highlighted data (multiple clustering) -->
          <div
            style="
              background-color: #ffffff;
              padding: 20px;
              border-radius: 8px;
              box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            "
          >
            <!-- Datastore filter -->
            <div style="margin-bottom: 20px">
              <label>Datastore:</label>
              <el-select
                v-model="highlightedDatastoreMultiple"
                placeholder="Select Datastore"
                style="width: 100%"
                multiple
              >
                <el-option
                  v-for="index_name in allIndexNames"
                  :value="index_name"
                ></el-option>
              </el-select>
              <!-- <el-checkbox-group>
              <el-checkbox v-for="index_name in allIndexNames" :value="index_name"></el-checkbox>
            </el-checkbox-group> -->
            </div>
            <!-- Date Range filter -->
            <div style="margin-bottom: 20px">
              <label>Date Range:</label>
              <el-date-picker
                v-model="selectedDateRangeMultiple"
                type="daterange"
                unlink-panels
                range-separator="To"
                start-placeholder="Start Date"
                end-placeholder="End Date"
                style="width: 100%"
              >
              </el-date-picker>
            </div>
            <!-- Clusterings -->
            <div
              v-for="(clustering, clusteringIndex) in clusterings"
              :key="clusteringIndex"
              style="margin-bottom: 20px"
            >
              <h3>Clustering {{ clusteringIndex + 1 }}</h3>
              <!-- Attribute Filters -->
              <div>
                <label>Attributes filtering</label>
                <div
                  v-for="(filter, index) in clustering.attributeFilters"
                  :key="index"
                  style="
                    display: flex;
                    align-items: center;
                    margin-bottom: 10px;
                  "
                >
                  <!-- Select Attribute -->
                  <el-select
                    v-model="filter.attribute"
                    placeholder="Select Attribute"
                    style="flex: 1; margin-right: 10px"
                    @change="onAttributeChangeMultiple(clusteringIndex, index)"
                  >
                    <el-option
                      v-for="attr in attributesMultiple"
                      :key="attr"
                      :label="attr"
                      :value="attr"
                    ></el-option>
                  </el-select>
                  <!-- Select Value -->
                  <el-select
                    v-model="filter.value"
                    placeholder="Select Value"
                    style="flex: 1; margin-right: 10px"
                  >
                    <el-option
                      v-for="val in filter.values"
                      :key="val"
                      :label="val"
                      :value="val"
                    ></el-option>
                  </el-select>
                  <!-- Remove Filter Button with Text -->
                  <el-button
                    icon="el-icon-minus"
                    @click="removeFilterMultiple(clusteringIndex, index)"
                  >
                    remove
                  </el-button>
                </div>
                <!-- Add Filter Button -->
                <el-button
                  type="primary"
                  icon="el-icon-plus"
                  @click="addFilterMultiple(clusteringIndex)"
                >
                  Add Filter
                </el-button>
              </div>
              <!-- ID Filters -->
              <div style="margin-top: 20px">
                <label>Select one by ID</label>
                <div
                  v-for="(filter, index) in clustering.idFilters"
                  :key="index"
                  style="
                    display: flex;
                    align-items: center;
                    margin-bottom: 10px;
                  "
                >
                  <!-- Select ID -->
                  <el-select
                    v-model="filter.id"
                    placeholder="Select ID"
                    style="flex: 1; margin-right: 10px"
                  >
                    <el-option
                      v-for="id in idValuesMultiple"
                      :key="id"
                      :label="id"
                      :value="id"
                    ></el-option>
                  </el-select>
                  <!-- Remove Filter Button with Text -->
                  <el-button
                    icon="el-icon-minus"
                    @click="removeIdFilterMultiple(clusteringIndex, index)"
                  >
                    remove
                  </el-button>
                </div>
                <!-- Add ID Filter Button -->
                <el-button
                  type="primary"
                  icon="el-icon-plus"
                  @click="addIdFilterMultiple(clusteringIndex)"
                >
                  Add Filter
                </el-button>
              </div>
              <!-- Remove Clustering Button -->
              <div style="margin-top: 10px">
                <el-button
                  v-if="clusteringIndex > 0"
                  type="danger"
                  icon="el-icon-delete"
                  @click="removeClustering(clusteringIndex)"
                >
                  Remove Clustering
                </el-button>
              </div>
            </div>
            <!-- Add Clustering Button -->
            <el-button
              type="primary"
              icon="el-icon-plus"
              @click="addClustering"
            >
              Add Clustering
            </el-button>
          </div>
        </div>
      </div>

      <div style="flex: 1;">

        <div style="margin-top: 20px">
          <p>Clustering Algorithm:</p>
          <el-select v-model="selectedAlgorithm" placeholder="Method">
            <el-option
              v-for="algorithm in clusteringAlgorithms"
              :key="algorithm"
              :label="algorithm"
              :value="algorithm"
            ></el-option>
          </el-select>
        </div>

        <div v-if="selectedAlgorithm===clusteringAlgorithms[0]" style="margin-top: 20px">
          <p>Method:</p>
          <el-select v-model="selectedAgnesMethod" placeholder="Method">
            <el-option
              v-for="method in agnesMethods"
              :key="method"
              :label="method"
              :value="method"
            ></el-option>
          </el-select>
        </div>

        <div v-if="selectedAlgorithm===clusteringAlgorithms[1]" style="margin-top: 20px">
          <p>Distance Function:</p>
          <el-select v-model="selectedDistFuncHdbs" placeholder="Method">
            <el-option
              v-for="func in distFuncHdbs"
              :key="func"
              :label="func"
              :value="func"
            ></el-option>
          </el-select>
        </div>

        <div v-if="selectedAlgorithm===clusteringAlgorithms[2]" style="margin-top: 20px">
          <p>Distance Function:</p>
          <el-select v-model="selectedDistFuncHcluster" placeholder="Method">
            <el-option
              v-for="func in distFuncHcluster"
              :key="func"
              :label="func"
              :value="func"
            ></el-option>
          </el-select>

          <p>Linkage:</p>
          <el-select v-model="selectedLinkageHcluster" placeholder="Method">
            <el-option
              v-for="linkage in linkageHcluster"
              :key="linkage"
              :label="linkage"
              :value="linkage"
            ></el-option>
          </el-select>
        </div>

      </div>

      <!-- Run Button -->
      <div style="margin-top: 20px">
        <el-button v-if="!loading"
          type="primary"
          style="width: 100%; height: 50px"
          @click="onRunButtonClick"
        >
          Run
        </el-button>
        <p v-else style="text-align: center; margin-top: 20px">Loading...</p>
      </div>
    </div>

    <!-- Upper Section -->
    <div class="clustering-section">
      <!-- Left Side: Tree Chart -->
      <div style="flex: 3; position: relative">
        <h2 style="text-align: center; margin-bottom: 10px">
          Cluster Grouping Tree Chart
        </h2>

        <!-- Clustering Selector -->
        <div style="position: absolute; top: 10px; right: 10px">
          <el-select
            v-model="selectedClusteringIndex"
            placeholder="Select Clustering"
            style="width: 200px"
            @change="updateTree"
          >
            <el-option
              v-for="(clustering, index) in clusterings"
              :key="index"
              :label="'Clustering ' + (index + 1)"
              :value="index"
            ></el-option>
          </el-select>
        </div>

        <!-- Tree Chart -->
        <div
          style="
            display: flex;
            height: 100%;
            overflow-x: auto;
            overflow-y: auto;
          "
        >
          <svg id="chart" width="50%" height="100%" style="flex-grow: 1"></svg>
        </div>
      </div>

      <!-- Right Side: Slider + Overall Statistic -->
      <div
        style="
          flex: 3;
          margin-left: 20px;
          display: flex;
          flex-direction: column;
          height: 100%;
          overflow: hidden;
        "
      >
        <!-- Slider Module -->
        <div
          style="
            background-color: #f7f7f7;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
            flex: none;
          "
        >
          <h3>Number of clusters shown in tree chart: {{ clusterCount }}</h3>
          <el-slider
            v-model="clusterCount"
            :min="3"
            :max="maxClusterCount"
            @input="updateTree"
          ></el-slider>
        </div>

        <!-- New Slider Module for Statistic -->
        <div
          style="
            background-color: #f7f7f7;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
            flex: none;
          "
        >
          <h3>
            Number of clusters selected for statistic: {{ numberOfNodes }}
          </h3>
          <el-slider
            v-model="numberOfNodes"
            :min="10"
            :max="300"
            @input="updateClustersOfFirstNNodes"
          ></el-slider>
        </div>

        <!-- Overall Statistic Module -->
        <div
          id="statistics-panel"
          style="
            background-color: #f7f7f7;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            flex: 1 1 auto;
            max-width: 100%;
            overflow-x: scroll;
            overflow-y: hidden;
            position: relative;
          "
        >
          <h3>Overall Statistic</h3>
          <div
            id="bar-chart"
            style="
              width: fit-content;
              height: 100%;
              overflow-x: auto;
              overflow-y: hidden;
            "
          ></div>
        </div>
      </div>
    </div>
    <!-- Lower Section: Attribute Statistic Module and Bar Chart -->
    <div
      style="
        flex: 2;
        display: flex;
        flex-direction: column; /* Changed from row to column */
        height: 150vh;
        background-color: #f7f7f7;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
        overflow: hidden;
      "
    >
      <!-- Upper part: Attribute Statistic Module and Bar Chart -->
      <div
        style="
          display: flex;
          flex-direction: row;
          width: 100%;
          height: 50%;
          margin-bottom: 20px;
        "
      >
        <!-- Left Side: Attribute Statistic Module and Bar Chart -->
        <div
          style="
            width: 100%;
            display: flex;
            flex-direction: column;
            margin-right: 20px;
          "
        >
          <!-- Attribute Statistic Module -->
          <div>
            <h2 style="text-align: center; margin-bottom: 10px">
              Attribute Statistic
            </h2>
            <!-- Cluster and Attribute Selection -->
            <div
              style="
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
              "
            >
              <!-- Cluster Selection -->
              <div style="margin-bottom: 20px">
                <label>Select Cluster:</label>
                <el-select
                  v-model="selectedClusterForAttribute"
                  placeholder="Select Cluster"
                  style="width: 100%"
                >
                  <el-option
                    v-for="cluster in clusterNames"
                    :key="cluster"
                    :label="cluster"
                    :value="cluster"
                  ></el-option>
                </el-select>
              </div>
              <!-- Attribute Selection -->
              <div style="margin-bottom: 20px">
                <label>Select Attribute:</label>
                <el-select
                  v-model="selectedAttributeForStatistic"
                  placeholder="Select Attribute"
                  style="width: 100%"
                >
                  <el-option
                    v-for="attr in attributesForStatistic"
                    :key="attr"
                    :label="attr"
                    :value="attr"
                  ></el-option>
                </el-select>
              </div>
              <!-- Generate Button -->
              <div style="margin-top: 20px">
                <el-button
                  type="primary"
                  style="width: 100%; height: 50px"
                  @click="generateAttributeStatistic"
                >
                  Generate Statistic
                </el-button>
              </div>
            </div>
          </div>
          <!-- Attribute Statistic Bar Chart Module -->
          <div
            id="attribute-bar-chart-container"
            style="
              flex: 1;
              background-color: #f7f7f7;
              padding: 20px;
              border-radius: 8px;
              box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
              overflow-x: scroll;
              overflow-y: auto;
              margin-top: 20px;
              height: 100vh;
              position: relative;
            "
          >
            <!-- Title with Download Button -->
            <div
              style="
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 10px;
              "
            >
              <h3 style="margin: 0; margin-right: 20px">
                Attribute Statistic Bar Chart
              </h3>
              <el-button
                type="primary"
                icon="el-icon-download"
                size="mini"
                @click="downloadBarChart"
                :disabled="!isBarChartGenerated"
                style="
                  display: flex;
                  align-items: center;
                  justify-content: center;
                "
              >
                Download
              </el-button>
            </div>

            <!-- Add legend for colors -->
            <div style="position: absolute; top: 10px; right: 10px">
              <div style="display: flex; align-items: center">
                <div
                  style="
                    width: 20px;
                    height: 10px;
                    background-color: #69b3a2;
                    margin-right: 5px;
                  "
                ></div>
                <span>Total count (general data + highlighted data)</span>
              </div>
              <div style="display: flex; align-items: center; margin-top: 5px">
                <div
                  style="
                    width: 20px;
                    height: 10px;
                    background-color: red;
                    margin-right: 5px;
                  "
                ></div>
                <span>Highlighted data</span>
              </div>
            </div>

            <div
              id="attribute-bar-chart"
              style="
                width: fit-content;
                height: 100%;
                overflow-x: auto;
                overflow-y: hidden;
              "
            ></div>
          </div>
        </div>
      </div>

      <!-- Lower part: Attribute Statistic Table Module -->
      <div style="width: 100%; height: 47%">
        <!-- Attribute Statistic Table Module -->
        <div
          style="
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            height: 100%;
            overflow-x: auto;
            overflow-y: auto;
          "
        >
          <!-- Title with Download Button -->
          <div
            style="
              display: flex;
              align-items: center;
              justify-content: center;
              margin-bottom: 10px;
            "
          >
            <h3 style="margin: 0; margin-right: 20px">
              Attribute Statistic Table
            </h3>
            <el-button
              type="primary"
              icon="el-icon-download"
              size="mini"
              @click="downloadTableData"
              :disabled="!dataForClusterTable.length"
            >
              Download
            </el-button>
          </div>
          <!-- Filter -->
          <div style="margin-bottom: 20px">
            <label>Filter:</label>
            <div style="display: flex; align-items: center">
              <!-- Select Attribute -->
              <el-select
                v-model="selectedTableFilterAttribute"
                placeholder="Select Attribute"
                style="flex: 1; margin-right: 10px"
                @change="onTableFilterAttributeChange"
              >
                <el-option
                  v-for="attr in attributesForTableFilter"
                  :key="attr"
                  :label="attr"
                  :value="attr"
                ></el-option>
              </el-select>
              <!-- Select Value -->
              <el-select
                v-model="selectedTableFilterValue"
                placeholder="Select Value"
                style="flex: 1; margin-right: 10px"
              >
                <el-option
                  v-for="val in tableFilterValues"
                  :key="val"
                  :label="val"
                  :value="val"
                ></el-option>
              </el-select>
            </div>
          </div>
          <!-- Table Content -->
          <table style="width: 100%; border-collapse: collapse">
            <thead>
              <!-- Grouped headers -->
              <tr>
                <th
                  v-for="(group, groupIndex) in tableColumns"
                  :key="'group-' + groupIndex"
                  :colspan="group.columns.length"
                  style="
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                  "
                >
                  {{ group.category }}
                </th>
              </tr>
              <tr>
                <th
                  v-for="(column, columnIndex) in tableHeaders"
                  :key="'column-' + columnIndex"
                  style="border: 1px solid #ddd; padding: 8px"
                >
                  {{ column }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, index) in filteredDataForClusterTable"
                :key="index"
              >
                <td
                  v-for="(column, columnIndex) in tableHeaders"
                  :key="'cell-' + index + '-' + columnIndex"
                  style="border: 1px solid #ddd; padding: 8px"
                  :style="
                    column === 'ID'
                      ? {
                          color: isHighlighted(item.ID)
                            ? 'red'
                            : isGeneralData(item.ID)
                              ? 'green'
                              : 'black',
                        }
                      : {}
                  "
                >
                  {{ item[column] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import * as d3 from "d3";
import { ref, onMounted, computed, watch, getCurrentInstance } from "vue";
import { ElMessage } from "element-plus";
import * as XLSX from "xlsx";

import { agnes, Cluster } from "ml-hclust";
import Clustering from "hdbscanjs";
import hcluster from "../hcluster.js"

import { euclidean } from "ml-distance-euclidean";
import axios from "axios";

import { assay_types, sub_types, index_names } from "../index_names";

const allIndexNames = ref(["local"]);
for (let assay_type of assay_types) {
  allIndexNames.value.push(index_names[assay_type]["assay"]);
}
const indexNamesString = allIndexNames.value.join(",");

// Data and cluster counts
const clusterData = ref(null);
const clusterCount = ref(100); // Default number of clusters
const maxClusterCount = ref(1500); // Assume max 1500 clusters

// Add the new reactive variable for selected attributes
const selectedAttributesForClustering = ref([]);

// Variables for the upper tree
const selectedNodeUpper = ref(""); // Selected node name
const selectedLayerUpper = ref(""); // Selected layer
const selectedLayerStatsUpper = ref(""); // Statistics for selected layer
const selectedLayerClustersUpper = ref([]); // Clusters in selected layer
const allNodesUpper = ref([]); // All nodes in the upper tree

// Variables for the clusters of first n nodes
const numberOfNodes = ref(20); // Default n
const clustersOfFirstNNodes = ref([]);
const clustersData = ref([]); // Data for the bar chart

// Data loading and filters for salmonella data
const selectedDateRange = ref(null); // Date range filter
const selectedDatastore = ref(null); // Datastore selection

const loading = ref(false);

const attributeFilters = ref([
  {
    attribute: "",
    value: "",
    values: [],
  },
]);
const attributes = ["Source", "Country", "Brand", "Serotype", "MLST"];

const salmonellaData = ref([]);
const filteredSalmonellaData = ref([]); // Filtered data for general data filter

// Add salmonellaHeaders to store the headers
const salmonellaHeaders = ref([]);

// 获取当前实例以获取 apiUrl
const instance = getCurrentInstance();
if (!instance) {
  throw new Error("Failed to get current instance");
}

const apiUrl = instance.proxy.$apiHost;
if (!apiUrl) {
  throw new Error("API URL not found");
}

// 定义 value2，如果尚未定义
const value2 = ref<[Date, Date] | undefined>([new Date(), new Date()]);

// 定义 AST 列
const astColumns = [
  "Amikacin Interpretation",
  "Tobramycin Interpretation",
  "Gentamicin Interpretation",
  "Amox/K Clav Interpretation",
  "Amp/Sulbactam Interpretation",
  "Pip/Tazo Interpretation",
  "Ampicillin Interpretation",
  "Piperacillin Interpretation",
  "Aztreonam Interpretation",
  "Cefepime Interpretation",
  "Cefotaxime Interpretation",
  "Cefoxitin Interpretation",
  "Ceftazidime Interpretation",
  "Cefuroxime Interpretation",
  "Chloramphenicol Interpretation",
  "Ciprofloxacin Interpretation",
  "Levofloxacin Interpretation",
  "Norfloxacin Interpretation",
  "Colistin Interpretation",
  "Doripenem Interpretation",
  "Ertapenem Interpretation",
  "Imipenem Interpretation",
  "Meropenem Interpretation",
  "Fosfomycin Interpretation",
  "Minocycline Interpretation",
  "Tetracycline Interpretation",
  "Nitrofurantoin Interpretation",
  "Trimeth/Sulfa Interpretation",
];

// 定义 SPI 列
const spiColumns = [
  "C63PI",
  "CS54_island",
  "HPI",
  "SESS-LEE",
  "SGI1",
  "SGI2",
  "SPI-1",
  "SPI-2",
  "SPI-3",
  "SPI-4",
  "SPI-5",
  "SPI-6",
  "SPI-7",
  "SPI-8",
  "SPI-9",
  "SPI-10",
  "SPI-11",
  "SPI-12",
  "SPI-13",
  "SPI-14",
];

// 定义 AMR 列
const amrColumns = [
  "Aac2-Ia_AGly",
  "Aac3-IIa_AGly",
  "Aac3-Iva_AGly",
  "Aac3-VIa_AGly",
  "Aac6-Aph2_AGly",
  "Aac6-Iaa_AGly",
  "Aac6-If_AGly",
  "AacAad_AGly",
  "AadA_AGly",
  "AadB_AGly",
  "Ant6-Ia_AGly",
  "Aph3--Ia_AGly",
  "Aph3-IIb_AGly",
  "Aph3-III_AGly",
  "Aph4-Ia_AGly",
  "Aph7_AGly",
  "AphA2_AGly",
  "Sat4A_AGly",
  "Sat-2A_AGly",
  "StrA_AGly",
  "StrB_AGly",
  "VanC1_Gly",
  "VanR-C_Gly",
  "VanS-C_Gly",
  "VanT_Gly",
  "VanX-Yc_Gly",
  "ACI-1_Bla",
  "ACT-MIR_Bla",
  "AmpC1_Ecoli_Bla",
  "AmpC2_Ecoli_Bla",
  "AmpH_Bla",
  "AMPH_Ecoli_Bla",
  "CARB_Bla",
  "CEPA-85_Bla",
  "CfiA_Bla",
  "CMY_Bla",
  "CTX-M-1_Bla",
  "CTX-M-2_Bla",
  "CTX-M-8_Bla",
  "CTX-M-9_Bla",
  "DHA_Bla",
  "LAP_Bla",
  "MrdA_Bla",
  "OXA-1_Bla",
  "OXA-2_Bla",
  "OXA-50_Bla",
  "OXA-61_Bla",
  "SHV-OKP-LEN_Bla",
  "TEM-1D_Bla",
  "Arr_Rif",
  "Cat-86_Phe",
  "CatA1_Phe",
  "CatA2_Phe",
  "CatA3_Phe",
  "CatB7_Phe",
  "CatBx_Phe",
  "CmlA_Phe",
  "FexA_Phe",
  "FloR_Phe",
  "DfrA1_Tmt",
  "DfrA5_Tmt",
  "DfrA7_Tmt",
  "DfrA8_Tmt",
  "DfrA23_Tmt",
  "DfrA27_Tmt",
  "DfrA_Tmt",
  "SulI_Sul",
  "SulII_Sul",
  "SulIII_Sul",
  "Erm42_MLS",
  "ErmB_MLS",
  "ErmF_MLS",
  "LinB_MLS",
  "LnuA_MLS",
  "LnuC_MLS",
  "LnuF_MLS",
  "MphA_MLS",
  "FosA2_Fcyn",
  "FosA_Fcyn",
  "Mcr1_Colistin",
  "Mcr3_Colistin",
  "OqxA_Flq",
  "OqxB_Flq",
  "QepA_Flq",
  "Qnr-A_Flq",
  "Qnr-S_Flq",
  "QnrB_Flq",
  "TetA_Tet",
  "TetB_Tet",
  "TetC_Tet",
  "TetD_Tet",
  "TetG_Tet",
  "TetL_Tet",
  "TetM_Tet",
  "TetO_Tet",
  "TetQ_Tet",
  "TetS_Tet",
  "TetW_Tet",
  "TetX_Tet",
];

// 定义 plasmid 列
const plasmidColumns = [
  "IncFIA(HI1)",
  "IncHI1A",
  "IncHI2A",
  "IncI1-I(Alpha)",
  "IncHI1B(R27)",
  "IncB/O/K/Z",
  "IncHI2",
  "IncR",
  "IncN",
  "IncQ1",
  "IncX1",
  "IncX4",
  "IncFIB(S)",
  "IncFII",
  "IncFII(S)",
  "IncI(Gamma)",
  "pKPC-CAV1321",
  "ColpVC",
  "Col156",
  "Col(pHAD28)",
  "Col440II",
];

const loadSalmonellaData = async () => {
  const [startDate, endDate] = value2.value || [];
  try {
    const startDateParam = startDate
      ? startDate.toISOString().split("T")[0]
      : null;
    const endDateParam = endDate ? endDate.toISOString().split("T")[0] : null;

    // 指定需要的字段

    const response = await axios.get(`${apiUrl}/api/search_clustering/`, {
      params: {
        index_names: indexNamesString,
      },
    });

    const jsonData = response.data;
    console.log("cluster data:", jsonData);

    if (!jsonData.results || jsonData.results.length === 0) {
      ElMessage.warning("No data received");
      return;
    }

    let data = [];

    // 定义所有的 AST 列，SPI 列，AMR 列和 plasmid 列
    const astColumns = [
      "Amikacin Interpretation",
      "Tobramycin Interpretation",
      "Gentamicin Interpretation",
      "Amox/K Clav Interpretation",
      "Amp/Sulbactam Interpretation",
      "Pip/Tazo Interpretation",
      "Ampicillin Interpretation",
      "Piperacillin Interpretation",
      "Aztreonam Interpretation",
      "Cefepime Interpretation",
      "Cefotaxime Interpretation",
      "Cefoxitin Interpretation",
      "Ceftazidime Interpretation",
      "Cefuroxime Interpretation",
      "Chloramphenicol Interpretation",
      "Ciprofloxacin Interpretation",
      "Levofloxacin Interpretation",
      "Norfloxacin Interpretation",
      "Colistin Interpretation",
      "Doripenem Interpretation",
      "Ertapenem Interpretation",
      "Imipenem Interpretation",
      "Meropenem Interpretation",
      "Fosfomycin Interpretation",
      "Minocycline Interpretation",
      "Tetracycline Interpretation",
      "Nitrofurantoin Interpretation",
      "Trimeth/Sulfa Interpretation",
    ];

    const spiColumns = [
      "C63PI",
      "CS54_island",
      "HPI",
      "SESS-LEE",
      "SGI1",
      "SGI2",
      "SPI-1",
      "SPI-2",
      "SPI-3",
      "SPI-4",
      "SPI-5",
      "SPI-6",
      "SPI-7",
      "SPI-8",
      "SPI-9",
      "SPI-10",
      "SPI-11",
      "SPI-12",
      "SPI-13",
      "SPI-14",
    ];

    const amrColumns = [
      "Aac2-Ia_AGly",
      "Aac3-IIa_AGly",
      "Aac3-Iva_AGly",
      "Aac3-VIa_AGly",
      "Aac6-Aph2_AGly",
      "Aac6-Iaa_AGly",
      "Aac6-If_AGly",
      "AacAad_AGly",
      "AadA_AGly",
      "AadB_AGly",
      "Ant6-Ia_AGly",
      "Aph3--Ia_AGly",
      "Aph3-IIb_AGly",
      "Aph3-III_AGly",
      "Aph4-Ia_AGly",
      "Aph7_AGly",
      "AphA2_AGly",
      "Sat4A_AGly",
      "Sat-2A_AGly",
      "StrA_AGly",
      "StrB_AGly",
      "VanC1_Gly",
      "VanR-C_Gly",
      "VanS-C_Gly",
      "VanT_Gly",
      "VanX-Yc_Gly",
      "ACI-1_Bla",
      "ACT-MIR_Bla",
      "AmpC1_Ecoli_Bla",
      "AmpC2_Ecoli_Bla",
      "AmpH_Bla",
      "AMPH_Ecoli_Bla",
      "CARB_Bla",
      "CEPA-85_Bla",
      "CfiA_Bla",
      "CMY_Bla",
      "CTX-M-1_Bla",
      "CTX-M-2_Bla",
      "CTX-M-8_Bla",
      "CTX-M-9_Bla",
      "DHA_Bla",
      "LAP_Bla",
      "MrdA_Bla",
      "OXA-1_Bla",
      "OXA-2_Bla",
      "OXA-50_Bla",
      "OXA-61_Bla",
      "SHV-OKP-LEN_Bla",
      "TEM-1D_Bla",
      "Arr_Rif",
      "Cat-86_Phe",
      "CatA1_Phe",
      "CatA2_Phe",
      "CatA3_Phe",
      "CatB7_Phe",
      "CatBx_Phe",
      "CmlA_Phe",
      "FexA_Phe",
      "FloR_Phe",
      "DfrA1_Tmt",
      "DfrA5_Tmt",
      "DfrA7_Tmt",
      "DfrA8_Tmt",
      "DfrA23_Tmt",
      "DfrA27_Tmt",
      "DfrA_Tmt",
      "SulI_Sul",
      "SulII_Sul",
      "SulIII_Sul",
      "Erm42_MLS",
      "ErmB_MLS",
      "ErmF_MLS",
      "LinB_MLS",
      "LnuA_MLS",
      "LnuC_MLS",
      "LnuF_MLS",
      "MphA_MLS",
      "FosA2_Fcyn",
      "FosA_Fcyn",
      "Mcr1_Colistin",
      "Mcr3_Colistin",
      "OqxA_Flq",
      "OqxB_Flq",
      "QepA_Flq",
      "Qnr-A_Flq",
      "Qnr-S_Flq",
      "QnrB_Flq",
      "TetA_Tet",
      "TetB_Tet",
      "TetC_Tet",
      "TetD_Tet",
      "TetG_Tet",
      "TetL_Tet",
      "TetM_Tet",
      "TetO_Tet",
      "TetQ_Tet",
      "TetS_Tet",
      "TetW_Tet",
      "TetX_Tet",
    ];

    const plasmidColumns = [
      "IncFIA(HI1)",
      "IncHI1A",
      "IncHI2A",
      "IncI1-I(Alpha)",
      "IncHI1B(R27)",
      "IncB/O/K/Z",
      "IncHI2",
      "IncR",
      "IncN",
      "IncQ1",
      "IncX1",
      "IncX4",
      "IncFIB(S)",
      "IncFII",
      "IncFII(S)",
      "IncI(Gamma)",
      "pKPC-CAV1321",
      "ColpVC",
      "Col156",
      "Col(pHAD28)",
      "Col440II",
    ];

    jsonData.results.forEach((item) => {
      // 处理 AST 数据
      const astData = {};
      // 初始化 AST 列
      astColumns.forEach((col) => {
        astData[col] = null; // 初始化为 null，稍后再处理
      });

      if (Array.isArray(item.AST)) {
        item.AST.forEach((astEntry) => {
          Object.entries(astEntry).forEach(([key, value]) => {
            if (astColumns.includes(key)) {
              // 由于 value 是数组，取第一个元素
              astData[key] = value[0];
            }
          });
        });
      }

      // 将 'S'、'I'、'R' 映射为数值 0、1、2
      const mapping = { S: 0, I: 1, R: 2 };
      astColumns.forEach((col) => {
        if (astData[col] !== undefined && mapping[astData[col]] !== undefined) {
          astData[col] = mapping[astData[col]];
        } else if (astData[col] === undefined || astData[col] === null) {
          astData[col] = 0; // 缺失值设为 0
        }
      });

      // 处理 SPI 数据
      const spiData = {};
      // 初始化 SPI 列
      spiColumns.forEach((col) => {
        spiData[col] = 0; // 初始化为 0
      });
      if (Array.isArray(item.SPI)) {
        item.SPI.forEach((spiName) => {
          if (spiColumns.includes(spiName)) {
            spiData[spiName] = 1; // 存在则设为 1
          }
        });
      }

      // 处理 AMR 数据
      const amrData = {};
      // 初始化 AMR 列
      amrColumns.forEach((col) => {
        amrData[col] = 0; // 初始化为 0
      });
      if (Array.isArray(item.AMR)) {
        item.AMR.forEach((amrName) => {
          if (amrColumns.includes(amrName)) {
            amrData[amrName] = 1; // 存在则设为 1
          }
        });
      }

      // 处理 plasmid 数据
      const plasmidData = {};
      // 初始化 plasmid 列
      plasmidColumns.forEach((col) => {
        plasmidData[col] = 0; // 初始化为 0
      });
      if (Array.isArray(item.plasmid)) {
        item.plasmid.forEach((plasmidName) => {
          if (plasmidColumns.includes(plasmidName)) {
            plasmidData[plasmidName] = 1; // 存在则设为 1
          }
        });
      }

      // 添加到数据列表
      data.push({
        ID: String(item.ID[0]),
        Source: item.Source[0],
        Date: item.Date[0],
        Country: item.Country[0],
        Brand: item.Brand[0],
        Serotype: item.Serotype[0],
        MLST: item.MLST[0],
        index_name: item.index_name,
        ...astData,
        ...spiData,
        ...amrData,
        ...plasmidData,
      });
    });

    // 存储数据
    salmonellaData.value = data;
    console.log("salmonellaData:", salmonellaData.value);

    // 设置标题
    try {
      salmonellaHeaders.value = Object.keys(data[0]);
      ElMessage.success("Data loaded successfully");
    } catch (error) {
      ElMessage.error("Failed to load data");
      console.error("Error loading data:", error);
    }
  } catch (error) {
    ElMessage.error("Failed to load data from API");
    console.error("Error loading data from API:", error);
  }
};

// 监听日期范围的变化，如果适用
watch(value2, async (newVal, oldVal) => {
  if (newVal && newVal.length === 2) {
    await loadSalmonellaData();
  }
});

// 在组件挂载时加载数据
onMounted(async () => {
  try {
    loading.value = true;
    const startYear = 1900;
    const endYear = new Date().getFullYear();
    value2.value = [
      new Date(`${startYear}-01-01`),
      new Date(`${endYear}-12-31`),
    ];
    await loadSalmonellaData();
    loading.value = false;
  } catch (error) {
    console.error("Error loading data on mount:", error);
    loading.value = false;
  } finally {
    loading.value = false;
  }
});

// Function to process attribute values
function processAttributeValue(val) {
  if (val === undefined || val === null || val === "") {
    return null;
  }

  if (typeof val === "string") {
    val = val.trim();

    if (val.startsWith("[") && val.endsWith("]")) {
      // Try to parse as JSON
      try {
        const parsed = JSON.parse(val);
        if (Array.isArray(parsed)) {
          return parsed.length > 0 ? parsed[0] : null;
        } else {
          return parsed;
        }
      } catch (e) {
        // Parsing failed, return val as is
        return val;
      }
    } else {
      return val;
    }
  } else if (Array.isArray(val)) {
    return val.length > 0 ? val[0] : null;
  } else {
    return val;
  }
}

function parseDateYMD(dateInput) {
  if (!dateInput) return null;

  let dateString = dateInput;
  if (Array.isArray(dateInput)) {
    dateString = dateInput[0];
  }

  const parts = dateString.split("-");
  if (parts.length !== 3) return null;
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1; // Months are zero-based
  const day = parseInt(parts[2], 10);
  return new Date(year, month, day);
}

// Function to get distinct values for an attribute
const getAttributeValues = (attribute) => {
  if (!attribute || !salmonellaData.value.length) return [];

  const values = salmonellaData.value
    .map((item) => processAttributeValue(item[attribute]))
    .filter((val) => val !== null);

  return Array.from(new Set(values));
};

// Function to handle attribute change
const onAttributeChange = (index) => {
  const filter = attributeFilters.value[index];
  filter.value = ""; // Reset selected value
  filter.values = getAttributeValues(filter.attribute);
};

// Functions to add and remove filters
const addFilter = () => {
  attributeFilters.value.push({
    attribute: "",
    value: "",
    values: [],
  });
};

const removeFilter = (index) => {
  attributeFilters.value.splice(index, 1);
};

/* Multiple clustering filter code */

// Multiple clusterings
const clusterings = ref([
  {
    attributeFilters: [
      {
        attribute: "",
        value: "",
        values: [],
      },
    ],
    idFilters: [
      {
        id: "",
      },
    ],
  },
]);

const selectedDateRangeMultiple = ref(null);
const attributesMultiple = ["Source", "Country", "Brand", "Serotype", "MLST"];
const idValuesMultiple = ref([]);

const selectedDatastoreMultiple = ref([]);
const highlightedDatastoreMultiple = ref([]);

// Functions to add and remove clusterings
const addClustering = () => {
  clusterings.value.push({
    attributeFilters: [
      {
        attribute: "",
        value: "",
        values: [],
      },
    ],
    idFilters: [
      {
        id: "",
      },
    ],
  });
};

const removeClustering = (clusteringIndex) => {
  clusterings.value.splice(clusteringIndex, 1);
};

// Functions to add and remove attribute filters in multiple clustering
const addFilterMultiple = (clusteringIndex) => {
  clusterings.value[clusteringIndex].attributeFilters.push({
    attribute: "",
    value: "",
    values: [],
  });
};

const removeFilterMultiple = (clusteringIndex, index) => {
  clusterings.value[clusteringIndex].attributeFilters.splice(index, 1);
};

// Function to handle attribute change in multiple clustering
const onAttributeChangeMultiple = (clusteringIndex, index) => {
  const filter = clusterings.value[clusteringIndex].attributeFilters[index];
  filter.value = "";
  filter.values = getAttributeValuesMultiple(filter.attribute);
};

// Function to get attribute values for multiple clustering
const getAttributeValuesMultiple = (attribute) => {
  if (!attribute || !salmonellaData.value.length) return [];

  const values = salmonellaData.value
    .map((item) => processAttributeValue(item[attribute]))
    .filter((val) => val !== null);

  return Array.from(new Set(values));
};

// Functions to add and remove ID filters in multiple clustering
const addIdFilterMultiple = (clusteringIndex) => {
  clusterings.value[clusteringIndex].idFilters.push({
    id: "",
  });
};

const removeIdFilterMultiple = (clusteringIndex, index) => {
  clusterings.value[clusteringIndex].idFilters.splice(index, 1);
};

// Function to populate ID values for multiple clustering
const populateIdValuesMultiple = () => {
  idValuesMultiple.value = salmonellaData.value
    .map((item) => processAttributeValue(item["ID"]))
    .filter((id) => id !== null);

  idValuesMultiple.value = Array.from(new Set(idValuesMultiple.value));
};

/* End of multiple clustering filter code */

function parseDateDMY(dateString) {
  const parts = dateString.split("/");
  if (parts.length !== 3) return null;
  const day = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1; // Months are 0-based
  const year = parseInt(parts[2], 10);
  return new Date(year, month, day);
}

// Function to filter salmonellaData based on selected filters
function filterSalmonellaData() {
  let data = salmonellaData.value;

  //apply selected Datastore filter
  if (selectedDatastoreMultiple.value.length > 0) {
    data = data.filter((item) => {
      const index_name = String(processAttributeValue(item["index_name"]));
      return selectedDatastoreMultiple.value.includes(index_name);
    });
  }

  // Apply selectedDateRange filter
  if (selectedDateRange.value && selectedDateRange.value.length === 2) {
    const [startDate, endDate] = selectedDateRange.value;
    data = data.filter((item) => {
      const itemDateValue = processAttributeValue(item["Date"]);
      const itemDate = parseDateYMD(itemDateValue);
      return itemDate >= startDate && itemDate <= endDate;
    });
  }

  // Group filters by attribute
  const filtersByAttribute = {};
  attributeFilters.value.forEach((filter) => {
    if (filter.attribute && filter.value) {
      if (!filtersByAttribute[filter.attribute]) {
        filtersByAttribute[filter.attribute] = [];
      }
      filtersByAttribute[filter.attribute].push(filter.value);
    }
  });

  // Apply attributeFilters with logical AND between attributes and OR within the same attribute
  for (const attribute in filtersByAttribute) {
    const values = filtersByAttribute[attribute];
    data = data.filter((item) => {
      const itemAttributeValue = processAttributeValue(item[attribute]);
      return values.includes(itemAttributeValue);
    });
  }

  // Store the filtered data
  filteredSalmonellaData.value = data;
}

function filterClusteringData(clustering) {
  let dataFromAttributeFilters: any[] = [];
  let dataFromIdFilters: any[] = [];

  let dataInSelectedDatastore = salmonellaData.value;
  console.log("Before:", dataInSelectedDatastore.length);
  // Apply highlighted datastore filter
  if (highlightedDatastoreMultiple.value.length > 0) {
    dataInSelectedDatastore = dataInSelectedDatastore.filter((item) => {
      const index_name = String(processAttributeValue(item["index_name"]));
      return highlightedDatastoreMultiple.value.includes(index_name);
    });
  }
  console.log("After:", dataInSelectedDatastore.length);

  let filterHappened = false;

  console.log("filter clustering: ", clustering);
  // Apply attributeFilters and highlighted datastore filter
  if (clustering.attributeFilters.some((f) => f.attribute && f.value)) {
    filterHappened = true;
    dataFromAttributeFilters = [];
    let data = dataInSelectedDatastore;
    // Apply date range filter
    if (
      selectedDateRangeMultiple.value &&
      selectedDateRangeMultiple.value.length === 2
    ) {
      const [startDate, endDate] = selectedDateRangeMultiple.value;
      data = data.filter((item) => {
        const itemDateValue = processAttributeValue(item["Date"]);
        const itemDate = parseDateYMD(itemDateValue);
        return itemDate >= startDate && itemDate <= endDate;
      });
    }

    // Group filters by attribute
    const filtersByAttribute = {};
    clustering.attributeFilters.forEach((filter) => {
      if (filter.attribute && filter.value) {
        if (!filtersByAttribute[filter.attribute]) {
          filtersByAttribute[filter.attribute] = [];
        }
        filtersByAttribute[filter.attribute].push(filter.value);
      }
    });

    // Apply attributeFilters
    for (const attribute in filtersByAttribute) {
      const values = filtersByAttribute[attribute];
      data = data.filter((item) => {
        const itemAttributeValue = processAttributeValue(item[attribute]);
        return values.includes(itemAttributeValue);
      });
    }

    dataFromAttributeFilters = data;
  }

  // Apply idFilters
  const selectedIds = clustering.idFilters
    .map((filter) => String(filter.id))
    .filter((id) => id);

  if (selectedIds.length > 0) {
    filterHappened = true;
    dataFromIdFilters = [];
    let data = dataInSelectedDatastore.filter((item) => {
      const itemID = String(processAttributeValue(item["ID"]));
      return selectedIds.includes(itemID);
    });

    // Apply date range filter
    if (
      selectedDateRangeMultiple.value &&
      selectedDateRangeMultiple.value.length === 2
    ) {
      const [startDate, endDate] = selectedDateRangeMultiple.value;
      data = data.filter((item) => {
        const itemDateValue = processAttributeValue(item["Date"]);
        const itemDate = parseDateYMD(itemDateValue);
        return itemDate >= startDate && itemDate <= endDate;
      });
    }

    dataFromIdFilters = data;
  }

  // Combine data
  let unionData = [];
  if (filterHappened === true) {
    unionData = [...dataFromAttributeFilters, ...dataFromIdFilters];
  } else {
    unionData = dataInSelectedDatastore;
  }
  // Remove duplicates
  const idSet = new Set();
  const uniqueData = [];

  unionData.forEach((item) => {
    if (!idSet.has(item.ID)) {
      idSet.add(item.ID);
      uniqueData.push(item);
    }
  });
  console.log("uniqueData: ", uniqueData);
  return uniqueData;
}


async function testClusterAlgos(dataset) {
  // const module = await import('../hcluster/hcluster.js/hcluster.js');
  // const hcluster = module.default;
  const data=dataset.map((item,index)=>({
    name: index,
    position: item
  }))
  const cluster=hcluster()
    .distance('euclidean')
    .linkage('avg')
    .verbose(false)
    .data(data)
  const tree=cluster.tree()
  console.log("hcluster: ",tree)
}

/////////////////////////////////////
// Custering Algorithms

const clusteringAlgorithms = ["Agnes", "Hdbscanjs", "Hcluster"];
const selectedAlgorithm = ref(clusteringAlgorithms[0]);

const agnesMethods = ['ward','ward2','single','complete','average','upgma','wpgma','median','wpgmc','centroid','upgmc']
const selectedAgnesMethod = ref(agnesMethods[0])

const distFuncHdbs = ["euclidean","geoDist"]
const selectedDistFuncHdbs=ref(distFuncHdbs[0])

const distFuncHcluster = ["euclidean","angular"]
const selectedDistFuncHcluster=ref(distFuncHcluster[0])

const linkageHcluster=["avg","max","min"]
const selectedLinkageHcluster=ref(linkageHcluster[0])

// 1. Agnes
function createAgnesCluster(
  truncated_data,
  truncated_data_ids,
  truncated_source
) {
  const clusters: Cluster = agnes(truncated_data, {
    method: selectedAgnesMethod.value,
    distanceFunction: euclidean,
  });
  console.log("agnes clusters:", clusters);
  const rootNode = buildTreeFromAgnes(
    clusters,
    truncated_data_ids,
    truncated_source
  );
  bfsRenameTree(rootNode);
  return rootNode;
}

function buildTreeFromAgnes(
  node: any,
  truncated_data_ids: any,
  truncated_source: any
) {
  if (node.children && node.children.length > 0) {
    const leftChild: any = buildTreeFromAgnes(
      node.children[0],
      truncated_data_ids,
      truncated_source
    );
    const rightChild: any = buildTreeFromAgnes(
      node.children[1],
      truncated_data_ids,
      truncated_source
    );

    const nodeObj: any = {
      children: [leftChild, rightChild],
    };
    return nodeObj;
  } else {
    const leafNode = {
      name: truncated_data_ids[node.index],
      source_list: truncated_source[node.index],
    };
    return leafNode;
  }
}
// 2. Hdbscanjs
function createHdbscanCluster(
  truncated_data,
  truncated_data_ids,
  truncated_source
) {
  const data = truncated_data.map((item, index) => ({
    data: item,
    opt: index,
  }));
  let distFunc
  if (selectedDistFuncHdbs.value==="euclidean") {
    distFunc=Clustering.distFunc.euclidean;
  } else if (selectedDistFuncHdbs.value==="geoDist") {
    distFunc=Clustering.distFunc.geoDist;
  }
  const cluster = new Clustering(data, distFunc);
  const hdbscanResult = cluster.getTree();
  console.log("hdbscanjs clusters:", hdbscanResult);
  const rootNode = buildTreeFromHdbscan(
    hdbscanResult,
    truncated_data_ids,
    truncated_source
  );
  bfsRenameTree(rootNode);
  return rootNode;
}

function buildTreeFromHdbscan(
  node: any,
  truncated_data_ids: any,
  truncated_source: any
) {
  if (node.left || node.right) {
    let leftChild = null,
      rightChild = null;
    if (node.left) {
      leftChild = buildTreeFromHdbscan(
        node.left,
        truncated_data_ids,
        truncated_source
      );
    }
    if (node.right) {
      rightChild = buildTreeFromHdbscan(
        node.right,
        truncated_data_ids,
        truncated_source
      );
    }
    const nodeObj: any = {
      children: [leftChild, rightChild],
    };
    return nodeObj;
  } else {
    const leafNode = {
      name: truncated_data_ids[node.opt[0]],
      source_list: truncated_source[node.opt[0]],
    };
    return leafNode;
  }
}

// 3. Hcluster.js
function createHcluster(
  truncated_data,
  truncated_data_ids,
  truncated_source) 
{
  const data=truncated_data.map((item,index)=>({
    name: index,
    position: item
  }))
  const cluster=hcluster()
    .distance(selectedDistFuncHcluster.value)
    .linkage(selectedLinkageHcluster.value)
    .verbose(false)
    .data(data)
    .tree()
  console.log("hcluster: ",cluster)
  const treeNode=buildTreeFromHcluster(cluster,truncated_data_ids,truncated_source);
  bfsRenameTree(treeNode);
  return treeNode;
}

function buildTreeFromHcluster(
  node: any,
  truncated_data_ids: any,
  truncated_source: any) 
{
  if (node.children && node.children.length > 0) {
    const leftChild: any = buildTreeFromHcluster(
      node.children[0],
      truncated_data_ids,
      truncated_source
    );
    const rightChild: any = buildTreeFromHcluster(
      node.children[1],
      truncated_data_ids,
      truncated_source
    );
    const nodeObj: any = {
      children: [leftChild, rightChild],
    };
    return nodeObj;
  } else {
    const leafNode = {
      name: truncated_data_ids[Number(node.name)],
      source_list: truncated_source[Number(node.name)],
    };
    return leafNode;
  }
}


// Finally. Rename tree cluster names after create tree
function bfsRenameTree(node: any) {
  let queue = [node];
  let cluster_count = 0;
  while (queue.length > 0) {
    const currentNode = queue.shift();
    if (currentNode.children && currentNode.children.length > 0) {
      currentNode.name = `cluster${++cluster_count}`;
      const leftChild = currentNode.children[0];
      const rightChild = currentNode.children[1];
      queue.push(leftChild);
      queue.push(rightChild);
    }
  }
}

// Main function to create dendrogram
function createDendrogram(dataset, dataset_ids, source, n) {
  // Truncate data
  const truncated_data = dataset.slice(0, n);
  const truncated_data_ids = dataset_ids.slice(0, n);
  const truncated_source = source.slice(0, n);
  // testClusterAlgos(truncated_data)
  let rootNode = null;
  if (selectedAlgorithm.value === clusteringAlgorithms[0]) {
    rootNode = createAgnesCluster(truncated_data,truncated_data_ids,truncated_source);
  } else if (selectedAlgorithm.value === clusteringAlgorithms[1]) {
    rootNode = createHdbscanCluster(truncated_data,truncated_data_ids,truncated_source);
  } else if (selectedAlgorithm.value === clusteringAlgorithms[2]) {
    rootNode = createHcluster(truncated_data,truncated_data_ids,truncated_source) 
  }
  console.log("Selected algorithm: ", selectedAlgorithm.value);
  // let rootNode=createHdbscanTree(truncated_data,truncated_data_ids,truncated_source);
  console.log("final tree:",rootNode)
  return rootNode;
}

// function createDendrogram_new1(dataset, dataset_ids, source, n) {
//   // Truncate data
//   const truncated_data = dataset.slice(0, n);
//   const truncated_data_ids = dataset_ids.slice(0, n);
//   const truncated_source = source.slice(0, n);

//   // 调整数据格式，使其符合hdbscanjs的要求
//   const hdbscanData = truncated_data.map((item, index) => ({
//     data: item,
//     opt: index // 这里假设opt可以是数据点的索引，具体根据实际需求调整
//   }));

//   // 使用hdbscanjs库
//   const distFunc = Clustering.distFunc.euclidean; // 根据需求选择距离度量函数，这里选择欧几里得距离
//   const cluster = new Clustering(hdbscanData, distFunc);
//   const treeNode = cluster.getTree();

//   console.log("treeNode: ",treeNode);
//   // 这里不需要像原来那样构建树结构，因为hdbscanjs的getTree方法已经返回了树结构
//   // 可以直接返回treeNode，或者根据需要进一步处理
//   return treeNode;
// }

// function createDendrogram(dataset, dataset_ids, source, n) {
//     // Truncate data
//     const truncated_data = dataset.slice(0, n);
//     const truncated_data_ids = dataset_ids.slice(0, n);
//     const truncated_source = source.slice(0, n);

//     // 调整数据格式，使其符合hdbscanjs的要求
//     const hdbscanData = truncated_data.map((item, index) => ({
//         data: item,
//         opt: index // 这里假设opt可以是数据点的索引，具体根据实际需求调整
//     }));

//     // 使用hdbscanjs库
//     const distFunc = Clustering.distFunc.euclidean; // 根据需求选择距离度量函数，这里选择欧几里得距离
//     const cluster = new Clustering(hdbscanData, distFunc);
//     const hdbscanTreeNode = cluster.getTree();

//     // 转换hdbscanjs树结构为旧格式树结构
//     function convertToOldFormat(node) {
//         if (!node.children || node.children.length === 0) {
//             // 叶子节点
//             const index = node.value.id; // 假设id是索引
//             return {
//                 name: truncated_data_ids[index],
//                 source_list: truncated_source[index]
//             };
//         } else {
//             // 非叶子节点
//             const leftChild = convertToOldFormat(node.children[0]);
//             const rightChild = convertToOldFormat(node.children[1]);
//             const clusterName = `cluster${Math.random().toString(36).substring(7)}`;
//             return {
//                 name: clusterName,
//                 children: [leftChild, rightChild]
//             };
//         }
//     }

//     const rootNode = convertToOldFormat(hdbscanTreeNode);
//     console.log("rootNode: ", rootNode);
//     return rootNode;
// }

// Clustering results for multiple clusterings

const clusteringResults = ref([]); // Stores dendrograms and other data for each clusteringa

// Current selected clustering index
const selectedClusteringIndex = ref(0);

// Function to handle the Run button click event
const onRunButtonClick = () => {
  // 执行数据过滤
  filterSalmonellaData();

  // 处理多个聚类
  clusteringResults.value = []; // 重置结果

  clusterings.value.forEach((clustering, index) => {
    // 为每个聚类过滤其高亮数据
    const filteredHighlightedDataForClustering =
      filterClusteringData(clustering);

    // 合并一般数据和此聚类的高亮数据
    const combinedData = [
      ...filteredSalmonellaData.value,
      ...filteredHighlightedDataForClustering,
    ];

    // 删除重复项
    const idSet = new Set();
    const uniqueCombinedData = [];
    combinedData.forEach((item) => {
      if (!idSet.has(item.ID)) {
        idSet.add(item.ID);
        uniqueCombinedData.push(item);
      }
    });

    // 如果合并的数据为空，显示警告
    if (uniqueCombinedData.length === 0) {
      console.error("过滤后的数据集为空。");
      ElMessage.warning(
        `聚类 ${index + 1}：过滤后的数据集为空，无法进行聚类。`
      );
      clusteringResults.value.push(null); // 保持索引对齐
      return;
    }

    // 创建用于聚类的列列表
    let columnsToUseForClustering = [];

    if (selectedAttributesForClustering.value.includes("AST")) {
      columnsToUseForClustering = columnsToUseForClustering.concat(astColumns);
    }
    if (selectedAttributesForClustering.value.includes("SPI")) {
      columnsToUseForClustering = columnsToUseForClustering.concat(spiColumns);
    }
    if (selectedAttributesForClustering.value.includes("AMR")) {
      columnsToUseForClustering = columnsToUseForClustering.concat(amrColumns);
    }
    if (selectedAttributesForClustering.value.includes("plasmid")) {
      columnsToUseForClustering =
        columnsToUseForClustering.concat(plasmidColumns);
    }

    // 如果未选择任何属性，提示警告并返回
    if (columnsToUseForClustering.length === 0) {
      ElMessage.warning("Please choose at least one attribute for clustering.");
      clusteringResults.value.push(null); // 保持索引对齐
      return;
    }

    // 从选定的列创建数据集
    const dataset = uniqueCombinedData.map((item) => {
      return columnsToUseForClustering.map((col) => {
        let val = item[col];
        if (val === undefined || val === null || val === "") {
          return 0;
        } else if (!isNaN(Number(val))) {
          return Number(val);
        } else {
          return 0;
        }
      });
    });

    console.log("Dataset for clustering: ", dataset);
    if (dataset.length === 0 || dataset.some((arr) => arr.length === 0)) {
      console.error("Dataset is empty or contains empty arrays.");
      ElMessage.warning(
        `Error: Cluster ${index + 1}: Dataset is empty or contains empty arrays.`
      );
      clusteringResults.value.push(null); // 保持索引对齐
      return;
    }

    const datasetIds = uniqueCombinedData.map((item) => item.ID);
    const source = uniqueCombinedData.map((item) => item.Source);

    const dendrogram = createDendrogram(
      dataset,
      datasetIds,
      source,
      dataset.length
    );

    clusteringResults.value.push({
      dendrogram,
      combinedData: uniqueCombinedData,
      datasetIds,
      source,
      allNodes: [],
      highlightedData: filteredHighlightedDataForClustering, // 存储此聚类的高亮数据
    });
  });

  // 更新树和聚类
  updateTree();
  updateClustersOfFirstNNodes();

  // 更新聚类名称供选择
  updateClusterNames();
};

// Parse JSON into tree structure
const parseClusters = (data, parentName = "root") => {
  const node = { name: parentName, children: [] };

  if (typeof data === "object" && !Array.isArray(data)) {
    for (const key in data) {
      node.children.push(parseClusters(data[key], key));
    }
  } else if (Array.isArray(data)) {
    data.forEach((item) => {
      if (typeof item === "string") {
        node.children.push({ name: item });
      } else if (typeof item === "object") {
        for (const key in item) {
          node.children.push(parseClusters(item[key], key));
        }
      }
    });
  }

  return node;
};

// Draw the tree chart
// const drawTree = (
//   data,
//   maxNodes,
//   targetSvgId,
//   options = {
//     selectedNode: ref(''),
//     selectedLayer: ref(''),
//     selectedLayerStats: ref(''),
//     selectedLayerClusters: ref([]),
//     allNodesRef: null,
//     highlightedData: [], // Added
//     generalData: [],     // Added
//   }
// ) => {
//   const {
//     selectedNode,
//     selectedLayer,
//     selectedLayerStats,
//     selectedLayerClusters,
//     allNodesRef,
//     highlightedData,
//     generalData,
//   } = options;

//   const margin = { top: 50, right: 30, bottom: 50, left: 30 };
//   const containerWidth = document.getElementById(targetSvgId).clientWidth;
//   const containerHeight = document.getElementById(targetSvgId).clientHeight;

//   const width = containerWidth - margin.left - margin.right;
//   const height = containerHeight - margin.top - margin.bottom;

//   // 创建 tooltip 容器
//   const tooltip = d3.select('body')
//     .append('div')
//     .attr('class', 'tooltip')
//     .style('position', 'absolute')
//     .style('padding', '8px')
//     .style('background', 'rgba(0, 0, 0, 0.7)')
//     .style('color', '#fff')
//     .style('border-radius', '4px')
//     .style('pointer-events', 'none')
//     .style('visibility', 'hidden')
//     .style('font-size', '12px');

//   const svg = d3
//     .select(`#${targetSvgId}`)
//     .attr('width', containerWidth)
//     .attr('height', containerHeight)
//     .style('border', '1px solid #ccc');

//   const g = svg
//     .append('g')
//     .attr('transform', `translate(${margin.left},${margin.top})`);

//   const root = d3.hierarchy(data);

//   const nodeVerticalSpacing = 65;
//   const nodeHorizontalSpacing = 60;
//   const treeHeight = nodeVerticalSpacing * (root.height + 1);

//   const treeLayout = d3.tree().size([treeHeight * 1.3, nodeHorizontalSpacing * (root.height + 1)]);
//   treeLayout(root);

//   // Get all nodes
//   const allNodes = root.descendants();

//   // Pass allNodes to the reactive variable
//   if (allNodesRef) {
//     allNodesRef.value = allNodes;
//   }

//   // Display only the first maxNodes nodes
//   const nodesToDisplay = allNodes.slice(0, maxNodes);

//   // Calculate the number of nodes per layer
//   const layerCounts = {};
//   allNodes.forEach((node) => {
//     const depth = node.depth;
//     if (!layerCounts[depth]) {
//       layerCounts[depth] = 0;
//     }
//     layerCounts[depth] += 1;
//   });

//   // Draw links
//   g.selectAll('.link')
//     .data(nodesToDisplay.slice(1))
//     .enter()
//     .append('path')
//     .attr('class', 'link')
//     .attr('d', (d) => {
//       const startX = d.parent.x;
//       const startY = d.parent.y;
//       const endX = d.x;
//       const endY = d.y;
//       return `M${startX},${startY} H${endX} V${endY}`;
//     })
//     .style('fill', 'none')
//     .style('stroke', '#555')
//     .style('stroke-width', '2px');

//   // Draw nodes
//   const nodes = g
//     .selectAll('.node')
//     .data(nodesToDisplay)
//     .enter()
//     .append('g')
//     .attr('class', 'node')
//     .attr('transform', (d) => `translate(${d.x}, ${d.y})`)
//     .on('click', function (event, d) {
//       selectedNode.value = d.data.name;
//       // 更新选中的聚类
//       selectedClusterForAttribute.value = d.data.name;
//     })
//     .on('mouseover', function (event, d) {
//       tooltip.style('visibility', 'visible')
//         .text(d.data.name);
//     })
//     .on('mousemove', function (event) {
//       tooltip.style('top', (event.pageY - 10) + 'px')
//         .style('left', (event.pageX + 10) + 'px');
//     })
//     .on('mouseout', function () {
//       tooltip.style('visibility', 'hidden');
//     });

//   // 设置节点大小和颜色
//   nodes.append('circle')
//     .attr('r', (d) => {
//       const nodeCountInLayer = layerCounts[d.depth];
//       return nodeCountInLayer > 20 ? 3 : 5;
//     })
//     .style('fill', (d) => getNodeColor(d))
//     .transition()
//     .duration(300);

//   // Function to get node color
//   function getNodeColor(d) {
//     if (clustersOfFirstNNodes.value.includes(d.data.name)) {
//       return 'orange';
//     } else if (highlightedData.some((item) => item.ID === d.data.name)) {
//       return 'red'; // Highlighted data for current clustering
//     } else if (generalData.some((item) => item.ID === d.data.name)) {
//       return 'green'; // General data
//     } else {
//       return '#999'; // Default color
//     }
//   }
// };

// const drawTree = (
//   data,
//   maxNodes,
//   targetSvgId,
//   options = {
//     selectedNode: ref(""),
//     selectedLayer: ref(""),
//     selectedLayerStats: ref(""),
//     selectedLayerClusters: ref([]),
//     allNodesRef: null,
//     highlightedData: [],
//     generalData: [],
//   }
// ) => {
//   const {
//     selectedNode,
//     selectedLayer,
//     selectedLayerStats,
//     selectedLayerClusters,
//     allNodesRef,
//     highlightedData,
//     generalData,
//   } = options;

//   const margin = { top: 50, right: 30, bottom: 50, left: 30 };
//   const containerWidth = document.getElementById(targetSvgId).clientWidth;
//   const containerHeight = document.getElementById(targetSvgId).clientHeight;

//   const width = containerWidth - margin.left - margin.right;
//   const height = containerHeight - margin.top - margin.bottom;

//   // 创建 tooltip 容器
//   const tooltip = d3
//     .select("body")
//     .append("div")
//     .attr("class", "tooltip")
//     .style("position", "absolute")
//     .style("padding", "8px")
//     .style("background", "rgba(0, 0, 0, 0.7)")
//     .style("color", "#fff")
//     .style("border-radius", "4px")
//     .style("pointer-events", "none")
//     .style("visibility", "hidden")
//     .style("font-size", "12px");

//   const svg = d3
//     .select(`#${targetSvgId}`)
//     .attr("width", containerWidth)
//     .attr("height", containerHeight)
//     .style("border", "1px solid #ccc");

//   const g = svg
//     .append("g")
//     .attr("transform", `translate(${margin.left},${margin.top})`);

//   // 初始化缩放行为
//   const zoom = d3
//     .zoom()
//     .scaleExtent([0.5, 5]) // 设置缩放范围
//     .on("zoom", zoomed);

//   // 将缩放行为绑定到 SVG 上
//   svg.call(zoom);

//   function zoomed(event) {
//     g.attr("transform", event.transform);
//   }

//   const root = d3.hierarchy(data);

//   const nodeVerticalSpacing = 65;
//   const nodeHorizontalSpacing = 60;
//   const treeHeight = nodeVerticalSpacing * (root.height + 1);

//   const treeLayout = d3
//     .tree()
//     .size([treeHeight * 1.3, nodeHorizontalSpacing * (root.height + 1)]);
//   treeLayout(root);

//   // Get all nodes
//   const allNodes = root.descendants();

//   // Pass allNodes to the reactive variable
//   if (allNodesRef) {
//     allNodesRef.value = allNodes;
//   }

//   // Display only the first maxNodes nodes
//   const nodesToDisplay = allNodes.slice(0, maxNodes);

//   // Calculate the number of nodes per layer
//   const layerCounts = {};
//   allNodes.forEach((node) => {
//     const depth = node.depth;
//     if (!layerCounts[depth]) {
//       layerCounts[depth] = 0;
//     }
//     layerCounts[depth] += 1;
//   });

//   // Draw links
//   g.selectAll(".link")
//     .data(nodesToDisplay.slice(1))
//     .enter()
//     .append("path")
//     .attr("class", "link")
//     .attr("d", (d) => {
//       const startX = d.parent.x;
//       const startY = d.parent.y;
//       const endX = d.x;
//       const endY = d.y;
//       return `M${startX},${startY} H${endX} V${endY}`;
//     })
//     .style("fill", "none")
//     .style("stroke", "#555")
//     .style("stroke-width", "2px");

//   // Draw nodes
//   const nodes = g
//     .selectAll(".node")
//     .data(nodesToDisplay)
//     .enter()
//     .append("g")
//     .attr("class", "node")
//     .attr("transform", (d) => `translate(${d.x}, ${d.y})`)
//     .on("click", function (event, d) {
//       selectedNode.value = d.data.name;
//       // 更新选中的聚类
//       selectedClusterForAttribute.value = d.data.name;
//     })
//     .on("mouseover", function (event, d) {
//       tooltip.style("visibility", "visible").text(d.data.name);
//     })
//     .on("mousemove", function (event) {
//       tooltip
//         .style("top", event.pageY - 10 + "px")
//         .style("left", event.pageX + 10 + "px");
//     })
//     .on("mouseout", function () {
//       tooltip.style("visibility", "hidden");
//     });

//   // 设置节点大小和颜色
//   nodes
//     .append("circle")
//     .attr("r", (d) => {
//       const nodeCountInLayer = layerCounts[d.depth];
//       return nodeCountInLayer > 10 ? 200/nodeCountInLayer : 20;
//     })
//     .style("fill", (d) => getNodeColor(d))
//     .transition()
//     .duration(300);

//   // Function to get node color
//   function getNodeColor(d) {
//     if (clustersOfFirstNNodes.value.includes(d.data.name)) {
//       return "orange";
//     } else if (highlightedData.some((item) => item.ID === d.data.name)) {
//       return "red"; // Highlighted data for current clustering
//     } else if (generalData.some((item) => item.ID === d.data.name)) {
//       return "green"; // General data
//     } else {
//       return "#999"; // Default color
//     }
//   }
// };

const drawTree = (
  data,
  maxNodes,
  targetSvgId,
  options = {
    selectedNode: ref(""),
    selectedLayer: ref(""),
    selectedLayerStats: ref(""),
    selectedLayerClusters: ref([]),
    allNodesRef: null,
    highlightedData: [],
    generalData: [],
  }
) => {
  const {
    selectedNode,
    selectedLayer,
    selectedLayerStats,
    selectedLayerClusters,
    allNodesRef,
    highlightedData,
    generalData,
  } = options;

  const margin = { top: 50, right: 30, bottom: 50, left: 30 };
  const containerWidth = document.getElementById(targetSvgId).clientWidth;
  const containerHeight = document.getElementById(targetSvgId).clientHeight;

  const width = containerWidth - margin.left - margin.right;
  const height = containerHeight - margin.top - margin.bottom;

  // 创建 tooltip 容器
  const tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("position", "absolute")
    .style("padding", "8px")
    .style("background", "rgba(0, 0, 0, 0.7)")
    .style("color", "#fff")
    .style("border-radius", "4px")
    .style("pointer-events", "none")
    .style("visibility", "hidden")
    .style("font-size", "12px");

  const svg = d3
    .select(`#${targetSvgId}`)
    .attr("width", containerWidth)
    .attr("height", containerHeight)
    .style("border", "1px solid #ccc");

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // 初始化缩放行为
  const zoom = d3
    .zoom()
    .scaleExtent([0.5, 5]) // 设置缩放范围
    .on("zoom", zoomed);

  // 将缩放行为绑定到 SVG 上
  svg.call(zoom);

  function zoomed(event) {
    const transform = event.transform;
    g.attr("transform", transform);
    
    // 动态调整节点半径
    g.selectAll("circle")
      .attr("r", d => d.originalRadius / transform.k);
  }

  const root = d3.hierarchy(data);

  const nodeVerticalSpacing = 65;
  const nodeHorizontalSpacing = 60;
  const treeHeight = nodeVerticalSpacing * (root.height + 1);

  const treeLayout = d3
    .tree()
    .size([treeHeight * 1.3, nodeHorizontalSpacing * (root.height + 1)]);
  treeLayout(root);

  // Get all nodes
  const allNodes = root.descendants();

  // Pass allNodes to the reactive variable
  if (allNodesRef) {
    allNodesRef.value = allNodes;
  }

  // Display only the first maxNodes nodes
  const nodesToDisplay = allNodes.slice(0, maxNodes);

  // Calculate the number of nodes per layer
  const layerCounts = {};
  allNodes.forEach((node) => {
    const depth = node.depth;
    if (!layerCounts[depth]) {
      layerCounts[depth] = 0;
    }
    layerCounts[depth] += 1;
  });

  // Draw links
  g.selectAll(".link")
    .data(nodesToDisplay.slice(1))
    .enter()
    .append("path")
    .attr("class", "link")
    .attr("d", (d) => {
      const startX = d.parent.x;
      const startY = d.parent.y;
      const endX = d.x;
      const endY = d.y;
      return `M${startX},${startY} H${endX} V${endY}`;
    })
    .style("fill", "none")
    .style("stroke", "#555")
    .style("stroke-width", "2px");

  // Draw nodes
  const nodes = g
    .selectAll(".node")
    .data(nodesToDisplay)
    .enter()
    .append("g")
    .attr("class", "node")
    .attr("transform", (d) => `translate(${d.x}, ${d.y})`)
    .on("click", function (event, d) {
      selectedNode.value = d.data.name;
      // 更新选中的聚类
      selectedClusterForAttribute.value = d.data.name;
    })
    .on("mouseover", function (event, d) {
      tooltip.style("visibility", "visible").text(d.data.name);
    })
    .on("mousemove", function (event) {
      tooltip
        .style("top", event.pageY - 10 + "px")
        .style("left", event.pageX + 10 + "px");
    })
    .on("mouseout", function () {
      tooltip.style("visibility", "hidden");
    });

  // 设置节点大小和颜色
  nodes
  .append("circle")
  .attr("r", (d) => {
    const nodeCountInLayer = layerCounts[d.depth];
    // d.originalRadius = nodeCountInLayer>10?(200/(nodeCountInLayer-4)):20 // 保存原始半径
    d.originalRadius = 20 // 保存原始半径
    return d.originalRadius;
  })
  .style("fill", (d) => getNodeColor(d))
  .transition()
  .duration(300);

  // Function to get node color
  function getNodeColor(d) {
    if (clustersOfFirstNNodes.value.includes(d.data.name)) {
      return "orange";
    } else if (highlightedData.some((item) => item.ID === d.data.name)) {
      return "red"; // Highlighted data for current clustering
    } else if (generalData.some((item) => item.ID === d.data.name)) {
      return "green"; // General data
    } else {
      return "#999"; // Default color
    }
  }
};




//Function to count leaves under a node
function countLeaves(node) {
  if (!node.children || node.children.length === 0) {
    return 1;
  }
  return node.children.reduce((sum, child) => sum + countLeaves(child), 0);
}

// Function to count highlighted leaves under a node
function countHighlightedLeaves(node, highlightedData) {
  if (!node.children || node.children.length === 0) {
    // Leaf node
    if (highlightedData.some((item) => item.ID === node.data.name)) {
      return 1;
    } else {
      return 0;
    }
  }
  // Sum over children
  return node.children.reduce(
    (sum, child) => sum + countHighlightedLeaves(child, highlightedData),
    0
  );
}

// Function to count general leaves under a node (not highlighted)
function countGeneralLeaves(node, generalData) {
  if (!node.children || node.children.length === 0) {
    // Leaf node
    if (generalData.some((item) => item.ID === node.data.name)) {
      return 1;
    } else {
      return 0;
    }
  }
  // Sum over children
  return node.children.reduce(
    (sum, child) => sum + countGeneralLeaves(child, generalData),
    0
  );
}

// Update the upper tree
const updateTree = () => {
  d3.select("#chart").selectAll("*").remove();

  const currentResult = clusteringResults.value[selectedClusteringIndex.value];
  if (currentResult && currentResult.dendrogram) {
    drawTree(currentResult.dendrogram, clusterCount.value, "chart", {
      selectedNode: selectedNodeUpper,
      selectedLayer: selectedLayerUpper,
      selectedLayerStats: selectedLayerStatsUpper,
      selectedLayerClusters: selectedLayerClustersUpper,
      allNodesRef: allNodesUpper,
      highlightedData: currentResult.highlightedData, // Pass current clustering's highlighted data
      generalData: filteredSalmonellaData.value, // Pass general data
    });
    currentResult.allNodes = allNodesUpper.value; // Store all nodes
    // updateNodeColors(); // Not needed as colors are set in drawTree
  }
};

// Function to update clusters of first N nodes and draw bar chart
const updateClustersOfFirstNNodes = () => {
  const currentResult = clusteringResults.value[selectedClusteringIndex.value];
  if (currentResult && currentResult.allNodes && numberOfNodes.value > 0) {
    const allNodes = currentResult.allNodes;
    const n = Math.min(numberOfNodes.value, allNodes.length);
    const nodesToInclude = allNodes.slice(0, n);

    clustersOfFirstNNodes.value = nodesToInclude
      .filter((node) => node.data.name !== "root") // Exclude 'root' node
      .map((node) => node.data.name);

    // Compute leaves count for each node, excluding 'root'
    clustersData.value = nodesToInclude
      .filter((node) => node.data.name !== "root") // Exclude 'root' node
      .map((node) => {
        const leavesCount = countLeaves(node);
        const highlightedLeavesCount = countHighlightedLeaves(
          node,
          currentResult.highlightedData
        );
        const generalLeavesCount = countGeneralLeaves(
          node,
          filteredSalmonellaData.value
        );
        return {
          name: node.data.name,
          leavesCount,
          highlightedLeavesCount,
          generalLeavesCount,
        };
      });

    drawBarChart(clustersData.value);
    updateTree(); // Redraw tree to update node colors
  } else {
    clustersOfFirstNNodes.value = [];
    clustersData.value = [];
    drawBarChart(clustersData.value); // Clear the bar chart
    updateTree(); // Redraw tree to update node colors
  }
};

// Function to draw the bar chart (Overall Statistic)
function drawBarChart(data) {
  // Clear existing chart
  d3.select("#bar-chart").selectAll("*").remove();

  const containerWidth = document.getElementById("bar-chart").clientWidth;
  const containerHeight = document.getElementById("bar-chart").clientHeight;

  // Set margins
  const margin = { top: 50, right: 30, bottom: 80, left: 50 };
  const width = containerWidth - margin.left - margin.right;
  const height = containerHeight - margin.top - margin.bottom;

  // Adjust bar width
  const barWidth = 20; // Width of each bar
  const chartWidth = Math.max(width, data.length * barWidth);

  // Create SVG container
  const svg = d3
    .select("#bar-chart")
    .append("svg")
    .attr("width", chartWidth + margin.left + margin.right)
    .attr("height", containerHeight)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // Set x and y scales
  const x = d3
    .scaleBand()
    .domain(data.map((d) => d.name))
    .range([0, chartWidth])
    .padding(0.1);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.leavesCount)])
    .nice()
    .range([height, 0]);

  // Draw x-axis
  svg
    .append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).tickSize(0))
    .selectAll("text")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end")
    .style("font-size", "10px");

  // Draw y-axis
  svg.append("g").call(d3.axisLeft(y));

  // Draw total bars (background bars)
  svg
    .selectAll(".bar-total")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bar-total")
    .attr("x", (d) => x(d.name))
    .attr("y", (d) => y(d.leavesCount))
    .attr("width", x.bandwidth())
    .attr("height", (d) => height - y(d.leavesCount))
    .attr("fill", "#69b3a2");

  // Draw highlighted bars (red overlay bars)
  svg
    .selectAll(".bar-highlighted")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bar-highlighted")
    .attr("x", (d) => x(d.name))
    .attr("y", (d) => y(d.highlightedLeavesCount))
    .attr("width", x.bandwidth())
    .attr("height", (d) => height - y(d.highlightedLeavesCount))
    .attr("fill", "red");

  // Add labels on top of total bars
  svg
    .selectAll(".bar-label")
    .data(data)
    .enter()
    .append("text")
    .attr("class", "bar-label")
    .attr("x", (d) => x(d.name) + x.bandwidth() / 2)
    .attr("y", (d) => y(d.leavesCount) - 5) // Slightly above the bar
    .attr("text-anchor", "middle")
    .text((d) => d.leavesCount)
    .style("fill", "#000")
    .style("font-size", "12px");

  // Add labels on top of highlighted bars (only if count > 0)
  svg
    .selectAll(".bar-highlighted-label")
    .data(data.filter((d) => d.highlightedLeavesCount > 0))
    .enter()
    .append("text")
    .attr("class", "bar-highlighted-label")
    .attr("x", (d) => x(d.name) + x.bandwidth() / 2)
    .attr("y", (d) => y(d.highlightedLeavesCount) - 5) // Slightly above the bar
    .attr("text-anchor", "middle")
    .text((d) => d.highlightedLeavesCount)
    .style("fill", "red")
    .style("font-size", "12px");

  // Add legend
  const legend = svg
    .append("g")
    .attr("class", "legend")
    .attr("transform", "translate(0,-40)");

  legend
    .append("rect")
    .attr("x", 0)
    .attr("width", 20)
    .attr("height", 10)
    .attr("fill", "#69b3a2");

  legend
    .append("text")
    .attr("x", 25)
    .attr("y", 10)
    .text("Green: total clusters number")
    .style("font-size", "12px")
    .attr("alignment-baseline", "middle");

  legend
    .append("rect")
    .attr("x", 0)
    .attr("y", 15)
    .attr("width", 20)
    .attr("height", 10)
    .attr("fill", "red");

  legend
    .append("text")
    .attr("x", 25)
    .attr("y", 25)
    .text("Red: highlighted clusters number")
    .style("font-size", "12px")
    .attr("alignment-baseline", "middle");
}

// Update cluster names for selection
const clusterNames = ref([]);

const updateClusterNames = () => {
  const currentResult = clusteringResults.value[selectedClusteringIndex.value];
  if (currentResult && currentResult.allNodes) {
    clusterNames.value = currentResult.allNodes
      .filter((node) => node.data.name.startsWith("cluster"))
      .map((node) => node.data.name);
    clusterNames.value = sortClusterList(clusterNames.value);
  } else {
    clusterNames.value = [];
  }
};

function sortClusterList(clusterList: string[]): string[] {
  return clusterList.sort((a, b) => {
    // 从字符串中提取数字部分
    const numA = parseInt(a.replace("cluster", ""), 10);
    const numB = parseInt(b.replace("cluster", ""), 10);
    // 比较数字大小
    return numA - numB;
  });
}

// Variables for Attribute Statistic Module
const selectedClusterForAttribute = ref("");
const selectedAttributeForStatistic = ref("");
const attributesForStatistic = [
  "Source",
  "Country",
  "Brand",
  "Serotype",
  "MLST",
];
const isBarChartGenerated = ref(false);

// New reactive variable for table data
const dataForClusterTable = ref([]);

// Variables for table filtering
const selectedTableFilterAttribute = ref("");
const selectedTableFilterValue = ref("");
const tableFilterValues = ref([]);
const attributesForTableFilter = attributesForStatistic;

// Function to handle attribute change in table filter
const onTableFilterAttributeChange = () => {
  selectedTableFilterValue.value = ""; // Reset selected value
  tableFilterValues.value = getTableFilterValues(
    selectedTableFilterAttribute.value
  );
};

// Function to get distinct values for the selected attribute in dataForClusterTable
const getTableFilterValues = (attribute) => {
  if (!attribute || !dataForClusterTable.value.length) return [];

  const values = dataForClusterTable.value
    .map((item) => item[attribute])
    .filter((val) => val !== undefined && val !== null);

  return Array.from(new Set(values));
};

// Computed property for filtered data in the table
const filteredDataForClusterTable = computed(() => {
  let data;
  if (!selectedTableFilterAttribute.value || !selectedTableFilterValue.value) {
    data = dataForClusterTable.value;
  } else {
    data = dataForClusterTable.value.filter(
      (item) =>
        item[selectedTableFilterAttribute.value] ===
        selectedTableFilterValue.value
    );
  }

  // 对数据进行排序，高亮项排在前面
  return data.slice().sort((a, b) => {
    const aHighlighted = isHighlighted(a.ID) ? 1 : 0;
    const bHighlighted = isHighlighted(b.ID) ? 1 : 0;
    return bHighlighted - aHighlighted;
  });
});

// Function to generate attribute statistic bar chart and populate table
const generateAttributeStatistic = () => {
  if (
    selectedClusteringIndex.value === null ||
    !selectedClusterForAttribute.value ||
    !selectedAttributeForStatistic.value
  ) {
    ElMessage.warning("Please select a clustering, cluster, and an attribute.");
    return;
  }

  const currentResult = clusteringResults.value[selectedClusteringIndex.value];
  if (!currentResult) {
    ElMessage.error("Selected clustering not found.");
    return;
  }

  // Get current clustering's highlighted data and general data
  const highlightedData = currentResult.highlightedData;
  const generalData = filteredSalmonellaData.value;

  // Find the selected cluster node
  const selectedClusterNode = findNodeByName(
    currentResult.dendrogram,
    selectedClusterForAttribute.value
  );
  if (!selectedClusterNode) {
    ElMessage.error("Selected cluster not found.");
    return;
  }

  // Get all leaf nodes under the selected cluster
  const leafNodes = getLeafNodes(selectedClusterNode);

  // Get IDs of the leaf nodes
  const leafNodeIds = leafNodes.map((node) => node.name);

  // Filter the data to include only the leaf nodes
  const dataForCluster = currentResult.combinedData.filter((item) =>
    leafNodeIds.includes(item.ID)
  );

  // Set data for the table
  dataForClusterTable.value = dataForCluster;

  // Reset table filters
  selectedTableFilterAttribute.value = "";
  selectedTableFilterValue.value = "";
  tableFilterValues.value = [];

  // Count the occurrences of each attribute value, including highlighted and general data
  const attributeCounts = {};
  dataForCluster.forEach((item) => {
    const attrValue = item[selectedAttributeForStatistic.value] || "Unknown";
    if (!attributeCounts[attrValue]) {
      attributeCounts[attrValue] = { total: 0, highlighted: 0, general: 0 };
    }
    attributeCounts[attrValue].total += 1;

    // Check if item is in highlighted data
    const isHighlightedItem = highlightedData.some(
      (highlightedItem) => highlightedItem.ID === item.ID
    );
    if (isHighlightedItem) {
      attributeCounts[attrValue].highlighted += 1;
    }

    // Check if item is in general data
    const isGeneralItem = generalData.some(
      (generalItem) => generalItem.ID === item.ID
    );
    if (isGeneralItem) {
      attributeCounts[attrValue].general += 1;
    }
  });

  // Prepare data for the bar chart
  const barChartData = Object.keys(attributeCounts).map((key) => ({
    attributeValue: key,
    totalCount: attributeCounts[key].general + attributeCounts[key].highlighted,
    highlightedCount: attributeCounts[key].highlighted,
    generalCount: attributeCounts[key].general, // Optional, if needed elsewhere
  }));

  drawAttributeBarChart(barChartData);
  isBarChartGenerated.value = true;
};

// Function to find node by name
const findNodeByName = (node, name) => {
  if (node.name === name) {
    return node;
  }
  if (node.children) {
    for (let child of node.children) {
      const result = findNodeByName(child, name);
      if (result) {
        return result;
      }
    }
  }
  return null;
};

// Function to get all leaf nodes under a node
const getLeafNodes = (node) => {
  if (!node.children || node.children.length === 0) {
    return [node];
  }
  let leaves = [];
  node.children.forEach((child) => {
    leaves = leaves.concat(getLeafNodes(child));
  });
  return leaves;
};

// Function to draw the attribute bar chart
function drawAttributeBarChart(data) {
  // Clear existing chart
  d3.select("#attribute-bar-chart").selectAll("*").remove();

  const containerWidth = document.getElementById(
    "attribute-bar-chart-container"
  ).clientWidth;
  const containerHeight = document.getElementById(
    "attribute-bar-chart-container"
  ).clientHeight;

  // Set margins
  const margin = { top: 50, right: 30, bottom: 80, left: 50 };
  const width = containerWidth - margin.left - margin.right;
  const height = containerHeight - margin.top - margin.bottom;

  // Adjust bar width
  const barWidth = 20;
  const chartWidth = Math.max(width, data.length * barWidth);

  // Create SVG container
  const svg = d3
    .select("#attribute-bar-chart")
    .append("svg")
    .attr("width", chartWidth + margin.left + margin.right)
    .attr("height", containerHeight)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // Set x and y scales
  const x = d3
    .scaleBand()
    .domain(data.map((d) => d.attributeValue))
    .range([0, chartWidth])
    .padding(0.1);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.totalCount)])
    .nice()
    .range([height, 0]);

  // Draw x-axis
  svg
    .append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).tickSize(0))
    .selectAll("text")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end")
    .style("font-size", "10px");

  // Draw y-axis
  svg.append("g").call(d3.axisLeft(y));

  // Draw total count bars (background bars)
  svg
    .selectAll(".bar-total")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bar-total")
    .attr("x", (d) => x(d.attributeValue))
    .attr("y", (d) => y(d.totalCount))
    .attr("width", x.bandwidth())
    .attr("height", (d) => height - y(d.totalCount))
    .attr("fill", "#69b3a2");

  // Draw highlighted data bars (red bars) overlaying the total count bars
  svg
    .selectAll(".bar-highlighted")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bar-highlighted")
    .attr("x", (d) => x(d.attributeValue))
    .attr("y", (d) => y(d.highlightedCount))
    .attr("width", x.bandwidth())
    .attr("height", (d) => height - y(d.highlightedCount))
    .attr("fill", "red");

  // Add labels for highlighted count
  svg
    .selectAll(".bar-highlighted-label")
    .data(data.filter((d) => d.highlightedCount > 0))
    .enter()
    .append("text")
    .attr("class", "bar-highlighted-label")
    .attr("x", (d) => x(d.attributeValue) + x.bandwidth() / 2)
    .attr("y", (d) => y(d.highlightedCount) - 5)
    .attr("text-anchor", "middle")
    .text((d) => d.highlightedCount)
    .style("fill", "red")
    .style("font-size", "12px");

  // Add labels for total count
  svg
    .selectAll(".bar-total-label")
    .data(data.filter((d) => d.totalCount > 0))
    .enter()
    .append("text")
    .attr("class", "bar-total-label")
    .attr("x", (d) => x(d.attributeValue) + x.bandwidth() / 2)
    .attr("y", (d) => y(d.totalCount) - 5)
    .attr("text-anchor", "middle")
    .text((d) => d.totalCount)
    .style("fill", "#69b3a2")
    .style("font-size", "12px");
}

// Function to download the Attribute Statistic Table as an Excel file
const downloadTableData = () => {
  if (!dataForClusterTable.value || dataForClusterTable.value.length === 0) {
    ElMessage.error("No data to download.");
    return;
  }

  const worksheet = XLSX.utils.json_to_sheet(dataForClusterTable.value);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(
    workbook,
    worksheet,
    "Attribute Statistic Table"
  );

  XLSX.writeFile(workbook, "Attribute_Statistic_Table.xlsx");
};

// Function to download the bar chart as an image
const downloadBarChart = () => {
  const svgElement = document.querySelector("#attribute-bar-chart svg");
  if (!svgElement) {
    ElMessage.error("Bar chart not found.");
    return;
  }

  const serializer = new XMLSerializer();
  const svgString = serializer.serializeToString(svgElement);

  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  const svgSize = svgElement.getBoundingClientRect();
  canvas.width = svgSize.width;
  canvas.height = svgSize.height;

  const img = new Image();
  const svgBlob = new Blob([svgString], {
    type: "image/svg+xml;charset=utf-8",
  });
  const url = URL.createObjectURL(svgBlob);

  img.onload = () => {
    ctx.drawImage(img, 0, 0);
    URL.revokeObjectURL(url);

    const imgURL = canvas.toDataURL("image/png");

    // Create a download link
    const downloadLink = document.createElement("a");
    downloadLink.href = imgURL;
    downloadLink.download = "bar_chart.png";
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
  };

  img.src = url;
};

// Function to check if an ID is highlighted in the current clustering (for Attribute Statistic)
const isHighlighted = (id) => {
  const currentResult = clusteringResults.value[selectedClusteringIndex.value];
  if (!currentResult || !currentResult.highlightedData) {
    return false;
  }
  return currentResult.highlightedData.some((item) => item.ID === id);
};

// Function to check if an ID is general data in the current clustering
const isGeneralData = (id) => {
  return filteredSalmonellaData.value.some((item) => item.ID === id);
};

// Table columns with categories
const tableColumns = ref([
  {
    category: "General",
    columns: ["ID", "Source", "Country", "Brand", "Serotype", "MLST"],
  },
  {
    category: "AST",
    columns: [
      "Amikacin Interpretation",
      "Tobramycin Interpretation",
      "Gentamicin Interpretation",
      "Amox/K Clav Interpretation",
      "Amp/Sulbactam Interpretation",
      "Pip/Tazo Interpretation",
      "Ampicillin Interpretation",
      "Piperacillin Interpretation",
      "Aztreonam Interpretation",
      "Cefepime Interpretation",
      "Cefotaxime Interpretation",
      "Cefoxitin Interpretation",
      "Ceftazidime Interpretation",
      "Cefuroxime Interpretation",
      "Chloramphenicol Interpretation",
      "Ciprofloxacin Interpretation",
      "Levofloxacin Interpretation",
      "Norfloxacin Interpretation",
      "Colistin Interpretation",
      "Doripenem Interpretation",
      "Ertapenem Interpretation",
      "Imipenem Interpretation",
      "Meropenem Interpretation",
      "Fosfomycin Interpretation",
      "Minocycline Interpretation",
      "Tetracycline Interpretation",
      "Nitrofurantoin Interpretation",
      "Trimeth/Sulfa Interpretation",
    ],
  },
  {
    category: "SPI",
    columns: [
      "C63PI",
      "CS54_island",
      "HPI",
      "SESS-LEE",
      "SGI1",
      "SGI2",
      "SPI-1",
      "SPI-2",
      "SPI-3",
      "SPI-4",
      "SPI-5",
      "SPI-6",
      "SPI-7",
      "SPI-8",
      "SPI-9",
      "SPI-10",
      "SPI-11",
      "SPI-12",
      "SPI-13",
      "SPI-14",
    ],
  },
  {
    category: "AMR",
    columns: [
      "Aac2-Ia_AGly",
      "Aac3-IIa_AGly",
      "Aac3-Iva_AGly",
      "Aac3-VIa_AGly",
      "Aac6-Aph2_AGly",
      "Aac6-Iaa_AGly",
      "Aac6-If_AGly",
      "AacAad_AGly",
      "AadA_AGly",
      "AadB_AGly",
      "Ant6-Ia_AGly",
      "Aph3--Ia_AGly",
      "Aph3-IIb_AGly",
      "Aph3-III_AGly",
      "Aph4-Ia_AGly",
      "Aph7_AGly",
      "AphA2_AGly",
      "Sat4A_AGly",
      "Sat-2A_AGly",
      "StrA_AGly",
      "StrB_AGly",
      "VanC1_Gly",
      "VanR-C_Gly",
      "VanS-C_Gly",
      "VanT_Gly",
      "VanX-Yc_Gly",
      "ACI-1_Bla",
      "ACT-MIR_Bla",
      "AmpC1_Ecoli_Bla",
      "AmpC2_Ecoli_Bla",
      "AmpH_Bla",
      "AMPH_Ecoli_Bla",
      "CARB_Bla",
      "CEPA-85_Bla",
      "CfiA_Bla",
      "CMY_Bla",
      "CTX-M-1_Bla",
      "CTX-M-2_Bla",
      "CTX-M-8_Bla",
      "CTX-M-9_Bla",
      "DHA_Bla",
      "LAP_Bla",
      "MrdA_Bla",
      "OXA-1_Bla",
      "OXA-2_Bla",
      "OXA-50_Bla",
      "OXA-61_Bla",
      "SHV-OKP-LEN_Bla",
      "TEM-1D_Bla",
      "Arr_Rif",
      "Cat-86_Phe",
      "CatA1_Phe",
      "CatA2_Phe",
      "CatA3_Phe",
      "CatB7_Phe",
      "CatBx_Phe",
      "CmlA_Phe",
      "FexA_Phe",
      "FloR_Phe",
      "DfrA1_Tmt",
      "DfrA5_Tmt",
      "DfrA7_Tmt",
      "DfrA8_Tmt",
      "DfrA23_Tmt",
      "DfrA27_Tmt",
      "DfrA_Tmt",
      "SulI_Sul",
      "SulII_Sul",
      "SulIII_Sul",
      "Erm42_MLS",
      "ErmB_MLS",
      "ErmF_MLS",
      "LinB_MLS",
      "LnuA_MLS",
      "LnuC_MLS",
      "LnuF_MLS",
      "MphA_MLS",
      "FosA2_Fcyn",
      "FosA_Fcyn",
      "Mcr1_Colistin",
      "Mcr3_Colistin",
      "OqxA_Flq",
      "OqxB_Flq",
      "QepA_Flq",
      "Qnr-A_Flq",
      "Qnr-S_Flq",
      "QnrB_Flq",
      "TetA_Tet",
      "TetB_Tet",
      "TetC_Tet",
      "TetD_Tet",
      "TetG_Tet",
      "TetL_Tet",
      "TetM_Tet",
      "TetO_Tet",
      "TetQ_Tet",
      "TetS_Tet",
      "TetW_Tet",
      "TetX_Tet",
    ],
  },
  {
    category: "plasmid",
    columns: [
      "IncFIA(HI1)",
      "IncHI1A",
      "IncHI2A",
      "IncI1-I(Alpha)",
      "IncHI1B(R27)",
      "IncB/O/K/Z",
      "IncHI2",
      "IncR",
      "IncN",
      "IncQ1",
      "IncX1",
      "IncX4",
      "IncFIB(S)",
      "IncFII",
      "IncFII(S)",
      "IncI(Gamma)",
      "pKPC-CAV1321",
      "ColpVC",
      "Col156",
      "Col(pHAD28)",
      "Col440II",
    ],
  },
]);

// Computed property for table headers
const tableHeaders = computed(() => {
  return tableColumns.value.flatMap((group) => group.columns);
});

// Watcher to update cluster names when selectedClusteringForAttribute changes
watch(selectedClusteringIndex, () => {
  updateClusterNames();
  updateClustersOfFirstNNodes(); // 如果需要同时更新Overall Statistic
});

// onMounted(async () => {
//   await loadSalmonellaData();
//   populateIdValuesMultiple();
// });
</script>

<style scoped>
.settings-section {
  flex: 1;
  display: flex;
  flex-direction: column;

  background-color: #f7f7f7;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.three-settings {
  display: flex;
  flex-direction: row;
}

.clustering-section {
  flex: 1;
  display: flex;
  flex-direction: row;
  height: 150vh;
  background-color: #f7f7f7;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
}

#chart,
#second-chart {
  width: 100%;
  height: 100%;
  pointer-events: all;
}

/* Node styles */
.node circle {
  fill: #999;
  transition: fill 0.3s ease;
  cursor: pointer;
}

.link {
  stroke: #555;
  stroke-width: 2px;
}

/* Y-axis label styles */
.y-axis-label {
  fill: #555;
}

.y-axis-point {
  fill: #555;
  transition: fill 0.3s ease;
  cursor: pointer;
}

#bar-chart,
#attribute-bar-chart {
  width: 100%;
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
}

.bar-total,
.bar {
  transition: fill 0.3s ease;
}

.bar-highlighted {
  transition: fill 0.3s ease;
}

.bar:hover,
.bar-total:hover,
.bar-highlighted:hover {
  fill: #ff6347;
}

/* Adjust axis text */
.axis text {
  font-size: 10px;
}

.tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 8px;
  border-radius: 4px;
  pointer-events: none;
  visibility: hidden;
  font-size: 12px;
}

@media screen and (max-width: 768px) {
  .three-settings {
    flex-direction: column;
  }
  .clustering-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 150vh;
    background-color: #f7f7f7;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    overflow: hidden;
  }
}
</style>
