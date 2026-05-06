<template>
  <div class="page">
    <div class="header">
      <button class="btn btn-secondary" @click="$router.push('/course-entries')">
        <i class="pi pi-arrow-left"></i> Volver
      </button>
      <h1>Nueva Entrada a Cancha</h1>
    </div>

    <section class="card form-container">
      <div class="form-group">
        <label>Nombre del Cliente</label>
        <input v-model="form.customer_name" placeholder="Ej. Juan Pérez" />
      </div>

      <div class="form-group">
        <label>Cantidad de Personas</label>
        <input v-model.number="form.people_count" type="number" min="1" placeholder="Personas" />
      </div>

      <div class="form-group">
        <label>Tipo de Tarifa</label>
        <Select v-model="priceOption" :options="priceOptions" optionLabel="label" optionValue="value" />
      </div>

      <div class="form-group" v-if="priceOption === 'CUSTOM'">
        <label>Valor Unitario Personalizado (CLP)</label>
        <input v-model.number="customAmount" type="number" min="0" placeholder="Ingrese monto por persona" />
      </div>

      <div class="form-group">
        <label>Total a Cobrar</label>
        <div class="total-display">{{ formatClp(calculatedAmount) }}</div>
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
          Guardar Entrada
        </button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { createCourseEntry, getBusinessSettings } from '@/services/golf';
import Select from 'primevue/select';

const paymentOptions = [
  { label: 'Efectivo', value: 'CASH' },
  { label: 'Tarjeta', value: 'CARD' },
  { label: 'Transferencia', value: 'TRANSFER' },
  { label: 'Otro', value: 'OTHER' }
];

const priceOptions = ref([
  { label: 'Día de Semana', value: 'SEMANA' },
  { label: 'Fin de semana / Festivo', value: 'FINDE' },
  { label: 'Personalizado', value: 'CUSTOM' }
]);

const basePrices = ref({
  weekday: 20000,
  weekend: 25000,
});

const router = useRouter();

const today = new Date().getDay();
const isWeekend = today === 0 || today === 6;

const priceOption = ref<'SEMANA' | 'FINDE' | 'CUSTOM'>(isWeekend ? 'FINDE' : 'SEMANA');
const customAmount = ref<number>(0);

const form = ref({
  customer_name: "",
  people_count: 1,
  payment_method: "CASH" as "CASH" | "CARD" | "TRANSFER" | "OTHER",
  notes: "",
});

const calculatedAmount = computed(() => {
  let baseAmount = 0;
  if (priceOption.value === 'SEMANA') baseAmount = basePrices.value.weekday;
  else if (priceOption.value === 'FINDE') baseAmount = basePrices.value.weekend;
  else baseAmount = customAmount.value || 0;
  
  return baseAmount * (form.value.people_count || 1);
});

const saving = ref(false);
const error = ref("");

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(value);
}

onMounted(async () => {
  try {
    const settings = await getBusinessSettings();
    basePrices.value.weekday = settings.course_price_weekday_clp;
    basePrices.value.weekend = settings.course_price_weekend_clp;
    priceOptions.value[0].label = `Día de Semana (${formatClp(settings.course_price_weekday_clp)})`;
    priceOptions.value[1].label = `Fin de semana / Festivo (${formatClp(settings.course_price_weekend_clp)})`;
  } catch (err) {
    console.error("Error al cargar precios:", err);
  }
});

async function submit() {
  if (!form.value.customer_name.trim()) {
    error.value = "El nombre del cliente es obligatorio";
    return;
  }
  if (calculatedAmount.value < 0 && priceOption.value === 'CUSTOM') {
    error.value = "Ingrese un monto válido";
    return;
  }

  saving.value = true;
  error.value = "";

  try {
    await createCourseEntry({
      ...form.value,
      amount_clp: calculatedAmount.value
    } as any);
    router.push('/course-entries');
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
