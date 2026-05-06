<template>
  <div class="report-preview">
    <!-- Header -->
    <div class="report-header">
      <div class="branding">
        <img :src="logoSrc" alt="Minttu" class="report-logo" />
        <div class="title-block">
          <h1>Reporte de Métricas</h1>
          <div class="date-range">
            {{ formatDate(summary.date_range.from) }} al {{ formatDate(summary.date_range.to) }}
          </div>
          <div class="generated-at" v-if="summary.generated_at">
            Generado: {{ formatDateTime(summary.generated_at) }}
          </div>
        </div>
      </div>
    </div>

    <!-- KPIs -->
    <div class="report-kpis">
      <div class="kpi-card">
        <div class="kpi-icon total">
          <i class="pi pi-bell"></i>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ summary.kpis.total }}</span>
          <span class="kpi-label">Total Alertas</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon pending">
          <i class="pi pi-clock"></i>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ summary.kpis.pending }}</span>
          <span class="kpi-label">Pendientes</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon closed">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ summary.kpis.closed }}</span>
          <span class="kpi-label">Cerradas</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon false">
          <i class="pi pi-times-circle"></i>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ summary.kpis.false_positives }}</span>
          <span class="kpi-label">Falsos Positivos</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon accuracy">
          <i class="pi pi-percentage"></i>
        </div>
        <div class="kpi-content">
          <span class="kpi-value">{{ summary.kpis.accuracy }}%</span>
          <span class="kpi-label">Precisión</span>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="report-charts">
      <!-- Distribución por Tipo -->
      <div class="chart-section">
        <h3>
          <i class="pi pi-chart-bar"></i>
          Distribución por Tipo de Alerta
        </h3>
        <div class="chart-content">
          <div v-if="summary.alerts_by_type.length === 0" class="no-data">
            Sin datos disponibles
          </div>
          <div v-else class="type-bars">
            <div
              v-for="item in summary.alerts_by_type"
              :key="item.code"
              class="type-bar-item"
            >
              <div class="type-info">
                <span class="type-name">{{ item.name }}</span>
                <span class="type-count">{{ item.count }}</span>
              </div>
              <div class="type-bar-container">
                <div
                  class="type-bar-fill"
                  :style="{ width: getBarWidth(item.count) }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Distribución por Hora -->
      <div class="chart-section">
        <h3>
          <i class="pi pi-clock"></i>
          Detecciones por Hora del Día
        </h3>
        <div class="chart-content">
          <div class="hourly-chart">
            <div
              v-for="hour in summary.hourly_distribution"
              :key="hour.hour"
              class="hour-bar"
              :title="`${hour.hour}:00 - ${hour.count} alertas`"
            >
              <div
                class="hour-bar-fill"
                :style="{ height: getHourBarHeight(hour.count) }"
              ></div>
              <span class="hour-label">{{ hour.hour }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Distribución por Estado -->
      <div class="chart-section">
        <h3>
          <i class="pi pi-chart-pie"></i>
          Distribución por Estado
        </h3>
        <div class="chart-content status-grid">
          <div class="status-item pending">
            <div class="status-icon"><i class="pi pi-clock"></i></div>
            <div class="status-info">
              <span class="status-count">{{ summary.alerts_by_status.pending }}</span>
              <span class="status-label">Pendientes</span>
            </div>
          </div>
          <div class="status-item review">
            <div class="status-icon"><i class="pi pi-eye"></i></div>
            <div class="status-info">
              <span class="status-count">{{ summary.alerts_by_status.in_review }}</span>
              <span class="status-label">En Revisión</span>
            </div>
          </div>
          <div class="status-item closed">
            <div class="status-icon"><i class="pi pi-check"></i></div>
            <div class="status-info">
              <span class="status-count">{{ summary.alerts_by_status.closed }}</span>
              <span class="status-label">Cerradas</span>
            </div>
          </div>
          <div class="status-item false">
            <div class="status-icon"><i class="pi pi-times"></i></div>
            <div class="status-info">
              <span class="status-count">{{ summary.alerts_by_status.false_positive }}</span>
              <span class="status-label">Falsos Positivos</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Cámaras -->
      <div class="chart-section" v-if="summary.alerts_by_camera.length > 0">
        <h3>
          <i class="pi pi-video"></i>
          Top Cámaras con Más Alertas
        </h3>
        <div class="chart-content">
          <table class="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Cámara</th>
                <th>Código</th>
                <th class="right">Detecciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(camera, index) in summary.alerts_by_camera" :key="camera.code">
                <td class="rank">{{ index + 1 }}</td>
                <td>{{ camera.name }}</td>
                <td><code>{{ camera.code }}</code></td>
                <td class="right">{{ camera.count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Estados por Tipo -->
      <div class="chart-section" v-if="Object.keys(summary.status_by_type || {}).length > 0">
        <h3>
          <i class="pi pi-table"></i>
          Estados por Tipo de Alerta
        </h3>
        <div class="chart-content">
          <table class="data-table">
            <thead>
              <tr>
                <th>Tipo</th>
                <th class="right">Pendiente</th>
                <th class="right">En Revisión</th>
                <th class="right">Cerrada</th>
                <th class="right">Falso +</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="type in summary.alerts_by_type" :key="type.code">
                <td>{{ type.name }}</td>
                <td class="right">{{ summary.status_by_type[type.code]?.pending || 0 }}</td>
                <td class="right">{{ summary.status_by_type[type.code]?.in_review || 0 }}</td>
                <td class="right">{{ summary.status_by_type[type.code]?.closed || 0 }}</td>
                <td class="right">{{ summary.status_by_type[type.code]?.false_positive || 0 }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="report-footer">
      <p>Reporte generado por Minttu Dashboard</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Report, ReportSummary } from "@/services/reports";
import logoSrc from "@/assets/brand/logo_dark.svg";

const props = defineProps<{
  summary: ReportSummary;
  report: Report;
}>();

// ============================================
// COMPUTED
// ============================================
const maxTypeCount = computed(() => {
  if (!props.summary.alerts_by_type.length) return 1;
  return Math.max(...props.summary.alerts_by_type.map((t) => t.count), 1);
});

const maxHourCount = computed(() => {
  if (!props.summary.hourly_distribution.length) return 1;
  return Math.max(...props.summary.hourly_distribution.map((h) => h.count), 1);
});

// ============================================
// METHODS
// ============================================
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getBarWidth(count: number): string {
  const percentage = (count / maxTypeCount.value) * 100;
  return `${percentage}%`;
}

function getHourBarHeight(count: number): string {
  if (maxHourCount.value === 0) return "0%";
  const percentage = (count / maxHourCount.value) * 100;
  return `${Math.max(percentage, 2)}%`;
}
</script>

<style scoped>
.report-preview {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--minttu-primary);
}

/* Header */
.report-header {
  margin-bottom: var(--minttu-spacing-lg);
  padding-bottom: var(--minttu-spacing-lg);
  border-bottom: 2px solid var(--minttu-primary);
}

.branding {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-lg);
}

.report-logo {
  height: 48px;
}

.title-block h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--minttu-primary);
}

.date-range {
  font-size: 16px;
  color: var(--minttu-gray);
}

.generated-at {
  font-size: 12px;
  color: var(--minttu-gray);
  margin-top: 4px;
}

/* KPIs */
.report-kpis {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--minttu-spacing-md);
  margin-bottom: var(--minttu-spacing-lg);
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-md);
  padding: var(--minttu-spacing-md);
  background: var(--minttu-bg);
  border-radius: var(--minttu-radius-sm);
  border-left: 3px solid var(--minttu-border);
}

.kpi-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-icon i {
  font-size: 18px;
  color: white;
}

.kpi-icon.total {
  background: var(--minttu-primary);
}

.kpi-icon.pending {
  background: rgb(245, 158, 11);
}

.kpi-icon.closed {
  background: rgb(34, 197, 94);
}

.kpi-icon.false {
  background: rgb(239, 68, 68);
}

.kpi-icon.accuracy {
  background: rgb(59, 130, 246);
}

.kpi-content {
  display: flex;
  flex-direction: column;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--minttu-primary);
  line-height: 1;
}

.kpi-label {
  font-size: 12px;
  color: var(--minttu-gray);
  margin-top: 2px;
}

/* Charts */
.report-charts {
  display: flex;
  flex-direction: column;
  gap: var(--minttu-spacing-lg);
}

.chart-section {
  background: var(--minttu-bg);
  border-radius: var(--minttu-radius);
  padding: var(--minttu-spacing-md);
  page-break-inside: avoid;
}

.chart-section h3 {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-sm);
  margin: 0 0 var(--minttu-spacing-md) 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--minttu-primary);
}

.chart-section h3 i {
  color: var(--minttu-gray);
}

.chart-content {
  background: var(--minttu-white);
  border-radius: var(--minttu-radius-sm);
  padding: var(--minttu-spacing-md);
}

.no-data {
  text-align: center;
  color: var(--minttu-gray);
  padding: var(--minttu-spacing-lg);
}

/* Type Bars */
.type-bars {
  display: flex;
  flex-direction: column;
  gap: var(--minttu-spacing-sm);
}

.type-bar-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.type-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.type-name {
  color: var(--minttu-primary);
}

.type-count {
  font-weight: 600;
  color: var(--minttu-primary);
}

.type-bar-container {
  height: 8px;
  background: var(--minttu-border);
  border-radius: 4px;
  overflow: hidden;
}

.type-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--minttu-primary), rgba(29, 33, 49, 0.7));
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* Hourly Chart */
.hourly-chart {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 150px;
  padding-top: var(--minttu-spacing-sm);
}

.hour-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.hour-bar-fill {
  width: 100%;
  background: var(--minttu-primary);
  border-radius: 2px 2px 0 0;
  min-height: 2px;
  margin-top: auto;
  transition: height 0.3s ease;
}

.hour-label {
  font-size: 9px;
  color: var(--minttu-gray);
  margin-top: 4px;
}

/* Status Grid */
.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--minttu-spacing-md);
}

.status-item {
  display: flex;
  align-items: center;
  gap: var(--minttu-spacing-sm);
  padding: var(--minttu-spacing-sm);
  border-radius: var(--minttu-radius-sm);
}

.status-item.pending {
  background: rgba(245, 158, 11, 0.1);
}

.status-item.review {
  background: rgba(59, 130, 246, 0.1);
}

.status-item.closed {
  background: rgba(34, 197, 94, 0.1);
}

.status-item.false {
  background: rgba(239, 68, 68, 0.1);
}

.status-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-item.pending .status-icon {
  background: rgb(245, 158, 11);
  color: white;
}

.status-item.review .status-icon {
  background: rgb(59, 130, 246);
  color: white;
}

.status-item.closed .status-icon {
  background: rgb(34, 197, 94);
  color: white;
}

.status-item.false .status-icon {
  background: rgb(239, 68, 68);
  color: white;
}

.status-info {
  display: flex;
  flex-direction: column;
}

.status-count {
  font-size: 18px;
  font-weight: 700;
  color: var(--minttu-primary);
  line-height: 1;
}

.status-label {
  font-size: 11px;
  color: var(--minttu-gray);
}

/* Data Table */
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: var(--minttu-spacing-sm) var(--minttu-spacing-md);
  text-align: left;
  border-bottom: 1px solid var(--minttu-border);
}

.data-table th {
  font-size: 11px;
  font-weight: 600;
  color: var(--minttu-gray);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--minttu-bg);
}

.data-table td {
  font-size: 13px;
  color: var(--minttu-primary);
}

.data-table td.rank {
  font-weight: 600;
  color: var(--minttu-gray);
}

.data-table td code {
  font-size: 11px;
  background: var(--minttu-bg);
  padding: 2px 6px;
  border-radius: 4px;
}

.data-table .right {
  text-align: right;
}

/* Footer */
.report-footer {
  margin-top: var(--minttu-spacing-lg);
  padding-top: var(--minttu-spacing-md);
  border-top: 1px solid var(--minttu-border);
  text-align: center;
}

.report-footer p {
  margin: 0;
  font-size: 12px;
  color: var(--minttu-gray);
}

/* Responsive */
@media (max-width: 768px) {
  .report-kpis {
    grid-template-columns: repeat(2, 1fr);
  }

  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .branding {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* Print Styles */
@media print {
  .report-preview {
    padding: 0;
  }

  .chart-section {
    break-inside: avoid;
  }

  .report-kpis {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
