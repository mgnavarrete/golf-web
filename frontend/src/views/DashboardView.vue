<template>
  <div class="dashboard-page">
    <div class="header-row">
      <div>
        <h1>Resumen Diario</h1>
        <p>Control operativo de caja para cancha y range</p>
      </div>
      <div class="header-actions">
        <DatePicker v-model="operationalDateObj" dateFormat="dd/mm/yy" showIcon placeholder="Fecha Operativa" class="date-input" />
        <button class="btn btn-secondary" @click="loadSummary" :disabled="loading">
          <i :class="loading ? 'pi pi-spin pi-spinner' : 'pi pi-refresh'"></i>
          Actualizar
        </button>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card">
        <span>Total Hoy</span>
        <strong>{{ formatClp(summary?.total_general_clp || 0) }}</strong>
      </div>
      <div class="kpi-card">
        <span>Cancha</span>
        <strong>{{ formatClp(summary?.total_course_clp || 0) }}</strong>
      </div>
      <div class="kpi-card">
        <span>Driving Range</span>
        <strong>{{ formatClp(summary?.total_range_clp || 0) }}</strong>
      </div>
      <div class="kpi-card">
        <span>Personas</span>
        <strong>{{ summary?.total_people || 0 }}</strong>
      </div>
      <div class="kpi-card">
        <span>Registros Cancha</span>
        <strong>{{ summary?.total_course_records || 0 }}</strong>
      </div>
      <div class="kpi-card">
        <span>Canastos</span>
        <strong>{{ summary?.total_baskets || 0 }}</strong>
      </div>
    </div>

    <div class="split-grid">
      <section class="panel">
        <h3>Últimas Entradas a Cancha</h3>
        <table>
          <thead>
            <tr>
              <th>Hora</th>
              <th>Nombre</th>
              <th>Personas</th>
              <th>Monto</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in summary?.latest_course_entries || []" :key="item.id">
              <td>{{ formatTime(item.created_at) }}</td>
              <td>{{ item.customer_name }}</td>
              <td>{{ item.people_count }}</td>
              <td>{{ formatClp(item.amount_clp) }}</td>
            </tr>
            <tr v-if="(summary?.latest_course_entries || []).length === 0">
              <td colspan="4" class="empty">Sin registros</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="panel">
        <h3>Últimos Pedidos Driving Range</h3>
        <table>
          <thead>
            <tr>
              <th>Hora</th>
              <th>Nombre</th>
              <th>Canastos</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in summary?.latest_range_orders || []" :key="item.id">
              <td>{{ formatTime(item.created_at) }}</td>
              <td>{{ item.customer_name }}</td>
              <td>{{ item.baskets_count }}</td>
              <td>{{ formatClp(item.total_amount_clp) }}</td>
            </tr>
            <tr v-if="(summary?.latest_range_orders || []).length === 0">
              <td colspan="4" class="empty">Sin registros</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { fetchDashboardSummary, type DailySummary } from "@/services/golf";

import DatePicker from 'primevue/datepicker';

const loading = ref(false);
const error = ref("");
const summary = ref<DailySummary | null>(null);
const operationalDateObj = ref(new Date());

function formatDateForApi(d: any) {
  if (!d) return "";
  const date = new Date(d);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(
    value
  );
}

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString("es-CL", { hour: "2-digit", minute: "2-digit" });
}

async function loadSummary() {
  loading.value = true;
  error.value = "";
  try {
    const formattedDate = formatDateForApi(operationalDateObj.value);
    summary.value = await fetchDashboardSummary(formattedDate);
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo cargar el resumen";
  } finally {
    loading.value = false;
  }
}

onMounted(loadSummary);
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
:deep(.p-datepicker-input) {
  border: 1px solid var(--minttu-border);
  border-radius: var(--minttu-radius-sm);
  background: var(--minttu-white);
  color: var(--minttu-text);
  font-family: inherit;
  transition: all 0.2s ease;
  padding: 10px 14px;
}
:deep(.p-datepicker-input:focus) {
  border-color: var(--minttu-primary);
  box-shadow: 0 0 0 3px rgba(27, 67, 50, 0.1);
  outline: none;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
.kpi-card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 20px;
  box-shadow: var(--minttu-shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.kpi-card span {
  color: var(--minttu-gray);
  font-size: 13px;
}
.kpi-card strong {
  font-size: 21px;
}
.split-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.panel {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 20px;
  box-shadow: var(--minttu-shadow-soft);
}
.panel table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}
.panel th,
.panel td {
  text-align: left;
  border-bottom: 1px solid var(--minttu-border);
  padding: 12px 14px;
  font-size: 14px;
}
.panel th {
  background: var(--minttu-bg);
  color: var(--minttu-primary);
  font-weight: 600;
}
.panel th:first-child { border-top-left-radius: 8px; }
.panel th:last-child { border-top-right-radius: 8px; }
.panel tbody tr:hover { background-color: var(--minttu-bg); }
.empty {
  text-align: center !important;
  color: var(--minttu-gray);
}
.error {
  color: #c0392b;
}

@media (max-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .split-grid {
    grid-template-columns: 1fr;
  }
  .header-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
