<template>
  <div>
    <h3>Serovar Monitoring</h3>
    <div v-if="serovarIncreaseRecords.length > 0">
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <!-- <th>Date</th> -->
              <th>Serotype</th>
              <th>Initial Count</th>
              <th>Final Count</th>
              <th>Increase</th>
            </tr>
          </thead>
          <tbody>
            <tr 
            v-for="record in serovarIncreaseRecords"
              :key="record.name"
              @click="handleSerotypeClick(record.name)" 
              style="cursor: pointer; color: blue;"
            >
              <!-- <td>{{ record.date }}</td> -->
              <td>{{ record.name }}</td>
              <td>{{ record.initialCount }}</td>
              <td>{{ record.finalCount }}</td>
              <td>{{ record.increase }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div>
        Date from {{ formattedStartDate }} to {{ formattedEndDate }}
      </div>
    </div>
    <div v-else>
      No records found for the selected date.
    </div>

        <!-- Line Chart Container -->
    <div v-if="lineChartData">
      <h4>Trend for {{ selectedSerotype }}</h4>
      <v-chart :option="lineChartOption" autoresize style="height: 400px;"></v-chart>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { defineProps, ref, watch, computed, onMounted } from 'vue';
//1.24 larry: 引入echarts
import VChart from 'vue-echarts';
import * as echarts from 'echarts';


interface Record {
  ID: string[];
  Date: string[];
  Serotype: string[];
}

//1.24 larry: 关于linechart
const selectedSerotype = ref(''); // 当前选中的 serotype
const lineChartData = ref<{ date: string; count: number }[] | null>(null); // 图表数据
const lineChartOption = ref({}); // 图表配置
//1.24 larry: 实现处理sero点击逻辑
const handleSerotypeClick = (serotype: string) => {
  selectedSerotype.value = serotype;

  // 筛选出与当前 serotype 对应的数据
  const dataForSerotype = props.seroData
    .filter((record) => record.Serotype[0] === serotype)
    .map((record) => ({
      date: record.Date[0], // 获取日期
      count: 1, // 假设每条记录计数为 1，根据需求修改
    }));

  // 统计每个日期的总数
  const aggregatedData = dataForSerotype.reduce((acc, { date, count }) => {
    if (!acc[date]) {
      acc[date] = 0;
    }
    acc[date] += count;
    return acc;
  }, {} as Record<string, number>);

  // 转换为图表所需格式
  lineChartData.value = Object.entries(aggregatedData).map(([date, count]) => ({
    date,
    count,
  }));

  // 更新图表配置
  updateLineChart();
};

//1.24 larry: 实现更新图表配置
const updateLineChart = () => {
  if (!lineChartData.value || lineChartData.value.length === 0) {
    // 如果没有数据，设置默认提示
    lineChartOption.value = {
      title: {
        text: 'No Data Available',
        left: 'center',
      },
    };
    return;
  }

  // 更新图表的配置
  lineChartOption.value = {
    title: {
      text: `Trend for ${selectedSerotype.value}`,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: lineChartData.value.map((item) => item.date), // 横轴日期
      axisLabel: {
        rotate: 45, // 旋转日期标签，防止重叠
      },
    },
    yAxis: {
      type: 'value',
      name: 'Total Count',
    },
    series: [
      {
        type: 'line',
        data: lineChartData.value.map((item) => item.count), // 纵轴计数
        smooth: true, // 平滑曲线
        lineStyle: {
          color: '#007BFF', // 折线颜色
        },
        areaStyle: {
          opacity: 0.1, // 折线下方填充区域
        },
      },
    ],
  };
};



const props = defineProps<{ seroData: Record[]; startDate: Date | null; endDate: Date | null }>();

const serovarIncreaseRecords = ref<
  { date: string; name: string; initialCount: number; finalCount: number; increase: number }[]
>([]);

const applyFilters = (startDate: Date, endDate: Date) => {
  const initialCounts: { [key: string]: number } = {};
  const finalCounts: { [key: string]: number } = {};

  const startOfNextMonth = new Date(startDate.getFullYear(), startDate.getMonth() + 1, 1);

  props.seroData.forEach((record) => {
    const recordDate = new Date(record.Date[0]);

    //1/24: 过滤掉非指定日期范围内的数据
        // 忽略日期为 "1900-01-01" 的记录
        if (recordDate.toISOString().split('T')[0] === '1900-01-01') {
      return;
    }

    // 初始统计
    if (recordDate >= startDate && recordDate < startOfNextMonth) {
      initialCounts[record.Serotype[0]] = (initialCounts[record.Serotype[0]] || 0) + 1;
    }

    // 最终统计
    if (recordDate >= startDate && recordDate <= endDate) {
      finalCounts[record.Serotype[0]] = (finalCounts[record.Serotype[0]] || 0) + 1;
    }
  });

  // 根据过滤结果生成记录
  serovarIncreaseRecords.value = Object.keys(finalCounts).map((serotype) => ({
    date: formattedStartDate.value, // 保留起始日期作为展示
    name: serotype,
    initialCount: initialCounts[serotype] || 0,
    finalCount: finalCounts[serotype] || 0,
    increase: (finalCounts[serotype] || 0) - (initialCounts[serotype] || 0),
  }));
};

const formattedStartDate = computed(() =>
  props.startDate ? new Date(props.startDate).toISOString().split('T')[0] : ''
);
const formattedEndDate = computed(() =>
  props.endDate ? new Date(props.endDate).toISOString().split('T')[0] : ''
);




watch(
  () => [props.seroData, props.startDate, props.endDate],
  ([newSeroData, newStartDate, newEndDate]) => {
    if (newStartDate && newEndDate && newSeroData) {
      applyFilters(new Date(newStartDate), new Date(newEndDate));
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.startDate && props.endDate) {
    applyFilters(new Date(props.startDate), new Date(props.endDate));
  }
});
</script>

<style scoped>
.table-container {
  display: block;
  max-height: 400px;
  overflow-y: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
  position: sticky;
  top: 0;
  z-index: 1;
}

tbody tr {
  display: table;
  width: 100%;
  table-layout: fixed;
}

thead,
tbody {
  display: table;
  width: 100%;
  table-layout: fixed;
}
</style>
