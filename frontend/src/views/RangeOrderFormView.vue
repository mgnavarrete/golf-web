<template>
  <div class="page">
    <div class="header">
      <button class="btn btn-secondary" @click="$router.push('/range-orders')">
        <i class="pi pi-arrow-left"></i> Volver
      </button>
      <h1>Nuevo Pedido Driving Range</h1>
    </div>

    <section class="card form-container">
      <div class="form-group">
        <label>Nombre del Cliente</label>
        <input v-model="form.customer_name" placeholder="Ej. Juan Pérez" />
      </div>

      <div class="form-group">
        <label>Cantidad de Canastos</label>
        <input v-model.number="form.baskets_count" type="number" min="1" placeholder="Canastos" />
      </div>

      <div class="form-group">
        <label>Tipo de Tarifa</label>
        <Select v-model="priceOption" :options="priceOptions" optionLabel="label" optionValue="value" />
      </div>

      <div class="form-group" v-if="priceOption === 'CUSTOM'">
        <label>Valor Unitario Personalizado (CLP)</label>
        <input v-model.number="form.unit_price_clp" type="number" min="0" placeholder="Valor unitario" />
      </div>

      <div class="form-group">
        <label>Total a Cobrar</label>
        <div class="total-display">{{ formatClp(form.baskets_count * form.unit_price_clp) }}</div>
      </div>

      <div class="form-group">
        <label>Método de Pago</label>
        <Select v-model="form.payment_method" :options="paymentOptions" optionLabel="label" optionValue="value" />
      </div>

      <div class="form-group">
        <label>Notas</label>
        <input v-model="form.notes" placeholder="Opcional" />
      </div>

      <div class="form-actions">
        <button class="btn btn-primary" @click="submit" :disabled="saving">
          <i :class="saving ? 'pi pi-spin pi-spinner' : 'pi pi-save'"></i>
          Guardar Pedido
        </button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { createRangeOrder, getBusinessSettings } from '@/services/golf';
import Select from 'primevue/select';

const paymentOptions = [
  { label: 'Efectivo', value: 'CASH' },
  { label: 'Tarjeta', value: 'CARD' },
  { label: 'Transferencia', value: 'TRANSFER' },
  { label: 'Otro', value: 'OTHER' }
];

const router = useRouter();

const form = ref({
  customer_name: "",
  baskets_count: 1,
  unit_price_clp: 5000,
  payment_method: "CASH" as "CASH" | "CARD" | "TRANSFER" | "OTHER",
  notes: "",
});

const defaultPrice = ref(5000);
const priceOption = ref<'NORMAL' | 'CUSTOM'>('NORMAL');

const priceOptions = computed(() => [
  { label: `Normal (${formatClp(defaultPrice.value)})`, value: 'NORMAL' },
  { label: 'Personalizado', value: 'CUSTOM' }
]);

const saving = ref(false);
const error = ref("");

watch(priceOption, (val) => {
  if (val === 'NORMAL') {
    form.value.unit_price_clp = defaultPrice.value;
  }
});

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(value);
}

async function loadDefaultPrice() {
  try {
    const settings = await getBusinessSettings();
    defaultPrice.value = settings.default_range_unit_price_clp;
    if (priceOption.value === 'NORMAL') {
      form.value.unit_price_clp = defaultPrice.value;
    }
  } catch {
    // ignore
  }
}

async function submit() {
  if (!form.value.customer_name.trim()) {
    error.value = "El nombre del cliente es obligatorio";
    return;
  }

  saving.value = true;
  error.value = "";

  try {
    await createRangeOrder(form.value as any);
    router.push('/range-orders');
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo guardar";
    saving.value = false;
  }
}

onMounted(() => {
  loadDefaultPrice();
});
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
.form-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-weight: 500;
  color: var(--minttu-text);
  font-size: 14px;
}
input,
:deep(.p-select) {
  border: 1px solid var(--minttu-border);
  border-radius: var(--minttu-radius-sm);
  background: var(--minttu-white);
  color: var(--minttu-text);
  font-family: inherit;
  transition: all 0.2s ease;
  width: 100%;
}
input {
  padding: 12px 14px;
}
input:focus,
:deep(.p-select:not(.p-disabled).p-focus) {
  border-color: var(--minttu-primary);
  box-shadow: 0 0 0 3px rgba(27, 67, 50, 0.1);
  outline: none;
}
.total-display {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--minttu-primary);
  background: var(--minttu-bg);
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px dashed var(--minttu-primary);
}
.form-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.error {
  color: #c0392b;
  margin-top: 8px;
  font-size: 14px;
}
</style>
