<template>
  <div class="page">
    <div class="header">
      <div>
        <button class="action back-action" type="button" @click="router.push('/closures')">
          <i class="pi pi-arrow-left"></i> Volver
        </button>
        <h1>Detalle de Cierre</h1>
        <p v-if="closure" class="subtitle">
          {{ scopeLabel(closure.scope) }} · {{ formatDateLocal(closure.operational_date) }}
        </p>
      </div>
      <button v-if="closure" class="btn btn-primary" type="button" @click="downloadExcel">
        <i class="pi pi-file-excel"></i> Excel
      </button>
    </div>

    <p v-if="loading" class="empty">Cargando detalle...</p>
    <p v-else-if="error" class="error">{{ error }}</p>

    <template v-else-if="closure && detail">
      <section class="summary-grid">
        <div class="kpi-card">
          <span>Total General</span>
          <strong>{{ formatClp(closure.total_general_clp) }}</strong>
        </div>
        <div v-if="closure.scope !== 'RANGE'" class="kpi-card">
          <span>Total Cancha</span>
          <strong>{{ formatClp(closure.total_course_clp) }}</strong>
        </div>
        <div v-if="closure.scope !== 'COURSE'" class="kpi-card">
          <span>Total Driving Range</span>
          <strong>{{ formatClp(closure.total_range_clp) }}</strong>
        </div>
        <div class="kpi-card">
          <span>Efectivo</span>
          <strong>{{ formatClp(closure.total_cash_clp) }}</strong>
        </div>
        <div class="kpi-card">
          <span>Tarjeta</span>
          <strong>{{ formatClp(closure.total_card_clp) }}</strong>
        </div>
        <div class="kpi-card">
          <span>Transferencia</span>
          <strong>{{ formatClp(closure.total_transfer_clp) }}</strong>
        </div>
        <div v-if="closure.scope !== 'RANGE'" class="kpi-card">
          <span>Personas</span>
          <strong>{{ formatNumber(closure.total_people) }}</strong>
        </div>
        <div v-if="closure.scope !== 'COURSE'" class="kpi-card">
          <span>Canastos</span>
          <strong>{{ formatNumber(closure.total_baskets) }}</strong>
        </div>
      </section>

      <section class="card detail-meta">
        <div><strong>Usuario cierre:</strong> {{ closure.closed_by_name }}</div>
        <div><strong>Hora cierre:</strong> {{ formatDateTime(closure.closed_at) }}</div>
        <div v-if="closure.adjustment_clp"><strong>Ajuste manual:</strong> {{ formatClp(closure.adjustment_clp) }}</div>
        <div><strong>Observaciones:</strong> {{ closure.notes || "-" }}</div>
      </section>

      <div class="charts-grid">
        <section class="card chart-card">
          <h3>Totales por Método de Pago</h3>
          <div class="chart-wrapper">
            <Doughnut :data="paymentChartData" :options="chartOptions" />
          </div>
        </section>
        <section class="card chart-card">
          <h3>Cancha vs Driving Range</h3>
          <div class="chart-wrapper">
            <Bar :data="areaChartData" :options="chartOptions" />
          </div>
        </section>
      </div>

      <section v-if="closure.scope !== 'RANGE'" class="card detail-section">
        <div class="section-header">
          <h3>Entradas a Cancha</h3>
          <strong>{{ formatClp(closure.total_course_clp) }}</strong>
        </div>
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Hora</th>
                <th>Nombre</th>
                <th>Personas</th>
                <th>Monto</th>
                <th>Pago</th>
                <th>Usuario</th>
                <th>Notas</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in detail.course_entries" :key="entry.id">
                <td>{{ formatTime(entry.created_at) }}</td>
                <td>{{ entry.customer_name }}</td>
                <td>{{ formatNumber(entry.people_count) }}</td>
                <td>{{ formatClp(entry.amount_clp) }}</td>
                <td>{{ paymentLabel(entry.payment_method) }}</td>
                <td>{{ entry.created_by_name }}</td>
                <td>{{ entry.notes || "-" }}</td>
              </tr>
              <tr v-if="detail.course_entries.length === 0">
                <td colspan="7" class="empty">Sin entradas de cancha</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="closure.scope !== 'COURSE'" class="card detail-section">
        <div class="section-header">
          <h3>Pedidos Driving Range</h3>
          <strong>{{ formatClp(closure.total_range_clp) }}</strong>
        </div>
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Hora</th>
                <th>Nombre</th>
                <th>Canastos</th>
                <th>Unitario</th>
                <th>Total</th>
                <th>Pago</th>
                <th>Usuario</th>
                <th>Notas</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in detail.range_orders" :key="order.id">
                <td>{{ formatTime(order.created_at) }}</td>
                <td>{{ order.customer_name }}</td>
                <td>{{ formatNumber(order.baskets_count) }}</td>
                <td>{{ formatClp(order.unit_price_clp) }}</td>
                <td>{{ formatClp(order.total_amount_clp) }}</td>
                <td>{{ paymentLabel(order.payment_method) }}</td>
                <td>{{ order.created_by_name }}</td>
                <td>{{ order.notes || "-" }}</td>
              </tr>
              <tr v-if="detail.range_orders.length === 0">
                <td colspan="8" class="empty">Sin pedidos de driving range</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="card detail-section">
        <div class="section-header">
          <h3>Totales por Usuario</h3>
        </div>
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Cancha</th>
                <th>Driving Range</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="userTotal in detailUserTotals" :key="userTotal.user_id || userTotal.email || userTotal.name">
                <td>{{ userTotal.name }}</td>
                <td>{{ formatClp(userTotal.course_clp || 0) }}</td>
                <td>{{ formatClp(userTotal.range_clp || 0) }}</td>
                <td>{{ formatClp(userTotal.total_clp || 0) }}</td>
              </tr>
              <tr v-if="detailUserTotals.length === 0">
                <td colspan="4" class="empty">Sin totales por usuario</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Bar, Doughnut } from "vue-chartjs";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";
import {
  buildExportXlsxUrl,
  downloadBinary,
  fetchClosureDetail,
  type CashClosureDetail,
  type ClosureScope,
} from "@/services/golf";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const route = useRoute();
const router = useRouter();

const detail = ref<CashClosureDetail | null>(null);
const loading = ref(false);
const error = ref("");

const closure = computed(() => detail.value?.closure || null);
const detailUserTotals = computed(() => detail.value?.per_user_totals || []);

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "bottom" as const,
    },
  },
};

const paymentChartData = computed(() => ({
  labels: ["Efectivo", "Tarjeta", "Transferencia", "Otro"],
  datasets: [
    {
      data: [
        closure.value?.total_cash_clp || 0,
        closure.value?.total_card_clp || 0,
        closure.value?.total_transfer_clp || 0,
        closure.value?.total_other_clp || 0,
      ],
      backgroundColor: ["#f59e0b", "#3b82f6", "#10b981", "#8b5cf6"],
      borderWidth: 0,
    },
  ],
}));

const areaChartData = computed(() => ({
  labels: ["Cancha", "Driving Range"],
  datasets: [
    {
      label: "CLP",
      data: [closure.value?.total_course_clp || 0, closure.value?.total_range_clp || 0],
      backgroundColor: ["#1b4332", "#2b59c3"],
      borderRadius: 6,
    },
  ],
}));

function formatDateLocal(val: string) {
  return new Date(`${val}T00:00:00`).toLocaleDateString("es-CL");
}

function formatDateTime(val: string) {
  return new Date(val).toLocaleString("es-CL", { hour12: false });
}

function formatTime(val: string) {
  return new Date(val).toLocaleTimeString("es-CL", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("es-CL", { maximumFractionDigits: 0 }).format(value || 0);
}

function paymentLabel(method: string) {
  const labels: Record<string, string> = {
    CASH: "Efectivo",
    CARD: "Tarjeta",
    TRANSFER: "Transferencia",
    OTHER: "Otro",
  };
  return labels[method] || method;
}

function scopeLabel(scope: ClosureScope) {
  if (scope === "COURSE") return "Cancha";
  if (scope === "RANGE") return "Driving Range";
  return "Final";
}

async function load() {
  const id = Number(route.params.id);
  if (!Number.isFinite(id)) {
    error.value = "Cierre inválido";
    return;
  }

  loading.value = true;
  error.value = "";
  try {
    detail.value = await fetchClosureDetail(id);
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo cargar el detalle del cierre";
  } finally {
    loading.value = false;
  }
}

async function downloadExcel() {
  if (!closure.value) return;
  const opDate = closure.value.operational_date;
  const path = buildExportXlsxUrl({ date_from: opDate, date_to: opDate });
  await downloadBinary(path, `cierre-${opDate}.xlsx`, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
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
  align-items: flex-start;
  gap: 16px;
}
.header h1 {
  margin: 8px 0 0;
}
.subtitle {
  color: var(--minttu-gray);
  margin: 4px 0 0;
}
.card,
.kpi-card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  box-shadow: var(--minttu-shadow-soft);
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}
.kpi-card {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}
.kpi-card span {
  color: var(--minttu-gray);
  font-size: 12px;
}
.kpi-card strong {
  color: var(--minttu-primary);
  font-size: 18px;
}
.detail-meta {
  padding: 18px 20px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  font-size: 14px;
}
.charts-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
  gap: 12px;
}
.chart-card {
  padding: 20px;
}
.chart-card h3,
.detail-section h3 {
  margin: 0;
  color: var(--minttu-primary);
  font-size: 16px;
}
.chart-wrapper {
  position: relative;
  height: 280px;
  margin-top: 14px;
}
.detail-section {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
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
  white-space: nowrap;
}
th {
  background: var(--minttu-bg);
  color: var(--minttu-primary);
  font-weight: 600;
}
th:first-child {
  border-top-left-radius: 8px;
}
th:last-child {
  border-top-right-radius: 8px;
}
tbody tr:hover {
  background-color: var(--minttu-bg);
}
.action {
  border: none;
  background: var(--minttu-border);
  color: var(--minttu-primary);
  border-radius: 6px;
  padding: 6px 12px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}
.action:hover {
  background: var(--minttu-primary);
  color: var(--minttu-white);
}
.back-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.empty {
  text-align: center;
  color: var(--minttu-gray);
}
.error {
  color: #c0392b;
}

@media (max-width: 1024px) {
  .summary-grid,
  .detail-meta,
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header,
  .section-header {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
