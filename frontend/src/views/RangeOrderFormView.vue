<template>
  <div class="page">
    <div class="header">
      <button class="btn btn-secondary" @click="$router.push('/range-orders')">
        <i class="pi pi-arrow-left"></i> Volver
      </button>
      <h1>Nuevo Pedido Driving Range</h1>
    </div>

    <section class="card">
      <RangeOrderForm :saving="saving" :error="error" submit-label="Guardar Pedido" @submit="submit" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import RangeOrderForm from "@/components/forms/RangeOrderForm.vue";
import { createRangeOrder, type RangeOrderPayload } from "@/services/golf";

const router = useRouter();

const saving = ref(false);
const error = ref("");

async function submit(payload: RangeOrderPayload) {
  saving.value = true;
  error.value = "";

  try {
    await createRangeOrder(payload);
    router.push("/range-orders");
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo guardar";
    saving.value = false;
  }
}
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 600px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--minttu-text);
}

.card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 32px;
  box-shadow: var(--minttu-shadow-soft);
}
</style>
