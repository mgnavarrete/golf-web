<template>
  <div class="cameras-view-container">
    <!-- Header -->
    <div class="cameras-view-header">
      <div class="cameras-view-header-left">
        <h1 class="cameras-view-title">Gestión de Cámaras</h1>
        <h2 class="cameras-view-subtitle">
          {{ stats.total }} cámaras registradas en el sistema
        </h2>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="cameras-stats-grid">
      <div class="stat-card stat-card-total">
        <div class="stat-card-icon">
          <i class="pi pi-video"></i>
        </div>
        <div class="stat-card-content">
          <span class="stat-card-value">{{ stats.total }}</span>
          <span class="stat-card-label">Total Cámaras</span>
        </div>
      </div>
      <div class="stat-card stat-card-online">
        <div class="stat-card-icon">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="stat-card-content">
          <span class="stat-card-value">{{ stats.online }}</span>
          <span class="stat-card-label">Online</span>
        </div>
        <div class="stat-card-percentage">
          {{ stats.total > 0 ? ((stats.online / stats.total) * 100).toFixed(0) : 0 }}%
        </div>
      </div>
      <div class="stat-card stat-card-offline">
        <div class="stat-card-icon">
          <i class="pi pi-times-circle"></i>
        </div>
        <div class="stat-card-content">
          <span class="stat-card-value">{{ stats.offline }}</span>
          <span class="stat-card-label">Offline</span>
        </div>
        <div class="stat-card-percentage">
          {{ stats.total > 0 ? ((stats.offline / stats.total) * 100).toFixed(0) : 0 }}%
        </div>
      </div>
      <div class="stat-card stat-card-unknown">
        <div class="stat-card-icon">
          <i class="pi pi-question-circle"></i>
        </div>
        <div class="stat-card-content">
          <span class="stat-card-value">{{ stats.unknown }}</span>
          <span class="stat-card-label">Desconocido</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="cameras-filters" :class="{ 'filters-collapsed': !isFiltersOpen && isMobile }">
      <div class="filters-header" @click="toggleFilters" :class="{ 'mobile-collapsible': isMobile }">
        <h3 class="filters-title">Filtros</h3>
        <div class="filters-header-right">
          <button v-if="hasActiveFilters && !isMobile" @click.stop="clearFilters" class="clear-filters-btn">
            <i class="pi pi-times"></i>
            Limpiar
          </button>
          <button v-if="isMobile" class="toggle-filters-btn">
            <i :class="isFiltersOpen ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"></i>
          </button>
        </div>
      </div>
      <Transition name="slide-fade">
        <div v-if="isFiltersOpen || !isMobile" class="filters-content">
          <div class="filters-left">
            <div class="search-wrapper">
              <i class="pi pi-search"></i>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar por nombre, código o ubicación..."
                class="search-input"
                @input="handleSearch"
              />
              <button v-if="searchQuery" @click="clearSearch" class="clear-search-btn">
                <i class="pi pi-times"></i>
              </button>
            </div>
          </div>
          <div class="filters-right">
            <div class="filter-group">
              <label class="filter-label">Estado</label>
              <div
                class="custom-select"
                :class="{ 'is-open': openFilterDropdown === 'status', 'has-value': !!statusFilter }"
              >
                <button type="button" class="custom-select-trigger" @click="toggleFilterDropdown('status')">
                  <span class="custom-select-value">{{ selectedStatusFilterLabel }}</span>
                  <i class="pi pi-chevron-down custom-select-arrow"></i>
                </button>
                <div v-if="openFilterDropdown === 'status'" class="custom-select-dropdown">
                  <div class="custom-select-options">
                    <button
                      type="button"
                      class="custom-select-option"
                      :class="{ 'is-selected': !statusFilter }"
                      @click="selectStatusFilter('')"
                    >
                      <span>Todos</span>
                      <i v-if="!statusFilter" class="pi pi-check custom-select-option-check"></i>
                    </button>
                    <button
                      v-for="option in statusFilterOptions"
                      :key="option.value"
                      type="button"
                      class="custom-select-option"
                      :class="{ 'is-selected': statusFilter === option.value }"
                      @click="selectStatusFilter(option.value)"
                    >
                      <span>{{ option.label }}</span>
                      <i
                        v-if="statusFilter === option.value"
                        class="pi pi-check custom-select-option-check"
                      ></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="filter-group">
              <label class="filter-label">Ordenar por</label>
              <div
                class="custom-select"
                :class="{ 'is-open': openFilterDropdown === 'sort', 'has-value': sortBy !== 'status' }"
              >
                <button type="button" class="custom-select-trigger" @click="toggleFilterDropdown('sort')">
                  <span class="custom-select-value">{{ selectedSortByLabel }}</span>
                  <i class="pi pi-chevron-down custom-select-arrow"></i>
                </button>
                <div v-if="openFilterDropdown === 'sort'" class="custom-select-dropdown">
                  <div class="custom-select-options">
                    <button
                      v-for="option in sortByOptions"
                      :key="option.value"
                      type="button"
                      class="custom-select-option"
                      :class="{ 'is-selected': sortBy === option.value }"
                      @click="selectSortBy(option.value)"
                    >
                      <span>{{ option.label }}</span>
                      <i
                        v-if="sortBy === option.value"
                        class="pi pi-check custom-select-option-check"
                      ></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="view-toggle">
              <button 
                :class="['toggle-btn', { active: viewMode === 'grid' }]"
                @click="viewMode = 'grid'"
                title="Vista de cuadrícula"
              >
                <i class="pi pi-th-large"></i>
              </button>
              <button 
                :class="['toggle-btn', { active: viewMode === 'list' }]"
                @click="viewMode = 'list'"
                title="Vista de lista"
              >
                <i class="pi pi-list"></i>
              </button>
            </div>
          </div>
          <div v-if="isMobile" class="mobile-filter-actions">
            <button @click.stop="clearFilters" class="btn-secondary">Limpiar</button>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="cameras-loading">
      <i class="pi pi-spin pi-spinner" style="font-size: 32px"></i>
      <span>Cargando cámaras...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredCameras.length === 0 && !loading" class="cameras-empty">
      <i class="pi pi-video" style="font-size: 48px; opacity: 0.3"></i>
      <h3 v-if="cameras.length === 0">No hay cámaras registradas</h3>
      <h3 v-else>No se encontraron cámaras con los filtros aplicados</h3>
      <p v-if="cameras.length > 0">Intenta ajustar los filtros de búsqueda</p>
      <button v-if="hasActiveFilters" @click="clearFilters" class="clear-filters-btn">
        <i class="pi pi-filter-slash"></i>
        Limpiar filtros
      </button>
    </div>

    <!-- Grid View -->
    <div v-else-if="viewMode === 'grid'" class="cameras-grid">
      <div
        v-for="camera in filteredCameras"
        :key="camera.id"
        class="camera-card"
        :class="getCardClass(camera)"
        @click="openCameraDetail(camera)"
      >
        <!-- Icono de cámara -->
        <div class="camera-card-icon" :class="getStatusBadgeClass(camera.status)">
          <i class="pi pi-video"></i>
        </div>

        <!-- Info principal -->
        <div class="camera-card-main">
          <div class="camera-card-title">
            <h3 class="camera-name">{{ camera.name }}</h3>
            <span class="camera-code">{{ camera.code }}</span>
          </div>
          <div class="camera-card-details">
            <div v-if="camera.location_name" class="info-item">
              <i class="pi pi-map-marker"></i>
              <span>{{ camera.location_name }}</span>
            </div>
            <div v-if="camera.latitude && camera.longitude" class="info-item">
              <i class="pi pi-compass"></i>
              <span>{{ Number(camera.latitude).toFixed(4) }}, {{ Number(camera.longitude).toFixed(4) }}</span>
            </div>
          </div>
        </div>

        <!-- Última actividad -->
        <div class="camera-card-activity">
          <span class="activity-label">Última actividad</span>
          <span class="activity-value">{{ formatLastSeen(camera.last_seen_at) }}</span>
        </div>

        <!-- Estado de conexión -->
        <div class="camera-card-status">
          <div class="camera-status-badge" :class="getStatusBadgeClass(camera.status)">
            <span class="status-dot"></span>
            {{ getStatusLabel(camera.status) }}
          </div>
        </div>

        <!-- Estado activo -->
        <div class="camera-card-active">
          <span :class="['active-badge', camera.is_active ? 'badge-active' : 'badge-inactive']">
            {{ camera.is_active ? 'Activa' : 'Inactiva' }}
          </span>
        </div>

        <!-- Acciones -->
        <div class="camera-card-actions">
          <button class="camera-action-btn" @click.stop="openCameraDetail(camera)" title="Ver detalles">
            <i class="pi pi-eye"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="cameras-list">
      <div class="list-header">
        <div class="list-col list-col-status">Estado</div>
        <div class="list-col list-col-name">Nombre</div>
        <div class="list-col list-col-code">Código</div>
        <div class="list-col list-col-location">Ubicación</div>
        <div class="list-col list-col-lastseen">Última actividad</div>
        <div class="list-col list-col-active">Activa</div>
        <div class="list-col list-col-actions">Acciones</div>
      </div>
      <div
        v-for="camera in filteredCameras"
        :key="camera.id"
        class="list-row"
        :class="{ 'row-offline': camera.status === 'OFFLINE' }"
        @click="openCameraDetail(camera)"
      >
        <div class="list-col list-col-status">
          <span class="status-badge" :class="getStatusBadgeClass(camera.status)">
            <span class="status-dot"></span>
            {{ getStatusLabel(camera.status) }}
          </span>
        </div>
        <div class="list-col list-col-name">
          <strong>{{ camera.name }}</strong>
        </div>
        <div class="list-col list-col-code">
          <code>{{ camera.code }}</code>
        </div>
        <div class="list-col list-col-location">
          <span v-if="camera.location_name">
            <i class="pi pi-map-marker"></i>
            {{ camera.location_name }}
          </span>
          <span v-else class="text-muted">Sin ubicación</span>
        </div>
        <div class="list-col list-col-lastseen">
          {{ formatLastSeen(camera.last_seen_at) }}
        </div>
        <div class="list-col list-col-active">
          <span :class="['active-badge', camera.is_active ? 'badge-active' : 'badge-inactive']">
            {{ camera.is_active ? 'Sí' : 'No' }}
          </span>
        </div>
        <div class="list-col list-col-actions">
          <button class="action-btn" @click.stop="openCameraDetail(camera)" title="Ver detalles">
            <i class="pi pi-eye"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Camera Detail Modal -->
    <div v-if="selectedCamera" class="modal-overlay" @click="closeCameraDetail">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Detalles de Cámara</h2>
          <button class="modal-close-btn" @click="closeCameraDetail">
            <i class="pi pi-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-header">
            <div class="detail-icon" :class="getStatusBadgeClass(selectedCamera.status)">
              <i class="pi pi-video"></i>
            </div>
            <div class="detail-title">
              <h3>{{ selectedCamera.name }}</h3>
              <code>{{ selectedCamera.code }}</code>
            </div>
            <div class="detail-status">
              <span class="status-badge large" :class="getStatusBadgeClass(selectedCamera.status)">
                <span class="status-dot"></span>
                {{ getStatusLabel(selectedCamera.status) }}
              </span>
            </div>
          </div>

          <div class="detail-grid">
            <div class="detail-item">
              <label>Ubicación</label>
              <span>{{ selectedCamera.location_name || 'No especificada' }}</span>
            </div>
            <div class="detail-item">
              <label>Coordenadas</label>
              <span v-if="selectedCamera.latitude && selectedCamera.longitude">
                {{ selectedCamera.latitude }}, {{ selectedCamera.longitude }}
              </span>
              <span v-else class="text-muted">No disponibles</span>
            </div>
            <div class="detail-item">
              <label>Estado de activación</label>
              <span :class="selectedCamera.is_active ? 'text-success' : 'text-danger'">
                {{ selectedCamera.is_active ? 'Activa' : 'Inactiva' }}
              </span>
            </div>
            <div class="detail-item">
              <label>Última actividad</label>
              <span>{{ formatLastSeenDetailed(selectedCamera.last_seen_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="cameras-error">
      <i class="pi pi-exclamation-triangle"></i>
      <span>{{ error }}</span>
      <button @click="loadCameras" class="error-retry-button">
        Reintentar
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// ============================================
// IMPORTS
// ============================================
import { ref, computed, onMounted, onUnmounted } from "vue";
import {
  fetchAllCameras,
  calculateCameraStats,
  filterCameras,
  sortCameras,
  type Camera,
  type CameraStats,
  type CameraFilters,
} from "@/services/cameras";

interface FilterOption {
  value: string;
  label: string;
}

type FilterDropdownKey = "status" | "sort";

const statusFilterOptions: FilterOption[] = [
  { value: "ONLINE", label: "Online" },
  { value: "OFFLINE", label: "Offline" },
  { value: "UNKNOWN", label: "Desconocido" },
];

const sortByOptions: FilterOption[] = [
  { value: "status", label: "Estado" },
  { value: "name", label: "Nombre" },
  { value: "code", label: "Codigo" },
  { value: "location", label: "Ubicacion" },
  { value: "last_seen", label: "Ultima actividad" },
];

// ============================================
// STATE
// ============================================
const cameras = ref<Camera[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const searchQuery = ref("");
const statusFilter = ref("");
const sortBy = ref("status");
const viewMode = ref<"grid" | "list">("grid");
const selectedCamera = ref<Camera | null>(null);
const isMobile = ref(false);
const isFiltersOpen = ref(false);
const openFilterDropdown = ref<FilterDropdownKey | null>(null);

// ============================================
// COMPUTED
// ============================================
const stats = computed<CameraStats>(() => {
  return calculateCameraStats(cameras.value);
});

const filteredCameras = computed(() => {
  const filters: CameraFilters = {};
  
  if (searchQuery.value) {
    filters.search = searchQuery.value;
  }
  
  if (statusFilter.value) {
    filters.status = statusFilter.value;
  }

  let result = filterCameras(cameras.value, filters);
  result = sortCameras(result, sortBy.value);
  
  return result;
});

const hasActiveFilters = computed(() => {
  return searchQuery.value || statusFilter.value;
});

const selectedStatusFilterLabel = computed(() => {
  if (!statusFilter.value) return "Todos";
  const option = statusFilterOptions.find((item) => item.value === statusFilter.value);
  return option?.label ?? statusFilter.value;
});

const selectedSortByLabel = computed(() => {
  const option = sortByOptions.find((item) => item.value === sortBy.value);
  return option?.label ?? "Estado";
});

// ============================================
// METHODS
// ============================================
async function loadCameras() {
  loading.value = true;
  error.value = null;

  try {
    cameras.value = await fetchAllCameras();
  } catch (err: any) {
    console.error("Error loading cameras:", err);
    error.value =
      err.response?.data?.detail ||
      err.message ||
      "Error al cargar las cámaras";
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  // El filtrado es reactivo a través de computed
}

function clearSearch() {
  searchQuery.value = "";
}

function closeFilterDropdowns() {
  openFilterDropdown.value = null;
}

function toggleFilterDropdown(key: FilterDropdownKey) {
  if (openFilterDropdown.value === key) {
    closeFilterDropdowns();
    return;
  }
  openFilterDropdown.value = key;
}

function selectStatusFilter(value: string) {
  statusFilter.value = value;
  closeFilterDropdowns();
}

function selectSortBy(value: string) {
  sortBy.value = value;
  closeFilterDropdowns();
}

function handleFilterClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement | null;
  if (!target) return;

  if (!target.closest('.custom-select')) {
    closeFilterDropdowns();
  }
}

function clearFilters() {
  searchQuery.value = "";
  statusFilter.value = "";
  sortBy.value = "status";
  closeFilterDropdowns();
}

function toggleFilters() {
  if (isMobile.value) {
    isFiltersOpen.value = !isFiltersOpen.value;
    if (!isFiltersOpen.value) {
      closeFilterDropdowns();
    }
  }
}

function checkMobile() {
  isMobile.value = window.innerWidth <= 768;
  if (!isMobile.value) {
    isFiltersOpen.value = true;
  } else {
    isFiltersOpen.value = false;
  }
}

function openCameraDetail(camera: Camera) {
  selectedCamera.value = camera;
}

function closeCameraDetail() {
  selectedCamera.value = null;
}

function getCardClass(camera: Camera): string {
  const classes = [];
  if (camera.status === "ONLINE") classes.push("card-online");
  else if (camera.status === "OFFLINE") classes.push("card-offline");
  else classes.push("card-unknown");
  if (!camera.is_active) classes.push("card-inactive");
  return classes.join(" ");
}

function getStatusBadgeClass(status: string): string {
  switch (status) {
    case "ONLINE":
      return "status-online";
    case "OFFLINE":
      return "status-offline";
    default:
      return "status-unknown";
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case "ONLINE":
      return "Online";
    case "OFFLINE":
      return "Offline";
    default:
      return "Desconocido";
  }
}

function formatLastSeen(dateString: string | null): string {
  if (!dateString) return "Sin actividad";

  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Hace un momento";
  if (diffMins < 60) return `Hace ${diffMins} min`;
  if (diffHours < 24) return `Hace ${diffHours}h`;
  if (diffDays === 1) return "Ayer";
  if (diffDays < 7) return `Hace ${diffDays} días`;

  return date.toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "short",
  });
}

function formatLastSeenDetailed(dateString: string | null): string {
  if (!dateString) return "Nunca";

  const date = new Date(dateString);
  return date.toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ============================================
// LIFECYCLE
// ============================================
onMounted(() => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
  document.addEventListener("click", handleFilterClickOutside);
  loadCameras();
});

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
  document.removeEventListener("click", handleFilterClickOutside);
});
</script>

<style scoped>
.cameras-view-container {
  display: flex;
  flex-direction: column;
  gap: var(--minttu-spacing-lg);
}

/* Header */
.cameras-view-header {
  margin-bottom: var(--minttu-spacing-xs);
}

.cameras-view-header-left {
  display: flex;
  flex-direction: column;
  gap: var(--minttu-spacing-xs);
}

.cameras-view-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--minttu-primary);
  margin: 0;
}

.cameras-view-subtitle {
  font-size: 14px;
  font-weight: 400;
  color: var(--minttu-gray);
  margin: 0;
}

/* Stats Cards */
.cameras-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--minttu-spacing-md);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-md);
  background: var(--minttu-white);
  border-radius: var(--minttu-radius);
  padding: var(--minttu-spacing-lg);
  box-shadow: var(--minttu-shadow-soft);
  border-left: 4px solid transparent;
  position: relative;
}

.stat-card-total {
  border-left-color: var(--minttu-primary);
}

.stat-card-online {
  border-left-color: rgb(34, 197, 94);
}

.stat-card-offline {
  border-left-color: rgb(239, 68, 68);
}

.stat-card-unknown {
  border-left-color: var(--minttu-gray);
}

.stat-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--minttu-bg);
}

.stat-card-icon i {
  font-size: 20px;
}

.stat-card-total .stat-card-icon i {
  color: var(--minttu-primary);
}

.stat-card-online .stat-card-icon i {
  color: rgb(34, 197, 94);
}

.stat-card-offline .stat-card-icon i {
  color: rgb(239, 68, 68);
}

.stat-card-unknown .stat-card-icon i {
  color: var(--minttu-gray);
}

.stat-card-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-card-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--minttu-primary);
  line-height: 1;
}

.stat-card-label {
  font-size: 13px;
  color: var(--minttu-gray);
}

.stat-card-percentage {
  position: absolute;
  top: var(--minttu-spacing-md);
  right: var(--minttu-spacing-md);
  font-size: 12px;
  font-weight: 600;
  color: var(--minttu-gray);
  background: var(--minttu-bg);
  padding: 4px 8px;
  border-radius: 12px;
}

/* Filters */
.cameras-filters {
  background: var(--minttu-white);
  border-radius: var(--minttu-radius);
  padding: var(--minttu-spacing-lg);
  box-shadow: var(--minttu-shadow-soft);
  margin-bottom: var(--minttu-spacing-lg);
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--minttu-spacing-md);
}

.filters-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--minttu-primary);
  margin: 0;
}

.filters-header-right {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-sm);
}

.clear-filters-btn {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-xs);
  padding: var(--minttu-spacing-xs) var(--minttu-spacing-md);
  background: transparent;
  border: 1px solid var(--minttu-border);
  color: var(--minttu-gray);
  border-radius: var(--minttu-radius-sm);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-filters-btn:hover {
  background: var(--minttu-bg);
  border-color: var(--minttu-gray);
}

.toggle-filters-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--minttu-bg);
  border: none;
  color: var(--minttu-primary);
  cursor: pointer;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.toggle-filters-btn i {
  font-size: 14px;
}

.filters-content {
  display: flex;
  flex-direction: column;
  gap: var(--minttu-spacing-md);
}

.filters-left {
  width: 100%;
}

.search-wrapper {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-sm);
  background: var(--minttu-bg);
  border-radius: var(--minttu-radius-sm);
  padding: var(--minttu-spacing-sm) var(--minttu-spacing-md);
  border: 1px solid var(--minttu-border);
  transition: border-color 0.2s ease;
}

.search-wrapper:focus-within {
  border-color: var(--minttu-primary);
}

.search-wrapper i {
  color: var(--minttu-gray);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--minttu-primary);
  outline: none;
  font-family: inherit;
}

.search-input::placeholder {
  color: var(--minttu-gray);
}

.clear-search-btn {
  background: none;
  border: none;
  color: var(--minttu-gray);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s ease;
}

.clear-search-btn:hover {
  color: var(--minttu-primary);
}

.filters-right {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--minttu-spacing-md);
  align-items: end;
}

.mobile-filter-actions {
  display: none;
}

.filter-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--minttu-spacing-xs);
  min-width: 0;
}

.filter-label {
  font-size: 13px;
  color: var(--minttu-primary);
}

.custom-select {
  width: 100%;
  position: relative;
}

.custom-select-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--minttu-spacing-sm);
  padding: var(--minttu-spacing-sm) var(--minttu-spacing-md);
  border: 1px solid var(--minttu-border);
  border-radius: 10px;
  font-size: 14px;
  font-family: inherit;
  color: var(--minttu-primary);
  background: linear-gradient(180deg, #ffffff 0%, #fcfcfc 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
  min-height: 42px;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.custom-select-trigger:hover {
  border-color: rgba(29, 33, 49, 0.45);
}

.custom-select.is-open .custom-select-trigger {
  border-color: var(--minttu-primary);
  box-shadow: 0 0 0 3px rgba(29, 33, 49, 0.08);
}

.custom-select.has-value .custom-select-trigger {
  border-color: rgba(29, 33, 49, 0.25);
}

.custom-select-value {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.custom-select.has-value .custom-select-value {
  font-weight: 500;
}

.custom-select-arrow {
  color: var(--minttu-gray);
  font-size: 12px;
  transition: transform 0.2s ease, color 0.2s ease;
  flex-shrink: 0;
}

.custom-select.is-open .custom-select-arrow {
  transform: rotate(180deg);
  color: var(--minttu-primary);
}

.custom-select-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 1050;
  background: var(--minttu-white);
  border: 1px solid var(--minttu-border);
  border-radius: 12px;
  box-shadow: var(--minttu-shadow-medium);
  overflow: hidden;
}

.custom-select-options {
  max-height: 220px;
  overflow-y: auto;
  padding: var(--minttu-spacing-xs);
}

.custom-select-option {
  width: 100%;
  border: 1px solid transparent;
  border-radius: 9px;
  background: transparent;
  color: var(--minttu-primary);
  font-size: 13px;
  font-family: inherit;
  text-align: left;
  padding: 9px var(--minttu-spacing-sm);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--minttu-spacing-sm);
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.custom-select-option:hover {
  background: rgba(247, 247, 247, 0.85);
  border-color: rgba(29, 33, 49, 0.12);
}

.custom-select-option.is-selected {
  background: rgba(29, 33, 49, 0.07);
  border-color: rgba(29, 33, 49, 0.2);
  font-weight: 600;
}

.custom-select-option-check {
  color: var(--minttu-primary);
  font-size: 12px;
}

.view-toggle {
  display: inline-flex;
  border: 1px solid var(--minttu-border);
  border-radius: var(--minttu-radius-sm);
  overflow: hidden;
  justify-self: end;
  align-self: end;
  width: fit-content;
}

.toggle-btn {
  width: 42px;
  height: 42px;
  padding: 0;
  border: none;
  background: var(--minttu-white);
  color: var(--minttu-gray);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-btn:first-child {
  border-right: 1px solid var(--minttu-border);
}

.toggle-btn.active {
  background: var(--minttu-primary);
  color: var(--minttu-white);
}

.toggle-btn:hover:not(.active) {
  background: var(--minttu-bg);
}

/* Loading & Empty States */
.cameras-loading,
.cameras-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--minttu-spacing-md);
  padding: var(--minttu-spacing-xl) var(--minttu-spacing-lg);
  background: var(--minttu-white);
  border-radius: var(--minttu-radius);
  box-shadow: var(--minttu-shadow-soft);
  color: var(--minttu-gray);
  min-height: 300px;
}

.cameras-empty h3 {
  margin: 0;
  color: var(--minttu-primary);
  font-size: 18px;
}

.cameras-empty p {
  margin: 0;
  font-size: 14px;
}

.cameras-empty .clear-filters-btn {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-xs);
  padding: var(--minttu-spacing-sm) var(--minttu-spacing-md);
  background: var(--minttu-primary);
  color: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-sm);
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.cameras-empty .clear-filters-btn:hover {
  opacity: 0.9;
}

/* Grid View */
.cameras-grid {
  display: flex;
  flex-direction: column;
  gap: var(--minttu-spacing-md);
}

.camera-card {
  background: var(--minttu-white);
  border-radius: var(--minttu-radius);
  padding: var(--minttu-spacing-md) var(--minttu-spacing-lg);
  box-shadow: var(--minttu-shadow-soft);
  border-left: 4px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  display: grid;
  grid-template-columns: 56px 1fr 140px 110px 80px 44px;
  align-items: center;
  gap: var(--minttu-spacing-lg);
}

.camera-card:hover {
  box-shadow: var(--minttu-shadow-medium);
  background: var(--minttu-bg);
}

.card-online {
  border-left-color: rgb(34, 197, 94);
}

.card-offline {
  border-left-color: rgb(239, 68, 68);
}

.card-unknown {
  border-left-color: var(--minttu-gray);
}

.card-inactive {
  opacity: 0.7;
}

/* Icono de cámara */
.camera-card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.camera-card-icon i {
  font-size: 22px;
  color: white;
}

.camera-card-icon.status-online {
  background: rgb(34, 197, 94);
}

.camera-card-icon.status-offline {
  background: rgb(239, 68, 68);
}

.camera-card-icon.status-unknown {
  background: var(--minttu-gray);
}

/* Info principal */
.camera-card-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.camera-card-title {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-sm);
  flex-wrap: wrap;
}

.camera-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--minttu-primary);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.camera-code {
  font-size: 12px;
  color: var(--minttu-gray);
  font-family: monospace;
  background: rgba(29, 33, 49, 0.05);
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.camera-card-details {
  display: flex;
  gap: var(--minttu-spacing-md);
  flex-wrap: wrap;
}

.camera-card-details .info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--minttu-gray);
}

.camera-card-details .info-item i {
  font-size: 12px;
}

/* Última actividad */
.camera-card-activity {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: center;
}

.activity-label {
  font-size: 11px;
  color: var(--minttu-gray);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.activity-value {
  font-size: 13px;
  color: var(--minttu-primary);
  font-weight: 500;
}

/* Estado de conexión */
.camera-card-status {
  display: flex;
  justify-content: center;
}

.camera-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-online {
  background: rgba(34, 197, 94, 0.1);
  color: rgb(34, 197, 94);
}

.status-offline {
  background: rgba(239, 68, 68, 0.1);
  color: rgb(239, 68, 68);
}

.status-unknown {
  background: rgba(156, 163, 175, 0.1);
  color: rgb(156, 163, 175);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.status-online .status-dot {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Estado activo */
.camera-card-active {
  display: flex;
  justify-content: center;
}

/* Acciones */
.camera-card-actions {
  display: flex;
  justify-content: center;
}

.camera-action-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid var(--minttu-border);
  background: var(--minttu-white);
  color: var(--minttu-gray);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-action-btn:hover {
  background: var(--minttu-primary);
  color: var(--minttu-white);
  border-color: var(--minttu-primary);
}

/* List View */
.cameras-list {
  background: var(--minttu-white);
  border-radius: var(--minttu-radius);
  box-shadow: var(--minttu-shadow-soft);
  overflow: hidden;
}

.list-header {
  display: grid;
  grid-template-columns: 120px 1fr 120px 1fr 150px 80px 80px;
  gap: var(--minttu-spacing-md);
  padding: var(--minttu-spacing-md) var(--minttu-spacing-lg);
  background: var(--minttu-bg);
  font-size: 12px;
  font-weight: 600;
  color: var(--minttu-gray);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.list-row {
  display: grid;
  grid-template-columns: 120px 1fr 120px 1fr 150px 80px 80px;
  gap: var(--minttu-spacing-md);
  padding: var(--minttu-spacing-md) var(--minttu-spacing-lg);
  border-bottom: 1px solid var(--minttu-border);
  align-items: center;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.list-row:hover {
  background: var(--minttu-bg);
}

.list-row:last-child {
  border-bottom: none;
}

.row-offline {
  background: rgba(239, 68, 68, 0.03);
}

.list-col code {
  background: rgba(29, 33, 49, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.list-col .text-muted {
  color: var(--minttu-gray);
  font-style: italic;
}

.list-col i {
  font-size: 12px;
  margin-right: 4px;
  color: var(--minttu-gray);
}

.active-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.badge-active {
  background: rgba(34, 197, 94, 0.1);
  color: rgb(34, 197, 94);
}

.badge-inactive {
  background: rgba(239, 68, 68, 0.1);
  color: rgb(239, 68, 68);
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--minttu-border);
  background: var(--minttu-white);
  color: var(--minttu-gray);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: var(--minttu-primary);
  color: var(--minttu-white);
  border-color: var(--minttu-primary);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--minttu-spacing-lg);
}

.modal-content {
  background: var(--minttu-white);
  border-radius: var(--minttu-radius);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--minttu-shadow-medium);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--minttu-spacing-lg);
  border-bottom: 1px solid var(--minttu-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  color: var(--minttu-primary);
}

.modal-close-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: var(--minttu-bg);
  color: var(--minttu-gray);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.modal-close-btn:hover {
  background: var(--minttu-primary);
  color: var(--minttu-white);
}

.modal-body {
  padding: var(--minttu-spacing-lg);
}

.detail-header {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-md);
  margin-bottom: var(--minttu-spacing-lg);
  padding-bottom: var(--minttu-spacing-lg);
  border-bottom: 1px solid var(--minttu-border);
}

.detail-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-icon i {
  font-size: 24px;
  color: white;
}

.detail-icon.status-online {
  background: rgb(34, 197, 94);
}

.detail-icon.status-offline {
  background: rgb(239, 68, 68);
}

.detail-icon.status-unknown {
  background: var(--minttu-gray);
}

.detail-title {
  flex: 1;
}

.detail-title h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: var(--minttu-primary);
}

.detail-title code {
  font-size: 13px;
  color: var(--minttu-gray);
  background: var(--minttu-bg);
  padding: 2px 8px;
  border-radius: 4px;
}

.detail-status .status-badge.large {
  font-size: 14px;
  padding: 6px 14px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--minttu-spacing-md);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-size: 12px;
  color: var(--minttu-gray);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-item span {
  font-size: 14px;
  color: var(--minttu-primary);
}

.text-success {
  color: rgb(34, 197, 94) !important;
}

.text-danger {
  color: rgb(239, 68, 68) !important;
}

.text-muted {
  color: var(--minttu-gray) !important;
  font-style: italic;
}

/* Error */
.cameras-error {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-md);
  padding: var(--minttu-spacing-md);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--minttu-radius);
  color: rgb(239, 68, 68);
}

.cameras-error i {
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

/* Responsive */
@media (max-width: 1200px) {
  .list-header,
  .list-row {
    grid-template-columns: 100px 1fr 100px 1fr 100px 60px 60px;
  }
}

@media (max-width: 1200px) {
  .camera-card {
    grid-template-columns: 56px 1fr 120px 100px 70px 44px;
    gap: var(--minttu-spacing-md);
  }
}

@media (max-width: 992px) {
  .cameras-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    min-width: unset;
  }

  .filters-right {
    justify-content: space-between;
  }

  .camera-card {
    grid-template-columns: 48px 1fr 90px 44px;
    gap: var(--minttu-spacing-sm);
    padding: var(--minttu-spacing-md);
  }

  .camera-card-icon {
    width: 48px;
    height: 48px;
  }

  .camera-card-icon i {
    font-size: 18px;
  }

  .camera-card-activity,
  .camera-card-active {
    display: none;
  }

  .list-header,
  .list-row {
    grid-template-columns: 100px 1fr 1fr 80px;
  }

  .list-col-code,
  .list-col-location,
  .list-col-lastseen {
    display: none;
  }
}

@media (max-width: 768px) {
  .cameras-view-container {
    gap: var(--minttu-spacing-md);
  }

  .cameras-view-header {
    margin-bottom: 0;
  }

  .cameras-view-title {
    font-size: 20px;
  }

  .cameras-view-subtitle {
    font-size: 13px;
  }

  .cameras-stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--minttu-spacing-sm);
  }

  .stat-card {
    padding: var(--minttu-spacing-md);
  }

  .stat-card-value {
    font-size: 24px;
  }

  .stat-card-icon {
    width: 40px;
    height: 40px;
  }

  .stat-card-icon i {
    font-size: 18px;
  }

  /* Filters */
  .cameras-filters {
    padding: var(--minttu-spacing-md);
  }

  .cameras-filters.filters-collapsed {
    padding-bottom: var(--minttu-spacing-md);
  }

  .filters-header {
    margin-bottom: 0;
  }

  .filters-header.mobile-collapsible {
    cursor: pointer;
    padding-bottom: var(--minttu-spacing-sm);
    border-bottom: 1px solid var(--minttu-border);
    margin-bottom: 0;
  }

  .cameras-filters.filters-collapsed .filters-header.mobile-collapsible {
    border-bottom: none;
    padding-bottom: 0;
  }

  .toggle-filters-btn {
    display: flex;
  }

  .filters-header .clear-filters-btn {
    display: none;
  }

  .filters-content {
    gap: var(--minttu-spacing-md);
    padding-top: var(--minttu-spacing-md);
  }

  .filters-right {
    grid-template-columns: 1fr;
    gap: var(--minttu-spacing-sm);
  }

  .filter-group {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--minttu-spacing-xs);
  }

  .custom-select-trigger {
    width: 100%;
    font-size: 16px; /* Evitar zoom en iOS */
    min-height: 44px;
    padding: var(--minttu-spacing-md);
  }

  .search-input {
    font-size: 16px; /* Evitar zoom en iOS */
    min-height: 44px;
  }

  .view-toggle {
    width: fit-content;
    margin-left: auto;
    justify-self: end;
  }

  .toggle-btn {
    flex: 0 0 44px;
    width: 44px;
    height: 44px;
    min-height: 44px;
  }

  .mobile-filter-actions {
    display: flex;
    gap: var(--minttu-spacing-md);
    margin-top: var(--minttu-spacing-sm);
  }

  .mobile-filter-actions .btn-secondary {
    flex: 1;
    justify-content: center;
    min-height: 44px;
    padding: var(--minttu-spacing-sm) var(--minttu-spacing-md);
    border-radius: var(--minttu-radius-sm);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid var(--minttu-border);
    background: var(--minttu-bg);
    color: var(--minttu-primary);
  }

  .mobile-filter-actions .btn-secondary:hover {
    background: var(--minttu-white);
    border-color: var(--minttu-primary);
  }

  /* Camera Cards */
  .camera-card {
    grid-template-columns: 44px 1fr 44px;
    gap: var(--minttu-spacing-sm);
    padding: var(--minttu-spacing-md);
  }

  .camera-card-icon {
    width: 44px;
    height: 44px;
  }

  .camera-card-icon i {
    font-size: 18px;
  }

  .camera-card-status,
  .camera-card-activity,
  .camera-card-active {
    display: none;
  }

  .camera-name {
    font-size: 14px;
  }

  .camera-code {
    font-size: 11px;
  }

  .camera-card-details {
    flex-direction: column;
    gap: 4px;
  }

  /* List View - Convert to cards on mobile */
  .cameras-list {
    display: none;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .modal-overlay {
    padding: var(--minttu-spacing-md);
  }

  .modal-content {
    max-width: 100%;
    max-height: 100vh;
    border-radius: var(--minttu-radius);
  }
}

/* Transiciones para el acordeón */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease-out;
  overflow: hidden;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  margin-top: 0;
  margin-bottom: 0;
}

.slide-fade-enter-to,
.slide-fade-leave-from {
  max-height: 1000px;
}
</style>


