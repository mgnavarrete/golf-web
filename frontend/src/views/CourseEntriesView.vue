<template>
  <div class="page">
    <div class="header">
      <h1>Entradas a Cancha</h1>
      <button class="btn btn-accent primary-create-button" @click="$router.push('/course-entries/new')">
        <i class="pi pi-plus"></i>
        Nuevo Registro
      </button>
    </div>

    <section class="summary-grid">
      <div class="summary-card">
        <span>Personas</span>
        <strong>{{ formatNumber(daySummary.people) }}</strong>
      </div>
      <div class="summary-card">
        <span>Total Día</span>
        <strong>{{ formatClp(daySummary.total) }}</strong>
      </div>
      <div class="summary-card">
        <span>Efectivo</span>
        <strong>{{ formatClp(daySummary.cash) }}</strong>
      </div>
      <div class="summary-card">
        <span>Tarjeta</span>
        <strong>{{ formatClp(daySummary.card) }}</strong>
      </div>
      <div class="summary-card">
        <span>Transferencia</span>
        <strong>{{ formatClp(daySummary.transfer) }}</strong>
      </div>
    </section>

    <section class="card">
      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Nombre</th>
              <th>Personas</th>
              <th>Monto</th>
              <th>Pago</th>
              <th>Usuario</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedEntries" :key="item.id">
              <td>{{ formatDate(item.created_at) }}</td>
              <td>{{ item.customer_name }}</td>
              <td>{{ item.people_count }}</td>
              <td>{{ formatClp(item.amount_clp) }}</td>
              <td>{{ paymentLabel(item.payment_method) }}</td>
              <td>{{ item.created_by_name }}</td>
              <td class="actions-cell">
                <button v-if="canEdit" class="action" @click="quickEdit(item)">Editar</button>
                <button v-if="canDelete" class="action danger" @click="askRemove(item.id)">Eliminar</button>
              </td>
            </tr>
            <tr v-if="entries.length === 0">
              <td colspan="7" class="empty">Sin registros</td>
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

    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-container record-modal">
        <div class="modal-header">
          <h3>Editar Registro de Cancha</h3>
          <button class="modal-close" :disabled="editing" @click="closeEditModal"><i class="pi pi-times"></i></button>
        </div>
        <div class="modal-body">
          <CourseEntryForm
            :initial-entry="editForm"
            :saving="editing"
            :error="editError"
            submit-label="Guardar Cambios"
            show-cancel
            @cancel="closeEditModal"
            @submit="saveEditModal"
          />
        </div>
      </div>
    </div>

    <ConfirmActionModal
      :visible="deleteTargetId !== null"
      title="Eliminar Registro"
      message="¿Seguro que deseas eliminar este registro de cancha? Esta acción no se puede deshacer."
      confirm-label="Eliminar"
      confirm-class="btn-danger"
      :loading="deleting"
      @cancel="cancelRemove"
      @confirm="confirmRemove"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  deleteCourseEntry,
  listCourseEntries,
  updateCourseEntry,
  type CourseEntry,
  type CourseEntryPayload,
} from "@/services/golf";
import { useAuthStore } from "@/stores/auth";
import CourseEntryForm from "@/components/forms/CourseEntryForm.vue";
import ConfirmActionModal from "@/components/modals/ConfirmActionModal.vue";

const auth = useAuthStore();

const error = ref("");
const entries = ref<CourseEntry[]>([]);

const currentPage = ref(1);
const itemsPerPage = 10;

const totalPages = computed(() => Math.ceil(entries.value.length / itemsPerPage) || 1);

const paginatedEntries = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return entries.value.slice(start, start + itemsPerPage);
});

const daySummary = computed(() => {
  return entries.value.reduce(
    (summary, item) => {
      summary.people += item.people_count || 0;
      summary.total += item.amount_clp || 0;
      if (item.payment_method === "CASH") summary.cash += item.amount_clp || 0;
      if (item.payment_method === "CARD") summary.card += item.amount_clp || 0;
      if (item.payment_method === "TRANSFER") summary.transfer += item.amount_clp || 0;
      return summary;
    },
    { people: 0, total: 0, cash: 0, card: 0, transfer: 0 }
  );
});

const canEdit = computed(() => auth.me?.permissions?.can_edit_course_entries || auth.isAdmin);
const canDelete = computed(() => auth.me?.permissions?.can_delete_course_entries || auth.isAdmin);

function paymentLabel(method: string) {
  return { CASH: "Efectivo", CARD: "Tarjeta", TRANSFER: "Transferencia", OTHER: "Otro" }[method] || method;
}

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(value);
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("es-CL", { maximumFractionDigits: 0 }).format(value || 0);
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("es-CL", { hour12: false });
}

function formatDateForApi(d: Date | null) {
  if (!d) return "";
  const date = new Date(d);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

async function load() {
  error.value = "";
  try {
    const today = new Date();
    const params: Record<string, string> = {};
    params.date_from = formatDateForApi(today);
    params.date_to = formatDateForApi(today);
    entries.value = await listCourseEntries(params);
    currentPage.value = 1;
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo cargar la lista";
  }
}

const showEditModal = ref(false);
const editForm = ref<Partial<CourseEntryPayload> | null>(null);
const editId = ref<number | null>(null);
const editing = ref(false);
const editError = ref("");

function quickEdit(item: CourseEntry) {
  editId.value = item.id;
  editError.value = "";
  editForm.value = {
    customer_name: item.customer_name,
    people_count: item.people_count,
    amount_clp: item.amount_clp,
    payment_method: item.payment_method,
    notes: item.notes,
  };
  showEditModal.value = true;
}

function closeEditModal() {
  if (editing.value) return;
  showEditModal.value = false;
  editId.value = null;
  editForm.value = null;
  editError.value = "";
}

async function saveEditModal(payload: CourseEntryPayload) {
  if (!editId.value) return;
  editing.value = true;
  editError.value = "";
  try {
    await updateCourseEntry(editId.value, payload);
    await load();
    editing.value = false;
    closeEditModal();
  } catch (err: any) {
    editError.value = err.response?.data?.detail || "No se pudo editar el registro";
  } finally {
    editing.value = false;
  }
}

const deleteTargetId = ref<number | null>(null);
const deleting = ref(false);

function askRemove(id: number) {
  deleteTargetId.value = id;
}

function cancelRemove() {
  if (deleting.value) return;
  deleteTargetId.value = null;
}

async function confirmRemove() {
  if (!deleteTargetId.value) return;

  deleting.value = true;
  error.value = "";
  try {
    await deleteCourseEntry(deleteTargetId.value);
    deleteTargetId.value = null;
    await load();
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo eliminar";
  } finally {
    deleting.value = false;
  }
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
.primary-create-button {
  min-height: 52px;
  padding: 0 24px;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 10px 24px rgba(27, 67, 50, 0.18);
}
.primary-create-button i {
  font-size: 18px;
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}
.summary-card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 16px;
  box-shadow: var(--minttu-shadow-soft);
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}
.summary-card span {
  color: var(--minttu-gray);
  font-size: 12px;
}
.summary-card strong {
  color: var(--minttu-primary);
  font-size: 18px;
}
.card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 20px;
  box-shadow: var(--minttu-shadow-soft);
}
.form-grid,
.filters {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  align-items: center;
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
tbody tr {
  transition: background-color 0.2s ease;
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
  margin-right: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
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
.record-modal {
  max-width: 600px;
}

@media (max-width: 1024px) {
  .form-grid,
  .filters,
  .summary-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header {
    align-items: stretch;
    flex-direction: column;
    gap: 12px;
  }
  .primary-create-button {
    min-height: 44px;
    width: 100%;
    padding: 0 16px;
    font-size: 14px;
  }
}
</style>
