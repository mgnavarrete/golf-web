<template>
  <form class="golf-record-form" @submit.prevent="handleSubmit">
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

    <div v-if="priceOption === 'CUSTOM'" class="form-group">
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
      <button v-if="showCancel" class="btn btn-secondary" type="button" :disabled="saving" @click="$emit('cancel')">
        {{ cancelLabel }}
      </button>
      <button class="btn btn-primary" type="submit" :disabled="saving">
        <i :class="saving ? 'pi pi-spin pi-spinner' : 'pi pi-save'"></i>
        {{ submitLabel }}
      </button>
    </div>

    <p v-if="visibleError" class="error">{{ visibleError }}</p>
  </form>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import Select from "primevue/select";
import {
  getBusinessSettings,
  type CourseEntryPayload,
  type PaymentMethod,
} from "@/services/golf";

import "@/styles/components/record-form.css";

type CoursePriceOption = "SEMANA" | "FINDE" | "CUSTOM";

const props = withDefaults(
  defineProps<{
    initialEntry?: Partial<CourseEntryPayload> | null;
    saving?: boolean;
    submitLabel?: string;
    showCancel?: boolean;
    cancelLabel?: string;
    error?: string;
  }>(),
  {
    initialEntry: null,
    saving: false,
    submitLabel: "Guardar Entrada",
    showCancel: false,
    cancelLabel: "Cancelar",
    error: "",
  },
);

const emit = defineEmits<{
  (e: "submit", payload: CourseEntryPayload): void;
  (e: "cancel"): void;
}>();

const paymentOptions = [
  { label: "Efectivo", value: "CASH" },
  { label: "Tarjeta", value: "CARD" },
  { label: "Transferencia", value: "TRANSFER" },
  { label: "Otro", value: "OTHER" },
];

const basePrices = ref({
  weekday: 20000,
  weekend: 25000,
});

const form = ref({
  customer_name: "",
  people_count: 1,
  payment_method: "CASH" as PaymentMethod,
  notes: "",
});

const priceOption = ref<CoursePriceOption>(defaultPriceOption());
const customAmount = ref(0);
const localError = ref("");

const priceOptions = computed(() => [
  { label: `Día de Semana (${formatClp(basePrices.value.weekday)})`, value: "SEMANA" },
  { label: `Fin de semana / Festivo (${formatClp(basePrices.value.weekend)})`, value: "FINDE" },
  { label: "Personalizado", value: "CUSTOM" },
]);

const calculatedAmount = computed(() => {
  let baseAmount = 0;
  if (priceOption.value === "SEMANA") baseAmount = basePrices.value.weekday;
  else if (priceOption.value === "FINDE") baseAmount = basePrices.value.weekend;
  else baseAmount = Number(customAmount.value) || 0;

  return baseAmount * normaliseCount(form.value.people_count);
});

const visibleError = computed(() => localError.value || props.error);

function defaultPriceOption(): CoursePriceOption {
  const day = new Date().getDay();
  return day === 0 || day === 6 ? "FINDE" : "SEMANA";
}

function normaliseCount(value: unknown) {
  const count = Number(value);
  if (!Number.isFinite(count) || count <= 0) return 1;
  return count;
}

function inferPriceOption(amount: number, peopleCount: number): CoursePriceOption {
  if (amount === basePrices.value.weekday * peopleCount) return "SEMANA";
  if (amount === basePrices.value.weekend * peopleCount) return "FINDE";
  return "CUSTOM";
}

function applyInitialEntry() {
  localError.value = "";
  const initial = props.initialEntry;

  if (!initial) {
    form.value = {
      customer_name: "",
      people_count: 1,
      payment_method: "CASH",
      notes: "",
    };
    priceOption.value = defaultPriceOption();
    customAmount.value = 0;
    return;
  }

  const peopleCount = normaliseCount(initial.people_count);
  const amount = Number(initial.amount_clp) || 0;
  const inferredOption = inferPriceOption(amount, peopleCount);

  form.value = {
    customer_name: initial.customer_name || "",
    people_count: peopleCount,
    payment_method: initial.payment_method || "CASH",
    notes: initial.notes || "",
  };
  priceOption.value = inferredOption;
  customAmount.value = inferredOption === "CUSTOM" ? amount / peopleCount : 0;
}

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    maximumFractionDigits: 0,
  }).format(value);
}

async function loadBusinessSettings() {
  try {
    const settings = await getBusinessSettings();
    basePrices.value.weekday = settings.course_price_weekday_clp;
    basePrices.value.weekend = settings.course_price_weekend_clp;
    if (props.initialEntry) applyInitialEntry();
  } catch {
    // Keep fallback prices if settings cannot be loaded.
  }
}

function handleSubmit() {
  const customerName = form.value.customer_name.trim();
  const peopleCount = Number(form.value.people_count);
  const customUnitPrice = Number(customAmount.value);

  localError.value = "";

  if (!customerName) {
    localError.value = "El nombre del cliente es obligatorio";
    return;
  }
  if (!Number.isFinite(peopleCount) || peopleCount <= 0) {
    localError.value = "La cantidad de personas debe ser mayor a 0";
    return;
  }
  if (priceOption.value === "CUSTOM" && (!Number.isFinite(customUnitPrice) || customUnitPrice < 0)) {
    localError.value = "Ingrese un monto válido";
    return;
  }

  emit("submit", {
    customer_name: customerName,
    people_count: peopleCount,
    amount_clp: Math.round(calculatedAmount.value),
    payment_method: form.value.payment_method,
    notes: form.value.notes || "",
  });
}

watch(() => props.initialEntry, applyInitialEntry, { immediate: true, deep: true });

onMounted(loadBusinessSettings);
</script>
