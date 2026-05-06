<template>
  <div class="page">
    <div class="header">
      <h1>Cierre de Caja Diario</h1>
    </div>

    <section class="card actions-grid">
      <button class="btn btn-primary" :disabled="loading || !canCloseCourse" @click="openCloseModal('COURSE')">
        Cerrar Cancha
      </button>
      <button class="btn btn-primary" :disabled="loading || !canCloseRange" @click="openCloseModal('RANGE')">
        Cerrar Driving Range
      </button>
      <button class="btn btn-primary" :disabled="loading || !canCloseFinal" @click="openCloseModal('FINAL')">
        Cierre Final
      </button>
    </section>

    <section class="card">
      <h3>Estado del Día Seleccionado</h3>
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Fecha Operativa</th>
              <th>Área</th>
              <th>Estado</th>
              <th>Total General</th>
              <th>Usuario</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="closure in closures" :key="closure.id">
              <td>{{ closure.operational_date }}</td>
              <td>{{ scopeLabel(closure.scope) }}</td>
              <td><span class="badge closed">Cerrado</span></td>
              <td class="font-medium">{{ formatClp(closure.total_general_clp) }}</td>
              <td>{{ closure.closed_by_name }}</td>
              <td class="actions-cell">
                <button class="action" @click="openDetail(closure)">Ver</button>
                <button v-if="canReopen" class="action danger" @click="askReopen(closure)">Reabrir</button>
                <button v-if="closure.scope === 'FINAL'" class="action" @click="downloadExcel(closure.operational_date)">
                  <i class="pi pi-file-excel"></i> Excel
                </button>
              </td>
            </tr>
            <tr v-if="closures.length === 0">
              <td colspan="6" class="empty">No hay cierres para la fecha</td>
            </tr>
          </tbody>
        </table>
      </div>
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
      <div class="table-responsive history-table">
        <table>
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
              <td>{{ scopeLabel(closure.scope) }}</td>
              <td>Cerrado</td>
              <td>{{ formatClp(closure.total_general_clp) }}</td>
              <td>{{ closure.closed_by_name }}</td>
              <td class="actions-cell">
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
      </div>

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

    <ClosureFormModal
      :visible="closeModalVisible"
      :title="closeModalTitle"
      :description="closeModalDescription"
      :scope="closeModalScope"
      :summary="closeModalSummary"
      :show-adjustment="closeModalScope === 'FINAL'"
      confirm-label="Generar Cierre"
      :loading="submittingClose"
      @cancel="closeCloseModal"
      @submit="submitClose"
    />

    <ConfirmActionModal
      :visible="reopenTarget !== null"
      title="Reabrir Cierre"
      message="Esta acción eliminará el cierre actual y, si corresponde, también el cierre final del día."
      confirm-label="Reabrir"
      confirm-class="btn-danger"
      :loading="submittingReopen"
      @cancel="cancelReopen"
      @confirm="confirmReopen"
    />

    <div v-if="detailClosure" class="modal-overlay" @click.self="detailClosure = null">
      <div class="modal-container detail-modal">
        <div class="modal-header">
          <h3>Detalle de Cierre</h3>
          <button class="modal-close" type="button" @click="detailClosure = null">
            <i class="pi pi-times"></i>
          </button>
        </div>
        <div class="modal-body detail-grid">
          <div><strong>Fecha:</strong> {{ detailClosure.operational_date }}</div>
          <div><strong>Área:</strong> {{ scopeLabel(detailClosure.scope) }}</div>
          <div v-if="detailClosure.scope !== 'RANGE'"><strong>Total Cancha:</strong> {{ formatClp(detailClosure.total_course_clp) }}</div>
          <div v-if="detailClosure.scope !== 'COURSE'"><strong>Total Range:</strong> {{ formatClp(detailClosure.total_range_clp) }}</div>
          <div><strong>Total General:</strong> {{ formatClp(detailClosure.total_general_clp) }}</div>
          <div><strong>Efectivo:</strong> {{ formatClp(detailClosure.total_cash_clp) }}</div>
          <div><strong>Tarjeta:</strong> {{ formatClp(detailClosure.total_card_clp) }}</div>
          <div><strong>Transferencia:</strong> {{ formatClp(detailClosure.total_transfer_clp) }}</div>
          <div><strong>Otro:</strong> {{ formatClp(detailClosure.total_other_clp) }}</div>
          <div v-if="detailClosure.scope !== 'RANGE'"><strong>Personas:</strong> {{ formatNumber(detailClosure.total_people) }}</div>
          <div v-if="detailClosure.scope !== 'RANGE'"><strong>Registros cancha:</strong> {{ formatNumber(detailClosure.total_course_records) }}</div>
          <div v-if="detailClosure.scope !== 'RANGE'">
            <strong>Promedio por persona:</strong> {{ formatClp(average(detailClosure.total_course_clp, detailClosure.total_people)) }}
          </div>
          <div v-if="detailClosure.scope !== 'COURSE'"><strong>Canastos:</strong> {{ formatNumber(detailClosure.total_baskets) }}</div>
          <div v-if="detailClosure.scope !== 'COURSE'"><strong>Pedidos range:</strong> {{ formatNumber(detailClosure.total_range_orders) }}</div>
          <div v-if="detailClosure.scope !== 'COURSE'">
            <strong>Promedio por canasto:</strong> {{ formatClp(average(detailClosure.total_range_clp, detailClosure.total_baskets)) }}
          </div>
          <div v-if="detailClosure.scope === 'FINAL' && detailClosure.adjustment_clp">
            <strong>Ajuste manual:</strong> {{ formatClp(detailClosure.adjustment_clp) }}
          </div>
          <div><strong>Observaciones:</strong> {{ detailClosure.notes || "-" }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  closeDayScope,
  fetchClosuresStatus,
  reopenDayScope,
  fetchReportsRecords,
  buildExportXlsxUrl,
  downloadBinary,
  type CashClosure,
  type ClosureScope,
  type ClosureSummary,
} from "@/services/golf";
import { useAuthStore } from "@/stores/auth";
import DatePicker from "primevue/datepicker";
import ConfirmActionModal from "@/components/modals/ConfirmActionModal.vue";
import ClosureFormModal from "@/components/modals/ClosureFormModal.vue";

const auth = useAuthStore();
const canReopen = computed(() => auth.me?.permissions?.can_reopen_closure || auth.isAdmin);

const loading = ref(false);
const error = ref("");
const closures = ref<CashClosure[]>([]);
const historyClosures = ref<CashClosure[]>([]);
const summaries = ref<Record<ClosureScope, ClosureSummary>>(defaultClosureSummaries());

const canCloseCourse = ref(true);
const canCloseRange = ref(true);
const canCloseFinal = ref(true);

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

function formatDateForApi(d: Date | null) {
  if (!d) return "";
  const date = new Date(d);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function formatDateLocal(val: string) {
  return new Date(`${val}T00:00:00`).toLocaleDateString("es-CL");
}

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("es-CL", { maximumFractionDigits: 0 }).format(value || 0);
}

function average(total: number, count: number) {
  if (!count) return 0;
  return total / count;
}

function scopeLabel(scope: ClosureScope) {
  if (scope === "COURSE") return "Cancha";
  if (scope === "RANGE") return "Driving Range";
  return "Final";
}

function emptyClosureSummary(): ClosureSummary {
  return {
    total_course_clp: 0,
    total_range_clp: 0,
    total_general_clp: 0,
    total_cash_clp: 0,
    total_card_clp: 0,
    total_transfer_clp: 0,
    total_other_clp: 0,
    total_people: 0,
    total_course_records: 0,
    total_range_orders: 0,
    total_baskets: 0,
  };
}

function defaultClosureSummaries(): Record<ClosureScope, ClosureSummary> {
  return {
    COURSE: emptyClosureSummary(),
    RANGE: emptyClosureSummary(),
    FINAL: emptyClosureSummary(),
  };
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const data = await fetchClosuresStatus(formatDateForApi(operationalDateObj.value));
    closures.value = data.closures;
    canCloseCourse.value = data.can_close_course;
    canCloseRange.value = data.can_close_range;
    canCloseFinal.value = data.can_close_final;
    summaries.value = data.summaries || defaultClosureSummaries();
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
      record_type: "NONE",
    };
    const data = await fetchReportsRecords(params);
    historyClosures.value = data.closures.filter((closure) => closure.scope === "FINAL");
    currentPage.value = 1;
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo cargar historial";
  }
}

const closeModalVisible = ref(false);
const closeModalScope = ref<ClosureScope>("COURSE");
const submittingClose = ref(false);

const closeModalSummary = computed(() => summaries.value[closeModalScope.value]);

const closeModalTitle = computed(() => {
  if (closeModalScope.value === "COURSE") return "Cerrar Cancha";
  if (closeModalScope.value === "RANGE") return "Cerrar Driving Range";
  return "Generar Cierre Final";
});

const closeModalDescription = computed(() => {
  const date = formatDateForApi(operationalDateObj.value);
  if (closeModalScope.value === "FINAL") {
    return `Generarás el cierre final del día ${date}. Puedes agregar observaciones y ajuste manual.`;
  }
  return `Generarás el cierre de ${scopeLabel(closeModalScope.value).toLowerCase()} para el día ${date}.`;
});

function openCloseModal(scope: ClosureScope) {
  closeModalScope.value = scope;
  closeModalVisible.value = true;
}

function closeCloseModal() {
  if (submittingClose.value) return;
  closeModalVisible.value = false;
}

async function submitClose(payload: { notes: string; adjustment_clp: number }) {
  submittingClose.value = true;
  error.value = "";
  try {
    await closeDayScope({
      scope: closeModalScope.value,
      operational_date: formatDateForApi(operationalDateObj.value),
      notes: payload.notes,
      adjustment_clp: closeModalScope.value === "FINAL" ? payload.adjustment_clp : 0,
    });
    closeModalVisible.value = false;
    await Promise.all([load(), loadHistory()]);
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo cerrar";
  } finally {
    submittingClose.value = false;
  }
}

const reopenTarget = ref<CashClosure | null>(null);
const submittingReopen = ref(false);

function askReopen(closure: CashClosure) {
  reopenTarget.value = closure;
}

function cancelReopen() {
  if (submittingReopen.value) return;
  reopenTarget.value = null;
}

async function confirmReopen() {
  if (!reopenTarget.value) return;

  submittingReopen.value = true;
  error.value = "";
  try {
    await reopenDayScope({
      scope: reopenTarget.value.scope,
      operational_date: reopenTarget.value.operational_date,
    });
    reopenTarget.value = null;
    await Promise.all([load(), loadHistory()]);
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo reabrir";
  } finally {
    submittingReopen.value = false;
  }
}

const detailClosure = ref<CashClosure | null>(null);

function openDetail(closure: CashClosure) {
  detailClosure.value = closure;
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
input,
:deep(.p-datepicker-input) {
  border: 1px solid var(--minttu-border);
  border-radius: var(--minttu-radius-sm);
  background: var(--minttu-white);
  color: var(--minttu-text);
  font-family: inherit;
  transition: all 0.2s ease;
  width: 100%;
}
:deep(.p-datepicker) {
  width: 100%;
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
  margin-right: 6px;
}
.action:hover {
  background: var(--minttu-primary);
  color: var(--minttu-white);
}
.action.danger {
  background: #fef2f2;
  color: #dc2626;
}
.action.danger:hover {
  background: #dc2626;
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
.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
}
.badge.closed {
  background: #ecfdf3;
  color: #166534;
}
.history-table {
  margin-top: 16px;
}
.detail-modal {
  max-width: 640px;
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  font-size: 14px;
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
  .controls {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }
  .controls > * {
    width: 100%;
  }
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
