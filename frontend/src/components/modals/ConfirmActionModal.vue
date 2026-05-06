<template>
  <div v-if="visible" class="modal-overlay" @click.self="emitCancel">
    <div class="modal-container confirm-modal">
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button class="modal-close" type="button" :disabled="loading" @click="emitCancel">
          <i class="pi pi-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <p class="confirm-message">{{ message }}</p>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" type="button" :disabled="loading" @click="emitCancel">
          {{ cancelLabel }}
        </button>
        <button class="btn" :class="confirmClass" type="button" :disabled="loading" @click="emitConfirm">
          <i v-if="loading" class="pi pi-spin pi-spinner"></i>
          {{ confirmLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    visible: boolean;
    title: string;
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    loading?: boolean;
    confirmClass?: string;
  }>(),
  {
    confirmLabel: "Confirmar",
    cancelLabel: "Cancelar",
    loading: false,
    confirmClass: "btn-danger",
  }
);

const emit = defineEmits<{
  (e: "confirm"): void;
  (e: "cancel"): void;
}>();

function emitConfirm() {
  emit("confirm");
}

function emitCancel() {
  emit("cancel");
}
</script>

<style scoped>
.confirm-modal {
  max-width: 460px;
}

.confirm-message {
  margin: 0;
  color: var(--minttu-text);
  font-size: 15px;
  line-height: 1.5;
}
</style>
