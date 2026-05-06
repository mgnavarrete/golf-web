<template>
  <div v-if="visible" class="modal-overlay" @click.self="handleCancel">
    <div class="modal-container form-modal">
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button class="modal-close" type="button" :disabled="loading" @click="handleCancel">
          <i class="pi pi-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <p v-if="description" class="modal-description">{{ description }}</p>

        <section v-if="summary" class="summary-panel">
          <div class="summary-grid">
            <div v-for="item in metricRows" :key="item.label" class="summary-item">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>

          <div class="payment-breakdown">
            <h4>Desglose por método de pago</h4>
            <div class="payment-row">
              <span>Efectivo</span>
              <strong>{{ formatClp(summary.total_cash_clp) }}</strong>
            </div>
            <div class="payment-row">
              <span>Tarjeta</span>
              <strong>{{ formatClp(summary.total_card_clp) }}</strong>
            </div>
            <div class="payment-row">
              <span>Transferencia</span>
              <strong>{{ formatClp(summary.total_transfer_clp) }}</strong>
            </div>
            <div class="payment-row">
              <span>Otro</span>
              <strong>{{ formatClp(summary.total_other_clp) }}</strong>
            </div>
          </div>
        </section>

        <div class="form-group">
          <label for="closure-notes">{{ notesLabel }}</label>
          <textarea
            id="closure-notes"
            v-model="notes"
            rows="3"
            :placeholder="notesPlaceholder"
            :disabled="loading"
          ></textarea>
        </div>

        <div v-if="showAdjustment" class="form-group">
          <label for="closure-adjustment">{{ adjustmentLabel }}</label>
          <input
            id="closure-adjustment"
            v-model="adjustmentInput"
            type="number"
            inputmode="numeric"
            :placeholder="adjustmentPlaceholder"
            :disabled="loading"
          />
        </div>

        <p v-if="localError" class="error">{{ localError }}</p>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" type="button" :disabled="loading" @click="handleCancel">
          {{ cancelLabel }}
        </button>
        <button class="btn btn-primary" type="button" :disabled="loading" @click="handleSubmit">
          <i v-if="loading" class="pi pi-spin pi-spinner"></i>
          {{ confirmLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type { ClosureScope, ClosureSummary } from "@/services/golf";

const props = withDefaults(
  defineProps<{
    visible: boolean;
    title: string;
    description?: string;
    confirmLabel?: string;
    cancelLabel?: string;
    loading?: boolean;
    scope?: ClosureScope;
    summary?: ClosureSummary | null;
    notesLabel?: string;
    notesPlaceholder?: string;
    showAdjustment?: boolean;
    adjustmentLabel?: string;
    adjustmentPlaceholder?: string;
    initialNotes?: string;
    initialAdjustment?: number;
  }>(),
  {
    description: "",
    confirmLabel: "Confirmar",
    cancelLabel: "Cancelar",
    loading: false,
    scope: "FINAL",
    summary: null,
    notesLabel: "Observaciones (opcional)",
    notesPlaceholder: "Escribe una observación",
    showAdjustment: false,
    adjustmentLabel: "Ajuste manual CLP (opcional)",
    adjustmentPlaceholder: "0",
    initialNotes: "",
    initialAdjustment: 0,
  }
);

const emit = defineEmits<{
  (e: "cancel"): void;
  (e: "submit", payload: { notes: string; adjustment_clp: number }): void;
}>();

const notes = ref("");
const adjustmentInput = ref("0");
const localError = ref("");

const metricRows = computed(() => {
  if (!props.summary) return [];
  const summary = props.summary;

  if (props.scope === "COURSE") {
    return [
      { label: "Total pagado", value: formatClp(summary.total_course_clp) },
      { label: "Personas", value: formatNumber(summary.total_people) },
      { label: "Registros", value: formatNumber(summary.total_course_records) },
      { label: "Promedio por persona", value: formatClp(average(summary.total_course_clp, summary.total_people)) },
      { label: "Promedio por registro", value: formatClp(average(summary.total_course_clp, summary.total_course_records)) },
    ];
  }

  if (props.scope === "RANGE") {
    return [
      { label: "Total pagado", value: formatClp(summary.total_range_clp) },
      { label: "Canastos", value: formatNumber(summary.total_baskets) },
      { label: "Pedidos", value: formatNumber(summary.total_range_orders) },
      { label: "Promedio por canasto", value: formatClp(average(summary.total_range_clp, summary.total_baskets)) },
      { label: "Promedio por pedido", value: formatClp(average(summary.total_range_clp, summary.total_range_orders)) },
    ];
  }

  return [
    { label: "Total general", value: formatClp(summary.total_general_clp) },
    { label: "Total cancha", value: formatClp(summary.total_course_clp) },
    { label: "Total range", value: formatClp(summary.total_range_clp) },
    { label: "Personas", value: formatNumber(summary.total_people) },
    { label: "Canastos", value: formatNumber(summary.total_baskets) },
    { label: "Registros cancha", value: formatNumber(summary.total_course_records) },
    { label: "Pedidos range", value: formatNumber(summary.total_range_orders) },
  ];
});

function average(total: number, count: number) {
  if (!count) return 0;
  return total / count;
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("es-CL", { maximumFractionDigits: 0 }).format(value || 0);
}

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function resetState() {
  notes.value = props.initialNotes;
  adjustmentInput.value = String(props.initialAdjustment);
  localError.value = "";
}

watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      resetState();
    }
  }
);

function handleCancel() {
  emit("cancel");
}

function handleSubmit() {
  localError.value = "";
  let adjustment = 0;

  if (props.showAdjustment) {
    adjustment = Number(adjustmentInput.value || "0");
    if (!Number.isFinite(adjustment)) {
      localError.value = "El ajuste manual debe ser un número válido";
      return;
    }
  }

  emit("submit", { notes: notes.value.trim(), adjustment_clp: adjustment });
}
</script>

<style scoped>
.form-modal {
  max-width: 560px;
}

.modal-description {
  margin: 0;
  color: var(--minttu-gray);
  font-size: 14px;
}

.summary-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  border: 1px solid var(--minttu-border);
  border-radius: var(--minttu-radius-md);
  background: var(--minttu-bg);
  padding: 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.summary-item span,
.payment-row span {
  color: var(--minttu-gray);
  font-size: 12px;
}

.summary-item strong,
.payment-row strong {
  color: var(--minttu-primary);
  font-size: 14px;
}

.payment-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid var(--minttu-border);
  padding-top: 12px;
}

.payment-breakdown h4 {
  margin: 0;
  color: var(--minttu-primary);
  font-size: 13px;
}

.payment-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--minttu-gray);
}

.form-group textarea,
.form-group input {
  border: 1px solid var(--minttu-border);
  border-radius: var(--minttu-radius-sm);
  background: var(--minttu-white);
  color: var(--minttu-text);
  font-family: inherit;
  transition: all 0.2s ease;
  width: 100%;
  padding: 10px 14px;
}

.form-group textarea:focus,
.form-group input:focus {
  border-color: var(--minttu-primary);
  box-shadow: 0 0 0 3px rgba(27, 67, 50, 0.1);
  outline: none;
}

.error {
  margin: 0;
  color: #c0392b;
}

@media (max-width: 520px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
