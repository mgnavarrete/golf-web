<template>
  <form class="golf-record-form" @submit.prevent="handleSubmit">
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

    <div v-if="priceOption === 'CUSTOM'" class="form-group">
      <label>Valor Unitario Personalizado (CLP)</label>
      <input v-model.number="form.unit_price_clp" type="number" min="0" placeholder="Valor unitario" />
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
  type PaymentMethod,
  type RangeOrderPayload,
} from "@/services/golf";

import "@/styles/components/record-form.css";

type RangePriceOption = "NORMAL" | "CUSTOM";

const props = withDefaults(
  defineProps<{
    initialOrder?: Partial<RangeOrderPayload> | null;
    saving?: boolean;
    submitLabel?: string;
    showCancel?: boolean;
    cancelLabel?: string;
    error?: string;
  }>(),
  {
    initialOrder: null,
    saving: false,
    submitLabel: "Guardar Pedido",
    showCancel: false,
    cancelLabel: "Cancelar",
    error: "",
  },
);

const emit = defineEmits<{
  (e: "submit", payload: RangeOrderPayload): void;
  (e: "cancel"): void;
}>();

const paymentOptions = [
  { label: "Efectivo", value: "CASH" },
  { label: "Tarjeta", value: "CARD" },
  { label: "Transferencia", value: "TRANSFER" },
  { label: "Otro", value: "OTHER" },
];

const defaultPrice = ref(5000);
const priceOption = ref<RangePriceOption>("NORMAL");
const localError = ref("");

const form = ref({
  customer_name: "",
  baskets_count: 1,
  unit_price_clp: 5000,
  payment_method: "CASH" as PaymentMethod,
  notes: "",
});

const priceOptions = computed(() => [
  { label: `Normal (${formatClp(defaultPrice.value)})`, value: "NORMAL" },
  { label: "Personalizado", value: "CUSTOM" },
]);

const calculatedAmount = computed(() => normaliseCount(form.value.baskets_count) * normalisePrice(form.value.unit_price_clp));
const visibleError = computed(() => localError.value || props.error);

function normaliseCount(value: unknown) {
  const count = Number(value);
  if (!Number.isFinite(count) || count <= 0) return 1;
  return count;
}

function normalisePrice(value: unknown) {
  const price = Number(value);
  if (!Number.isFinite(price) || price < 0) return 0;
  return price;
}

function applyInitialOrder() {
  localError.value = "";
  const initial = props.initialOrder;

  if (!initial) {
    form.value = {
      customer_name: "",
      baskets_count: 1,
      unit_price_clp: defaultPrice.value,
      payment_method: "CASH",
      notes: "",
    };
    priceOption.value = "NORMAL";
    return;
  }

  const unitPrice = normalisePrice(initial.unit_price_clp);

  form.value = {
    customer_name: initial.customer_name || "",
    baskets_count: normaliseCount(initial.baskets_count),
    unit_price_clp: unitPrice,
    payment_method: initial.payment_method || "CASH",
    notes: initial.notes || "",
  };
  priceOption.value = unitPrice === defaultPrice.value ? "NORMAL" : "CUSTOM";
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
    defaultPrice.value = settings.default_range_unit_price_clp;
    if (props.initialOrder) {
      applyInitialOrder();
    } else if (priceOption.value === "NORMAL") {
      form.value.unit_price_clp = defaultPrice.value;
    }
  } catch {
    // Keep fallback price if settings cannot be loaded.
  }
}

function handleSubmit() {
  const customerName = form.value.customer_name.trim();
  const basketsCount = Number(form.value.baskets_count);
  const unitPrice = Number(form.value.unit_price_clp);

  localError.value = "";

  if (!customerName) {
    localError.value = "El nombre del cliente es obligatorio";
    return;
  }
  if (!Number.isFinite(basketsCount) || basketsCount <= 0) {
    localError.value = "La cantidad de canastos debe ser mayor a 0";
    return;
  }
  if (!Number.isFinite(unitPrice) || unitPrice <= 0) {
    localError.value = "El valor unitario debe ser mayor a 0";
    return;
  }

  emit("submit", {
    customer_name: customerName,
    baskets_count: basketsCount,
    unit_price_clp: Math.round(unitPrice),
    total_amount_clp: Math.round(calculatedAmount.value),
    payment_method: form.value.payment_method,
    notes: form.value.notes || "",
  });
}

watch(priceOption, (value) => {
  if (value === "NORMAL") form.value.unit_price_clp = defaultPrice.value;
});

watch(() => props.initialOrder, applyInitialOrder, { immediate: true, deep: true });

onMounted(loadBusinessSettings);
</script>
