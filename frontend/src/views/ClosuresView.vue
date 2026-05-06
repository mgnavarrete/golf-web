<template>
  <div class="page">
    <div class="header">
      <h1>Cierre de Caja Diario</h1>
      <div class="controls">
        <DatePicker v-model="operationalDateObj" dateFormat="dd/mm/yy" showIcon />
        <button class="btn btn-secondary" @click="load">Actualizar Día</button>
      </div>
    </div>

    <section class="card actions">
      <button class="btn btn-primary" @click="closeScope('COURSE')" :disabled="loading">Cerrar Cancha</button>
      <button class="btn btn-primary" @click="closeScope('RANGE')" :disabled="loading">Cerrar Driving Range</button>
      <button class="btn btn-accent" @click="closeScope('FINAL')" :disabled="loading">Cierre Final</button>
    </section>

    <section class="card">
      <h3>Estado del Día Seleccionado</h3>
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Área</th>
            <th>Estado</th>
            <th>Total General</th>
            <th>Usuario Cierre</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="closure in closures" :key="closure.id">
            <td>{{ closure.operational_date }}</td>
            <td>{{ closure.scope }}</td>
            <td>{{ closure.status }}</td>
            <td>{{ formatClp(closure.total_general_clp) }}</td>
            <td>{{ closure.closed_by_name }}</td>
            <td>
              <button v-if="canReopen && closure.status === 'CLOSED'" class="action" @click="reopen(closure.scope)">
                Reabrir
              </button>
            </td>
          </tr>
          <tr v-if="closures.length === 0">
            <td colspan="6" class="empty">No hay cierres para la fecha</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="card">
      <div class="header">
        <h3>Historial de Cierres</h3>
        <div class="controls">
          <DatePicker v-model="historyFilters.date_from" dateFormat="dd/mm/yy" showIcon placeholder="Desde" />
          <DatePicker v-model="historyFilters.date_to" dateFormat="dd/mm/yy" showIcon placeholder="Hasta" />
          <button class="btn btn-secondary" @click="loadHistory">Filtrar Historial</button>
        </div>
      </div>
      <table style="margin-top: 16px;">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Área</th>
            <th>Estado</th>
            <th>Total General</th>
            <th>Usuario Cierre</th>
            <th>Descarga</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="closure in paginatedHistory" :key="closure.id">
            <td>{{ formatDateLocal(closure.operational_date) }}</td>
            <td>{{ closure.scope }}</td>
            <td>{{ closure.status }}</td>
            <td>{{ formatClp(closure.total_general_clp) }}</td>
            <td>{{ closure.closed_by_name }}</td>
            <td>
              <button class="action" @click="downloadExcel(closure.operational_date)">
                <i class="pi pi-file-excel"></i> Excel
              </button>
            </td>
          </tr>
          <tr v-if="historyClosures.length === 0">
            <td colspan="6" class="empty">No hay historial para estas fechas</td>
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
import { closeDayScope, fetchClosuresStatus, reopenDayScope, fetchReportsRecords, buildExportXlsxUrl, downloadBinary, type CashClosure } from "@/services/golf";
import { useAuthStore } from "@/stores/auth";
import DatePicker from 'primevue/datepicker';

const auth = useAuthStore();
const canReopen = computed(() => auth.me?.permissions?.can_reopen_closure || auth.isAdmin);

const loading = ref(false);
const error = ref("");
const closures = ref<CashClosure[]>([]);
const historyClosures = ref<CashClosure[]>([]);

const operationalDateObj = ref(new Date());

const today = new Date();
const historyFilters = ref({
  date_from: new Date(today.getFullYear(), today.getMonth() - 1, today.getDate()),
  date_to: today,
});

const currentPage = ref(1);
const itemsPerPage = 10;

const totalPages = computed(() => Math.ceil(historyClosures.value.length / itemsPerPage) || 1);

const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return historyClosures.value.slice(start, start + itemsPerPage);
});

function formatDateForApi(d: any) {
  if (!d) return "";
  const date = new Date(d);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

function formatDateLocal(val: string) {
  return new Date(val + "T00:00:00").toLocaleDateString("es-CL");
}

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(value);
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const data = await fetchClosuresStatus(formatDateForApi(operationalDateObj.value));
    closures.value = data.closures;
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo cargar cierres";
  } finally {
    loading.value = false;
  }
}

async function loadHistory() {
  try {
    const params: Record<string, string> = {
      date_from: formatDateForApi(historyFilters.value.date_from),
      date_to: formatDateForApi(historyFilters.value.date_to),
      record_type: "NONE" as any, // Evita cargar course_entries y range_orders
    };
    const data = await fetchReportsRecords(params);
    historyClosures.value = data.closures;
    currentPage.value = 1;
  } catch (err: any) {
    console.error("Error cargando historial de cierres:", err);
  }
}

async function closeScope(scope: "COURSE" | "RANGE" | "FINAL") {
  const notes = prompt("Observaciones (opcional)") || "";
  let adjustment = 0;
  if (scope === "FINAL") {
    const raw = prompt("Ajuste manual CLP (opcional)", "0");
    adjustment = Number(raw || "0");
  }
  try {
    await closeDayScope({ scope, operational_date: formatDateForApi(operationalDateObj.value), notes, adjustment_clp: adjustment });
    await load();
    await loadHistory();
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo cerrar";
  }
}

async function reopen(scope: "COURSE" | "RANGE" | "FINAL") {
  const reason = prompt("Motivo de reapertura");
  if (!reason) return;
  try {
    await reopenDayScope({ scope, operational_date: formatDateForApi(operationalDateObj.value), reason });
    await load();
    await loadHistory();
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo reabrir";
  }
}

async function downloadExcel(opDate: string) {
  const path = buildExportXlsxUrl({ date_from: opDate, date_to: opDate });
  await downloadBinary(path, `cierre-${opDate}.xlsx`, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
}

onMounted(() => {
  load();
  loadHistory();
});
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
.controls {
  display: flex;
  gap: 8px;
}
.card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 20px;
  box-shadow: var(--minttu-shadow-soft);
}
.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
input,
:deep(.p-datepicker-input) {
  border: 1px solid var(--minttu-border);
  border-radius: var(--minttu-radius-sm);
  background: var(--minttu-white);
  color: var(--minttu-text);
  font-family: inherit;
  transition: all 0.2s ease;
}
input {
  padding: 10px 14px;
}
input:focus,
:deep(.p-datepicker-input:focus) {
  border-color: var(--minttu-primary);
  box-shadow: 0 0 0 3px rgba(27, 67, 50, 0.1);
  outline: none;
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
  padding: 14px 16px;
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
}
</style>
