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
import { ref, watch } from "vue";

const props = withDefaults(
  defineProps<{
    visible: boolean;
    title: string;
    description?: string;
    confirmLabel?: string;
    cancelLabel?: string;
    loading?: boolean;
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
</style>
