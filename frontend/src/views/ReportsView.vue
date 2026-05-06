<template>
  <div class="page">
    <div class="header">
      <h1>Reportes e Historial</h1>
      <div class="actions">
        <button class="btn btn-primary btn-large" @click="downloadXlsx"><i class="pi pi-file-excel"></i> Exportar Excel</button>
      </div>
    </div>

    <section class="card filters">
      <DatePicker v-model="filters.date_from" dateFormat="dd/mm/yy" showIcon placeholder="Fecha Desde" />
      <DatePicker v-model="filters.date_to" dateFormat="dd/mm/yy" showIcon placeholder="Fecha Hasta" />
      <Select v-model="filters.record_type" :options="recordOptions" optionLabel="label" optionValue="value" />
      <Select v-model="filters.payment_method" :options="paymentOptions" optionLabel="label" optionValue="value" placeholder="Todos los pagos" />
      <button class="btn btn-primary" @click="load">Aplicar</button>
    </section>

    <div class="kpis">
      <div class="kpi-card">
        <span>Total General</span>
        <strong>{{ formatClp(summary?.totals.general_clp || 0) }}</strong>
      </div>
      <div class="kpi-card">
        <span>Total Cancha</span>
        <strong>{{ formatClp(summary?.totals.course_clp || 0) }}</strong>
      </div>
      <div class="kpi-card">
        <span>Total Driving Range</span>
        <strong>{{ formatClp(summary?.totals.range_clp || 0) }}</strong>
      </div>
      <div class="kpi-card">
        <span>Personas</span>
        <strong>{{ summary?.totals.people_count || 0 }}</strong>
      </div>
      <div class="kpi-card">
        <span>Canastos</span>
        <strong>{{ summary?.totals.baskets_count || 0 }}</strong>
      </div>
    </div>

    <div class="charts-grid">
      <section class="card chart-card">
        <h3>Cobro por día (Cancha vs Driving Range)</h3>
        <div class="chart-wrapper">
          <Line v-if="lineData" :data="lineData" :options="chartOptions" />
        </div>
      </section>
      <section class="card chart-card">
        <h3>Totales por método de pago</h3>
        <div class="chart-wrapper">
          <Bar v-if="barData" :data="barData" :options="chartOptions" />
        </div>
      </section>
    </div>

    <section class="card">
      <h3>Registros filtrados</h3>
      <table>
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Fecha</th>
            <th>Nombre</th>
            <th>Cantidad</th>
            <th>Monto</th>
            <th>Pago</th>
            <th>Usuario</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in paginatedRows" :key="row.key">
            <td>{{ row.type }}</td>
            <td>{{ row.date }}</td>
            <td>{{ row.name }}</td>
            <td>{{ row.qty }}</td>
            <td>{{ formatClp(row.amount) }}</td>
            <td>{{ paymentLabel(row.payment) }}</td>
            <td>{{ row.user }}</td>
          </tr>
          <tr v-if="flatRows.length === 0">
            <td colspan="7" class="empty">Sin datos para filtros aplicados</td>
          </tr>
        </tbody>
      </table>
      
      <div class="pagination" v-if="totalPages > 1">
        <button class="btn btn-secondary" :disabled="currentPage === 1" @click="currentPage--">
          <i class="pi pi-chevron-left"></i> Anterior
        </button>
        <span class="page-info">Página {{ currentPage }} de {{ totalPages }}</span>
        <button class="btn btn-secondary" :disabled="currentPage === totalPages" @click="currentPage++">
          Siguiente <i class="pi pi-chevron-right"></i>
        </button>
      </div>
    </section>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { Bar, Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { fetchReportsSummary, fetchReportsRecords, buildExportXlsxUrl, downloadBinary } from "@/services/golf";
import type { ReportsSummaryResponse, ReportsRecordsResponse } from "@/services/golf";

import DatePicker from 'primevue/datepicker';
import Select from 'primevue/select';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const recordOptions = [
  { label: 'Cancha + Driving Range', value: 'BOTH' },
  { label: 'Solo Cancha', value: 'COURSE' },
  { label: 'Solo Driving Range', value: 'RANGE' }
];

const paymentOptions = [
  { label: 'Todos los pagos', value: '' },
  { label: 'Efectivo', value: 'CASH' },
  { label: 'Tarjeta', value: 'CARD' },
  { label: 'Transferencia', value: 'TRANSFER' },
  { label: 'Otro', value: 'OTHER' }
];

const today = new Date();

const filters = ref({
  date_from: today,
  date_to: today,
  record_type: "BOTH",
  payment_method: "",
});

const summary = ref<ReportsSummaryResponse | null>(null);
const records = ref<ReportsRecordsResponse | null>(null);
const error = ref("");

const currentPage = ref(1);
const itemsPerPage = 10;

const totalPages = computed(() => Math.ceil(flatRows.value.length / itemsPerPage) || 1);

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return flatRows.value.slice(start, start + itemsPerPage);
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
};

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(value);
}

function paymentLabel(method: string) {
  return { CASH: "Efectivo", CARD: "Tarjeta", TRANSFER: "Transferencia", OTHER: "Otro" }[method] || method;
}

const lineData = computed(() => {
  const rows = summary.value?.series.by_day || [];
  if (!rows.length) return null;
  return {
    labels: rows.map((r) => r.date),
    datasets: [
      {
        label: "Cancha",
        data: rows.map((r) => r.course_total_clp),
        borderColor: "#2b59c3",
        backgroundColor: "rgba(43,89,195,0.2)",
      },
      {
        label: "Driving Range",
        data: rows.map((r) => r.range_total_clp),
        borderColor: "#20a67a",
        backgroundColor: "rgba(32,166,122,0.2)",
      },
    ],
  };
});

const barData = computed(() => {
  const payments = summary.value?.payment_totals;
  if (!payments) return null;
  return {
    labels: ["Efectivo", "Tarjeta", "Transferencia", "Otro"],
    datasets: [
      {
        label: "CLP",
        data: [payments.CASH || 0, payments.CARD || 0, payments.TRANSFER || 0, payments.OTHER || 0],
        backgroundColor: ["#f59e0b", "#3b82f6", "#10b981", "#8b5cf6"],
      },
    ],
  };
});

const flatRows = computed(() => {
  const result: Array<{
    key: string;
    type: string;
    date: string;
    name: string;
    qty: number;
    amount: number;
    payment: string;
    user: string;
  }> = [];

  records.value?.course_entries?.forEach((item) => {
    result.push({
      key: `c-${item.id}`,
      type: "Cancha",
      date: new Date(item.created_at).toLocaleString("es-CL", { hour12: false }),
      name: item.customer_name,
      qty: item.people_count,
      amount: item.amount_clp,
      payment: item.payment_method,
      user: item.created_by_name,
    });
  });

  records.value?.range_orders?.forEach((item) => {
    result.push({
      key: `r-${item.id}`,
      type: "Driving Range",
      date: new Date(item.created_at).toLocaleString("es-CL", { hour12: false }),
      name: item.customer_name,
      qty: item.baskets_count,
      amount: item.total_amount_clp,
      payment: item.payment_method,
      user: item.created_by_name,
    });
  });

  return result.sort((a, b) => (a.date < b.date ? 1 : -1));
});

function formatDateForApi(d: any) {
  if (!d) return "";
  const date = new Date(d);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

async function load() {
  error.value = "";
  const params: Record<string, string> = {
    date_from: formatDateForApi(filters.value.date_from),
    date_to: formatDateForApi(filters.value.date_to),
    record_type: filters.value.record_type,
  };
  if (filters.value.payment_method) params.payment_method = filters.value.payment_method;

  try {
    summary.value = await fetchReportsSummary(params);
    records.value = await fetchReportsRecords(params);
    currentPage.value = 1;
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudieron cargar reportes";
  }
}

async function downloadXlsx() {
  const fromStr = formatDateForApi(filters.value.date_from);
  const toStr = formatDateForApi(filters.value.date_to);
  const path = buildExportXlsxUrl({ date_from: fromStr, date_to: toStr });
  await downloadBinary(path, `reporte-${fromStr}-${toStr}.xlsx`, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
}

onMounted(load);
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.actions {
  display: flex;
  gap: 8px;
}
.btn-large {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--minttu-radius-md);
}
.card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 20px;
  box-shadow: var(--minttu-shadow-soft);
}
.filters {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}
input,
:deep(.p-select),
:deep(.p-datepicker-input) {
  border: 1px solid var(--minttu-border);
  border-radius: var(--minttu-radius-sm);
  background: var(--minttu-white);
  color: var(--minttu-text);
  font-family: inherit;
  transition: all 0.2s ease;
  width: 100%;
}
input {
  padding: 10px 14px;
}
input:focus,
:deep(.p-select:not(.p-disabled).p-focus),
:deep(.p-datepicker-input:focus) {
  border-color: var(--minttu-primary);
  box-shadow: 0 0 0 3px rgba(27, 67, 50, 0.1);
  outline: none;
}
:deep(.p-datepicker) {
  width: 100%;
}
.kpis {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}
.kpi-card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 16px;
  box-shadow: var(--minttu-shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.kpi-card span {
  color: var(--minttu-gray);
  font-size: 12px;
}
.kpi-card strong {
  font-size: 18px;
}
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.charts-grid .chart-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.chart-wrapper {
  position: relative;
  height: 300px;
  width: 100%;
}
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}
th,
td {
  text-align: left;
  border-bottom: 1px solid var(--minttu-border);
  padding: 12px 14px;
  font-size: 14px;
}
th {
  background: var(--minttu-bg);
  color: var(--minttu-primary);
  font-weight: 600;
}
th:first-child { border-top-left-radius: 8px; }
th:last-child { border-top-right-radius: 8px; }
tbody tr:hover { background-color: var(--minttu-bg); }
.empty {
  text-align: center;
  color: var(--minttu-gray);
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding-top: 20px;
  margin-top: 10px;
  border-top: 1px solid var(--minttu-border);
}
.page-info {
  font-size: 14px;
  font-weight: 500;
  color: var(--minttu-gray);
}
.error {
  color: #c0392b;
}

@media (max-width: 1024px) {
  .header {
    flex-direction: column;
    align-items: stretch;
  }
  .filters,
  .kpis,
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
