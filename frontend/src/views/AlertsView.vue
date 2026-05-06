<template>
  <div class="alerts-view-container">
    <!-- Header -->
    <div class="alerts-view-header">
      <div class="alerts-view-header-left">
        <h1 class="alerts-view-title">Listado de alertas</h1>
        <h2 class="alerts-view-subtitle">Se han detectado {{ totalCount }} alertas</h2>
      </div>
    </div>

    <!-- Filtros -->
    <AlertsFilters
      :filters="filters"
      :alert-types="alertTypes"
      :cameras="cameras"
      @update:filters="handleFiltersChange"
    />

    <!-- Tabla de alertas -->
    <AlertsTable
      :alerts="alerts"
      :loading="loading"
      :current-page="currentPage"
      :total-pages="totalPages"
      :total-count="totalCount"
      :page-size="pageSize"
      @page-change="handlePageChange"
      @alert-updated="handleAlertUpdated"
    />

    <!-- Error message -->
    <div v-if="error" class="alerts-error">
      <i class="pi pi-exclamation-triangle"></i>
      <span>{{ error }}</span>
      <button @click="loadAlerts" class="error-retry-button">
        Reintentar
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// ============================================
// IMPORTS
// ============================================
import { ref, onMounted, watch } from "vue";
import {
  fetchAlerts,
  fetchAlertTypes,
  fetchCameras,
  type Alert,
  type AlertFilters,
  type AlertType,
  type Camera,
} from "@/services/alerts";
import { useAlertsRealtimeStore } from "@/stores/alertsRealtime";

// Components
import AlertsFilters from "@/components/alerts/AlertsFilters.vue";
import AlertsTable from "@/components/alerts/AlertsTable.vue";

// Styles
import "@/styles/components/alerts.css";

// ============================================
// STATE
// ============================================
const alerts = ref<Alert[]>([]);
const alertTypes = ref<AlertType[]>([]);
const cameras = ref<Camera[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const currentPage = ref(1);
const totalPages = ref(1);
const totalCount = ref(0);
const filters = ref<AlertFilters>({});
const pageSize = 20; // Alertas por pagina
const alertsRealtime = useAlertsRealtimeStore();

// ============================================
// METHODS
// ============================================
async function loadAlerts() {
  loading.value = true;
  error.value = null;

  try {
    const response = await fetchAlerts(currentPage.value, filters.value, pageSize);
    alerts.value = response.results;
    totalCount.value = response.count;
    totalPages.value = Math.ceil(response.count / pageSize);
  } catch (err: any) {
    console.error("Error loading alerts:", err);
    error.value =
      err.response?.data?.detail ||
      err.message ||
      "Error al cargar las alertas";
  } finally {
    loading.value = false;
  }
}

async function loadFiltersData() {
  try {
    const [types, camerasList] = await Promise.all([fetchAlertTypes(), fetchCameras()]);
    alertTypes.value = types;
    cameras.value = camerasList;
  } catch (err: any) {
    console.error("Error loading filters data:", err);
  }
}

function handleFiltersChange(newFilters: AlertFilters) {
  filters.value = newFilters;
  currentPage.value = 1;
  void loadAlerts();
}

function handlePageChange(page: number) {
  currentPage.value = page;
  void loadAlerts();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function handleAlertUpdated(updatedAlert: Alert) {
  const index = alerts.value.findIndex((a) => a.id === updatedAlert.id);
  if (index !== -1) {
    alerts.value[index] = updatedAlert;
  }
}

// ============================================
// LIFECYCLE
// ============================================
onMounted(() => {
  void loadFiltersData();
  void loadAlerts();
});

watch(
  () => alertsRealtime.refreshTick,
  () => {
    if (!loading.value) {
      void loadAlerts();
    }
  }
);
</script>

<style scoped>
.alerts-view-container {
  display: flex;
  flex-direction: column;
  gap: var(--minttu-spacing-lg);
}

.alerts-view-header {
  margin-bottom: var(--minttu-spacing-xs);
}

.alerts-view-header-left {
  display: flex;
  flex-direction: column;
  gap: var(--minttu-spacing-xs);
}

.alerts-view-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--minttu-primary);
  margin: 0;
}

.alerts-view-subtitle {
  font-size: 14px;
  font-weight: 400;
  color: var(--minttu-gray);
  margin: 0;
}

/* Responsive para movil */
@media (max-width: 768px) {
  .alerts-view-container {
    gap: var(--minttu-spacing-md);
  }

  .alerts-view-title {
    font-size: 20px;
  }

  .alerts-view-subtitle {
    font-size: 13px;
  }
}

.alerts-error {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-md);
  padding: var(--minttu-spacing-md);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--minttu-radius);
  color: rgb(239, 68, 68);
  margin-top: var(--minttu-spacing-md);
}

.alerts-error i {
  font-size: 20px;
}

.error-retry-button {
  margin-left: auto;
  padding: var(--minttu-spacing-sm) var(--minttu-spacing-md);
  background: rgb(239, 68, 68);
  color: white;
  border: none;
  border-radius: var(--minttu-radius-sm);
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.2s ease;
}

.error-retry-button:hover {
  opacity: 0.9;
}
</style>

