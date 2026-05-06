<template>
  <div class="report-print-container">
    <!-- Loading -->
    <div v-if="loading" class="print-loading">
      <div class="loading-content">
        <div class="spinner"></div>
        <span>Preparando reporte...</span>
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="print-error">
      <i class="pi pi-exclamation-triangle"></i>
      <h3>Error al cargar el reporte</h3>
      <p>{{ error }}</p>
      <button @click="goBack" class="back-btn">Volver a Reportes</button>
    </div>

    <!-- Report Content -->
    <div v-else-if="reportData" class="report-document">
      <!-- ========================================== -->
      <!-- PORTADA -->
      <!-- ========================================== -->
      <section class="page cover-page">
        <div class="cover-content">
          <!-- Header con logo -->
          <div class="cover-header">
            <div class="logo-container">
              <img :src="logoMainWhite" alt="Minttu" class="cover-logo" />
            </div>
            <div class="cover-type-badge">REPORTE DE ANÁLISIS</div>
          </div>
          
          <!-- Título principal -->
          <div class="cover-main">
            <div class="cover-title-wrapper">
              <h1 class="cover-main-title">Informe de</h1>
              <h1 class="cover-main-title highlight">Detecciones</h1>
              <div class="title-underline"></div>
            </div>
            <p class="cover-description">
              Sistema de Monitoreo Inteligente y Análisis de Seguridad
            </p>
          </div>

          <!-- Información del reporte -->
          <div class="cover-info-section">
            <div class="info-grid">
              <div class="info-item">
                <div class="info-icon">
                  <i class="pi pi-building"></i>
                </div>
                <div class="info-content">
                  <span class="info-label">Empresa</span>
                  <span class="info-value">{{ reportData.company_name || 'N/A' }}</span>
                </div>
              </div>

              <div class="info-item">
                <div class="info-icon">
                  <i class="pi pi-calendar"></i>
                </div>
                <div class="info-content">
                  <span class="info-label">Período</span>
                  <span class="info-value">
                    {{ formatDateLong(reportData.summary.date_range.from) }} — 
                    {{ formatDateLong(reportData.summary.date_range.to) }}
                  </span>
                </div>
              </div>

              <div class="info-item">
                <div class="info-icon">
                  <i class="pi pi-chart-bar"></i>
                </div>
                <div class="info-content">
                  <span class="info-label">Analíticas</span>
                  <span class="info-value">
                    <span v-if="reportData.alert_types_selected.length === 0">Todas las analíticas</span>
                    <span v-else>{{ reportData.alert_types_selected.length }} tipo(s) seleccionado(s)</span>
                  </span>
                </div>
              </div>

              <div class="info-item">
                <div class="info-icon">
                  <i class="pi pi-user"></i>
                </div>
                <div class="info-content">
                  <span class="info-label">Generado por</span>
                  <span class="info-value">{{ reportData.created_by_name || reportData.created_by || 'Sistema' }}</span>
                </div>
              </div>
            </div>

            <!-- KPIs destacados -->
            <div class="cover-kpi-highlight">
              <div class="cover-kpi-item">
                <div class="cover-kpi-value">{{ summary.kpis.total.toLocaleString() }}</div>
                <div class="cover-kpi-label">Detecciones Totales</div>
              </div>
              <div class="cover-kpi-divider"></div>
              <div class="cover-kpi-item">
                <div class="cover-kpi-value">{{ summary.kpis.accuracy }}%</div>
                <div class="cover-kpi-label">Precisión del Sistema</div>
              </div>
              <div class="cover-kpi-divider"></div>
              <div class="cover-kpi-item">
                <div class="cover-kpi-value">{{ summary.alerts_by_type.length }}</div>
                <div class="cover-kpi-label">Tipos de Analítica</div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="cover-footer">
            <div class="cover-footer-line"></div>
            <div class="cover-footer-content">
              <div class="footer-left">
                <p class="footer-date">{{ formatDateTime(reportData.summary.generated_at) }}</p>
                <p class="footer-text">Documento generado automáticamente</p>
              </div>
              <div class="footer-right">
                <p class="confidential-badge">CONFIDENCIAL</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ========================================== -->
      <!-- RESUMEN EJECUTIVO -->
      <!-- ========================================== -->
      <section class="page">
        <div class="page-header">
          <img :src="logoSmall" alt="Minttu" class="page-logo" />
          <span class="page-title-small">Reporte de Detecciones</span>
        </div>

        <h2 class="section-title">
          <span class="title-number">01</span>
          Resumen Ejecutivo
        </h2>

        <p class="section-intro">
          Este informe presenta un análisis detallado de las detecciones realizadas por el sistema de 
          monitoreo inteligente durante el período comprendido entre 
          <strong>{{ formatDateLong(reportData.summary.date_range.from) }}</strong> y 
          <strong>{{ formatDateLong(reportData.summary.date_range.to) }}</strong>.
        </p>

        <!-- KPIs Grid -->
        <div class="kpi-grid">
          <div class="kpi-card kpi-total">
            <div class="kpi-icon">
              <i class="pi pi-bell"></i>
            </div>
            <div class="kpi-data">
              <span class="kpi-value">{{ summary.kpis.total.toLocaleString() }}</span>
              <span class="kpi-label">Total Detecciones</span>
            </div>
            <p class="kpi-description">
              Número total de eventos detectados por el sistema durante el período analizado.
            </p>
          </div>

          <div class="kpi-card kpi-pending">
            <div class="kpi-icon">
              <i class="pi pi-clock"></i>
            </div>
            <div class="kpi-data">
              <span class="kpi-value">{{ summary.kpis.pending.toLocaleString() }}</span>
              <span class="kpi-label">Pendientes</span>
            </div>
            <p class="kpi-description">
              Alertas que aún no han sido revisadas por el equipo de seguridad.
            </p>
          </div>

          <div class="kpi-card kpi-closed">
            <div class="kpi-icon">
              <i class="pi pi-check-circle"></i>
            </div>
            <div class="kpi-data">
              <span class="kpi-value">{{ summary.kpis.closed.toLocaleString() }}</span>
              <span class="kpi-label">Cerradas</span>
            </div>
            <p class="kpi-description">
              Alertas verificadas y confirmadas como detecciones correctas.
            </p>
          </div>

          <div class="kpi-card kpi-false">
            <div class="kpi-icon">
              <i class="pi pi-times-circle"></i>
            </div>
            <div class="kpi-data">
              <span class="kpi-value">{{ summary.kpis.false_positives.toLocaleString() }}</span>
              <span class="kpi-label">Falsos Positivos</span>
            </div>
            <p class="kpi-description">
              Detecciones que fueron identificadas como errores del sistema.
            </p>
          </div>
        </div>

        <!-- Accuracy Highlight -->
        <div class="accuracy-box">
          <div class="accuracy-content">
            <div class="accuracy-chart">
              <svg viewBox="0 0 100 100" class="accuracy-ring">
                <circle cx="50" cy="50" r="45" class="ring-bg" />
                <circle 
                  cx="50" cy="50" r="45" 
                  class="ring-progress"
                  :style="{ strokeDasharray: `${summary.kpis.accuracy * 2.83} 283` }"
                />
              </svg>
              <div class="accuracy-value">{{ summary.kpis.accuracy }}%</div>
            </div>
            <div class="accuracy-info">
              <h4>Precisión del Sistema</h4>
              <p>
                La precisión representa el porcentaje de alertas correctas del total. 
                Las alertas correctas son todas aquellas que NO son falsos positivos (incluye nuevas, en revisión y cerradas). 
                Se calcula como: Correctos / Total × 100. 
                Un valor alto indica que el sistema está funcionando de manera efectiva 
                con pocas falsas alarmas.
              </p>
            </div>
          </div>
        </div>

        <div class="page-footer">
          <span>{{ reportData.company_name }}</span>
          <span>Página 2</span>
        </div>
      </section>

      <!-- ========================================== -->
      <!-- DISTRIBUCIÓN POR TIPO -->
      <!-- ========================================== -->
      <section class="page">
        <div class="page-header">
          <img :src="logoSmall" alt="Minttu" class="page-logo" />
          <span class="page-title-small">Reporte de Detecciones</span>
        </div>

        <h2 class="section-title">
          <span class="title-number">02</span>
          Distribución por Tipo de Analítica
        </h2>

        <p class="section-intro">
          A continuación se presenta la distribución de las detecciones según el tipo de analítica 
          configurada en el sistema. Este análisis permite identificar las áreas que requieren mayor 
          atención y optimización.
        </p>

        <div class="chart-container">
          <div class="bar-chart">
            <div 
              v-for="(item, index) in summary.alerts_by_type" 
              :key="item.code"
              class="bar-item"
            >
              <div class="bar-label">
                <span class="bar-rank">{{ index + 1 }}</span>
                <span class="bar-name">{{ item.name }}</span>
              </div>
              <div class="bar-track">
                <div 
                  class="bar-fill" 
                  :style="{ width: getBarWidth(item.count, maxTypeCount) }"
                ></div>
              </div>
              <div class="bar-value">{{ item.count.toLocaleString() }}</div>
              <div class="bar-percent">{{ getPercentage(item.count) }}%</div>
            </div>
          </div>
        </div>

        <!-- Tabla de estados por tipo -->
        <h3 class="subsection-title">Desglose por Estado</h3>
        <p class="table-description">
          Esta tabla muestra el estado de las alertas para cada tipo de analítica, 
          permitiendo identificar patrones y áreas de mejora.
        </p>

        <table class="data-table">
          <thead>
            <tr>
              <th>Tipo de Analítica</th>
              <th class="center">Pendiente</th>
              <th class="center">En Revisión</th>
              <th class="center">Cerrada</th>
              <th class="center">Falso Positivo</th>
              <th class="center">Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="type in summary.alerts_by_type" :key="type.code">
              <td class="type-name">{{ type.name }}</td>
              <td class="center">{{ summary.status_by_type[type.code]?.pending || 0 }}</td>
              <td class="center">{{ summary.status_by_type[type.code]?.in_review || 0 }}</td>
              <td class="center">{{ summary.status_by_type[type.code]?.closed || 0 }}</td>
              <td class="center">{{ summary.status_by_type[type.code]?.false_positive || 0 }}</td>
              <td class="center total">{{ type.count }}</td>
            </tr>
          </tbody>
        </table>

        <div class="page-footer">
          <span>{{ reportData.company_name }}</span>
          <span>Página 3</span>
        </div>
      </section>

      <!-- ========================================== -->
      <!-- DISTRIBUCIÓN TEMPORAL -->
      <!-- ========================================== -->
      <section class="page">
        <div class="page-header">
          <img :src="logoSmall" alt="Minttu" class="page-logo" />
          <span class="page-title-small">Reporte de Detecciones</span>
        </div>

        <h2 class="section-title">
          <span class="title-number">03</span>
          Análisis Temporal
        </h2>

        <p class="section-intro">
          El análisis temporal permite identificar los horarios con mayor actividad, 
          facilitando la optimización de recursos y la planificación de turnos de monitoreo.
        </p>

        <h3 class="subsection-title">Distribución por Hora del Día</h3>
        <p class="chart-description">
          Este gráfico muestra la cantidad de detecciones agrupadas por hora. 
          Las barras más altas indican los horarios con mayor actividad.
        </p>

        <div class="hourly-chart">
          <div class="hourly-bars">
            <div 
              v-for="hour in summary.hourly_distribution" 
              :key="hour.hour"
              class="hourly-bar-container"
            >
              <div 
                class="hourly-bar"
                :style="{ height: getHourBarHeight(hour.count) }"
                :title="`${hour.hour}:00 - ${hour.count} alertas`"
              >
                <span v-if="hour.count > 0" class="hourly-value">{{ hour.count }}</span>
              </div>
              <span class="hourly-label">{{ hour.hour }}</span>
            </div>
          </div>
          <div class="hourly-axis">
            <span>Hora del día (0-23)</span>
          </div>
        </div>

        <!-- Insights -->
        <div class="insights-box">
          <h4><i class="pi pi-lightbulb"></i> Observaciones</h4>
          <ul>
            <li>
              <strong>Hora pico:</strong> {{ peakHour }}:00 con {{ peakHourCount }} detecciones
            </li>
            <li>
              <strong>Hora más tranquila:</strong> {{ quietHour }}:00 con {{ quietHourCount }} detecciones
            </li>
            <li>
              <strong>Promedio por hora:</strong> {{ averagePerHour }} detecciones
            </li>
          </ul>
        </div>

        <div class="page-footer">
          <span>{{ reportData.company_name }}</span>
          <span>Página 4</span>
        </div>
      </section>

      <!-- ========================================== -->
      <!-- TOP CÁMARAS -->
      <!-- ========================================== -->
      <section class="page" v-if="summary.alerts_by_camera.length > 0">
        <div class="page-header">
          <img :src="logoSmall" alt="Minttu" class="page-logo" />
          <span class="page-title-small">Reporte de Detecciones</span>
        </div>

        <h2 class="section-title">
          <span class="title-number">04</span>
          Análisis por Cámara
        </h2>

        <p class="section-intro">
          Este análisis identifica las cámaras con mayor cantidad de detecciones, 
          lo cual puede indicar zonas de alto riesgo o áreas que requieren atención especial.
        </p>

        <h3 class="subsection-title">Top 10 Cámaras con Mayor Actividad</h3>

        <table class="data-table camera-table">
          <thead>
            <tr>
              <th class="rank-col">#</th>
              <th>Cámara</th>
              <th>Código</th>
              <th class="center">Detecciones</th>
              <th class="center">% del Total</th>
              <th>Indicador</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(camera, index) in summary.alerts_by_camera" :key="camera.code">
              <td class="rank-col">
                <span :class="['rank-badge', `rank-${index + 1}`]">{{ index + 1 }}</span>
              </td>
              <td class="camera-name">{{ camera.name }}</td>
              <td class="camera-code">{{ camera.code }}</td>
              <td class="center">{{ camera.count.toLocaleString() }}</td>
              <td class="center">{{ getPercentage(camera.count) }}%</td>
              <td>
                <div class="mini-bar">
                  <div 
                    class="mini-bar-fill"
                    :style="{ width: getBarWidth(camera.count, maxCameraCount) }"
                  ></div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="insights-box">
          <h4><i class="pi pi-info-circle"></i> Interpretación</h4>
          <p>
            Las cámaras con mayor cantidad de detecciones pueden indicar zonas con mayor 
            tráfico de personas, áreas de mayor riesgo, o puntos donde el sistema detecta 
            más incumplimientos. Se recomienda revisar estas ubicaciones para determinar 
            si requieren medidas adicionales de seguridad o señalización.
          </p>
        </div>

        <div class="page-footer">
          <span>{{ reportData.company_name }}</span>
          <span>Página 5</span>
        </div>
      </section>

      <!-- ========================================== -->
      <!-- PÁGINA FINAL -->
      <!-- ========================================== -->
      <section class="page final-page">
        <div class="page-header">
          <img :src="logoSmall" alt="Minttu" class="page-logo" />
          <span class="page-title-small">Reporte de Detecciones</span>
        </div>

        <h2 class="section-title">
          <span class="title-number">05</span>
          Conclusiones y Recomendaciones
        </h2>

        <div class="conclusion-content">
          <div class="summary-stats">
            <h4>Resumen del Período</h4>
            <div class="stat-row">
              <span class="stat-label">Total de detecciones analizadas</span>
              <span class="stat-value">{{ summary.kpis.total.toLocaleString() }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Tasa de revisión</span>
              <span class="stat-value">{{ reviewRate }}%</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Precisión del sistema</span>
              <span class="stat-value">{{ summary.kpis.accuracy }}%</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Tipos de analítica monitoreados</span>
              <span class="stat-value">{{ summary.alerts_by_type.length }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Cámaras con actividad</span>
              <span class="stat-value">{{ summary.alerts_by_camera.length }}</span>
            </div>
          </div>

          <div class="recommendations">
            <h4>Recomendaciones</h4>
            <ol>
              <li v-if="summary.kpis.pending > 0">
                <strong>Revisar alertas pendientes:</strong> Existen {{ summary.kpis.pending }} 
                alertas sin revisar. Se recomienda procesarlas para mantener el sistema actualizado.
              </li>
              <li v-if="summary.kpis.accuracy < 80">
                <strong>Optimizar precisión:</strong> La precisión actual es {{ summary.kpis.accuracy }}%. 
                Considere ajustar los parámetros de detección para reducir falsos positivos.
              </li>
              <li v-if="peakHourCount > averagePerHour * 2">
                <strong>Reforzar monitoreo en horas pico:</strong> Se detectó alta actividad 
                alrededor de las {{ peakHour }}:00. Considere asignar más recursos en este horario.
              </li>
              <li>
                <strong>Mantener seguimiento:</strong> Continúe monitoreando las tendencias 
                para identificar patrones y mejorar la seguridad de manera proactiva.
              </li>
            </ol>
          </div>
        </div>

        <div class="report-signature">
          <p>Este reporte fue generado automáticamente por el sistema Minttu Dashboard.</p>
          <p>Para consultas, contacte al administrador del sistema.</p>
        </div>

        <div class="final-footer">
          <img :src="logoMain" alt="Minttu" class="footer-logo" />
          <p>© {{ currentYear }} Minttu. Todos los derechos reservados.</p>
          <p class="footer-small">Documento generado el {{ formatDateTime(reportData.summary.generated_at) }}</p>
        </div>
      </section>
    </div>

    <!-- Print Button (only on screen) -->
    <div class="print-actions" v-if="!loading && !error && reportData">
      <button @click="printReport" class="action-btn print-btn">
        <i class="pi pi-file-pdf"></i>
        Guardar PDF
      </button>
      <button @click="goBack" class="action-btn back-btn">
        <i class="pi pi-arrow-left"></i>
        Volver
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchReportSummary, type ReportSummaryResponse, type ReportSummary } from "@/services/reports";
import logoDark from "@/assets/brand/logo_dark.svg";
import logoMain from "@/assets/brand/logo_main.svg";
import logoMainWhite from "@/assets/brand/logo_dark.svg";
import logoSmall from "@/assets/brand/ico_dark.svg";

const route = useRoute();
const router = useRouter();

// ============================================
// STATE
// ============================================
const loading = ref(true);
const error = ref<string | null>(null);
const reportData = ref<ReportSummaryResponse | null>(null);

// ============================================
// COMPUTED
// ============================================
const summary = computed<ReportSummary>(() => {
  return reportData.value?.summary || {
    date_range: { from: "", to: "" },
    kpis: { total: 0, pending: 0, in_review: 0, closed: 0, false_positives: 0, accuracy: 0 },
    alerts_by_type: [],
    alerts_by_camera: [],
    alerts_by_status: { pending: 0, in_review: 0, closed: 0, false_positive: 0 },
    status_by_type: {},
    hourly_distribution: [],
    generated_at: "",
  };
});

const maxTypeCount = computed(() => {
  if (!summary.value.alerts_by_type.length) return 1;
  return Math.max(...summary.value.alerts_by_type.map((t) => t.count), 1);
});

const maxCameraCount = computed(() => {
  if (!summary.value.alerts_by_camera.length) return 1;
  return Math.max(...summary.value.alerts_by_camera.map((c) => c.count), 1);
});

const maxHourCount = computed(() => {
  if (!summary.value.hourly_distribution.length) return 1;
  return Math.max(...summary.value.hourly_distribution.map((h) => h.count), 1);
});

const peakHour = computed(() => {
  const hourly = summary.value.hourly_distribution;
  if (!hourly.length) return 0;
  const max = Math.max(...hourly.map((h) => h.count));
  const peak = hourly.find((h) => h.count === max);
  return peak?.hour || 0;
});

const peakHourCount = computed(() => {
  const hourly = summary.value.hourly_distribution;
  if (!hourly.length) return 0;
  return Math.max(...hourly.map((h) => h.count));
});

const quietHour = computed(() => {
  const hourly = summary.value.hourly_distribution;
  if (!hourly.length) return 0;
  const min = Math.min(...hourly.map((h) => h.count));
  const quiet = hourly.find((h) => h.count === min);
  return quiet?.hour || 0;
});

const quietHourCount = computed(() => {
  const hourly = summary.value.hourly_distribution;
  if (!hourly.length) return 0;
  return Math.min(...hourly.map((h) => h.count));
});

const averagePerHour = computed(() => {
  const total = summary.value.kpis.total;
  return Math.round(total / 24);
});

const reviewRate = computed(() => {
  const total = summary.value.kpis.total;
  const reviewed = summary.value.kpis.closed + summary.value.kpis.false_positives;
  if (total === 0) return 0;
  return Math.round((reviewed / total) * 100);
});

const currentYear = computed(() => new Date().getFullYear());

// ============================================
// METHODS
// ============================================
function formatDateLong(dateString: string): string {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

function formatDateTime(dateString: string): string {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("es-CL", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getBarWidth(count: number, max: number): string {
  const percentage = (count / max) * 100;
  return `${Math.max(percentage, 2)}%`;
}

function getHourBarHeight(count: number): string {
  if (maxHourCount.value === 0) return "2%";
  const percentage = (count / maxHourCount.value) * 100;
  return `${Math.max(percentage, 2)}%`;
}

function getPercentage(count: number): string {
  const total = summary.value.kpis.total || 1;
  return ((count / total) * 100).toFixed(1);
}

function printReport() {
  window.print();
}

function goBack() {
  router.back();
}

async function loadReport() {
  const reportId = route.query.id;

  if (!reportId) {
    error.value = "No se especificó el ID del reporte";
    loading.value = false;
    return;
  }

  try {
    reportData.value = await fetchReportSummary(Number(reportId));
  } catch (err: any) {
    console.error("Error loading report:", err);
    error.value = err.response?.data?.detail || "Error al cargar el reporte";
  } finally {
    loading.value = false;
  }
}

// ============================================
// LIFECYCLE
// ============================================
onMounted(() => {
  loadReport();
});
</script>

<style scoped>
/* ============================================
   VARIABLES & BASE
   ============================================ */
.report-print-container {
  --report-primary: var(--minttu-primary);
  --report-secondary: #6b7280;
  --report-accent: #3b82f6;
  --report-success: #22c55e;
  --report-warning: #f59e0b;
  --report-danger: #ef4444;
  --report-bg: #f9fafb;
  --report-border: #e5e7eb;
  
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--report-primary);
  background: #e5e7eb;
  min-height: 100vh;
}

/* ============================================
   LOADING & ERROR
   ============================================ */
.print-loading,
.print-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 16px;
  color: var(--report-secondary);
  background: white;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--report-border);
  border-top-color: var(--report-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.print-error i {
  font-size: 64px;
  color: var(--report-danger);
}

.print-error h3 {
  margin: 0;
  font-size: 24px;
  color: var(--report-primary);
}

.back-btn {
  margin-top: 16px;
  padding: 12px 32px;
  background: var(--report-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

/* ============================================
   DOCUMENT & PAGES
   ============================================ */
.report-document {
  max-width: 8.5in;
  margin: 0 auto;
  background: white;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
}

.page {
  width: 8.5in;
  height: 11in;
  padding: 0.6in 0.5in;
  background: white;
  position: relative;
  page-break-after: always;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.page:last-child {
  page-break-after: auto;
}

/* ============================================
   COVER PAGE - MODERN DESIGN
   ============================================ */
.cover-page {
  background: linear-gradient(135deg, var(--minttu-primary) 0%, #2d3349 100%);
  color: white;
  position: relative;
  overflow: hidden;
}

.cover-page::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.03) 0%, transparent 70%);
  border-radius: 50%;
}

.cover-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

/* Header */
.cover-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 40px;
}

.logo-container {
  /* Sin fondo, solo el logo */
}

.cover-logo {
  height: 56px;
  filter: brightness(0) invert(1);
}

.cover-type-badge {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

/* Main Title */
.cover-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px 0;
}

.cover-title-wrapper {
  margin-bottom: 20px;
}

.cover-main-title {
  font-size: 52px;
  font-weight: 800;
  margin: 0;
  line-height: 1.1;
  letter-spacing: -1px;
}

.cover-main-title.highlight {
  background: linear-gradient(90deg, #ffffff 0%, rgba(255, 255, 255, 0.7) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-underline {
  width: 120px;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6 0%, transparent 100%);
  margin-top: 16px;
  border-radius: 2px;
}

.cover-description {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  font-weight: 400;
  letter-spacing: 0.3px;
}

/* Info Section */
.cover-info-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(10px);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.info-icon {
  width: 36px;
  height: 36px;
  background: rgba(59, 130, 246, 0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
  font-size: 16px;
  flex-shrink: 0;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.info-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.info-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 500;
  line-height: 1.4;
}

/* KPI Highlight */
.cover-kpi-highlight {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.cover-kpi-item {
  text-align: center;
}

.cover-kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: white;
  line-height: 1;
  margin-bottom: 8px;
}

.cover-kpi-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.cover-kpi-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.15);
}

/* Footer */
.cover-footer {
  margin-top: auto;
  padding-top: 24px;
}

.cover-footer-line {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.2) 50%, transparent 100%);
  margin-bottom: 16px;
}

.cover-footer-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.footer-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.footer-date {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  font-weight: 500;
}

.footer-text {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
}

.footer-right {
  display: flex;
  align-items: center;
}

.confidential-badge {
  padding: 6px 16px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #fca5a5;
  margin: 0;
}

/* ============================================
   PAGE HEADER & FOOTER
   ============================================ */
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--report-border);
}

.page-logo {
  height: 24px;
}

.page-title-small {
  font-size: 12px;
  color: var(--report-secondary);
  font-weight: 500;
}

.page-footer {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--report-secondary);
  padding-top: 16px;
  border-top: 1px solid var(--report-border);
}

/* ============================================
   SECTION TITLES
   ============================================ */
.section-title {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 16px 0;
  color: var(--report-primary);
}

.title-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--report-primary);
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}

.section-intro {
  font-size: 14px;
  line-height: 1.7;
  color: var(--report-secondary);
  margin: 0 0 24px 0;
}

.subsection-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--report-primary);
  margin: 32px 0 8px 0;
}

/* ============================================
   KPI CARDS
   ============================================ */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  background: var(--report-bg);
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid var(--report-border);
}

.kpi-total { border-left-color: var(--report-primary); }
.kpi-pending { border-left-color: var(--report-warning); }
.kpi-closed { border-left-color: var(--report-success); }
.kpi-false { border-left-color: var(--report-danger); }

.kpi-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.kpi-total .kpi-icon { background: var(--report-primary); color: white; }
.kpi-pending .kpi-icon { background: var(--report-warning); color: white; }
.kpi-closed .kpi-icon { background: var(--report-success); color: white; }
.kpi-false .kpi-icon { background: var(--report-danger); color: white; }

.kpi-data {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--report-primary);
  line-height: 1;
}

.kpi-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--report-secondary);
}

.kpi-description {
  font-size: 12px;
  color: var(--report-secondary);
  line-height: 1.5;
  margin: 0;
}

/* ============================================
   ACCURACY BOX
   ============================================ */
.accuracy-box {
  background: linear-gradient(135deg, var(--minttu-primary) 0%, #2d3349 100%);
  border-radius: 12px;
  padding: 24px;
  color: white;
}

.accuracy-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.accuracy-chart {
  position: relative;
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}

.accuracy-ring {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.2);
  stroke-width: 8;
}

.ring-progress {
  fill: none;
  stroke: var(--report-success);
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s ease;
}

.accuracy-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
  font-weight: 700;
}

.accuracy-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.accuracy-info p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  opacity: 0.8;
}

/* ============================================
   BAR CHART
   ============================================ */
.chart-container {
  margin: 24px 0;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-item {
  display: grid;
  grid-template-columns: 180px 1fr 80px 60px;
  align-items: center;
  gap: 12px;
}

.bar-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bar-rank {
  width: 24px;
  height: 24px;
  background: var(--report-bg);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--report-secondary);
}

.bar-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-track {
  height: 24px;
  background: var(--report-bg);
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--report-primary), #4b5563);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.bar-value {
  font-size: 14px;
  font-weight: 600;
  text-align: right;
}

.bar-percent {
  font-size: 12px;
  color: var(--report-secondary);
  text-align: right;
}

/* ============================================
   DATA TABLES
   ============================================ */
.table-description {
  font-size: 13px;
  color: var(--report-secondary);
  margin: 8px 0 16px 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.data-table th {
  padding: 12px 10px;
  text-align: left;
  font-weight: 600;
  color: var(--report-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--report-bg);
  border-bottom: 2px solid var(--report-border);
}

.data-table td {
  padding: 12px 10px;
  border-bottom: 1px solid var(--report-border);
}

.data-table .center {
  text-align: center;
}

.data-table .total {
  font-weight: 600;
  background: var(--report-bg);
}

.data-table .type-name {
  font-weight: 500;
}

.camera-table .rank-col {
  width: 50px;
  text-align: center;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 11px;
}

.rank-1 { background: #fef3c7; color: #92400e; }
.rank-2 { background: #e5e7eb; color: #374151; }
.rank-3 { background: #fed7aa; color: #9a3412; }
.rank-badge:not(.rank-1):not(.rank-2):not(.rank-3) { 
  background: var(--report-bg); 
  color: var(--report-secondary); 
}

.camera-name {
  font-weight: 500;
}

.camera-code {
  font-family: monospace;
  font-size: 11px;
  color: var(--report-secondary);
}

.mini-bar {
  height: 8px;
  background: var(--report-bg);
  border-radius: 4px;
  overflow: hidden;
}

.mini-bar-fill {
  height: 100%;
  background: var(--report-primary);
  border-radius: 4px;
}

/* ============================================
   HOURLY CHART
   ============================================ */
.hourly-chart {
  margin: 24px 0;
}

.hourly-bars {
  display: flex;
  align-items: flex-end;
  height: 200px;
  gap: 4px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--report-border);
}

.hourly-bar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.hourly-bar {
  width: 100%;
  background: linear-gradient(180deg, var(--report-primary), #4b5563);
  border-radius: 4px 4px 0 0;
  margin-top: auto;
  min-height: 2px;
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.hourly-value {
  font-size: 9px;
  font-weight: 600;
  color: white;
  padding-top: 4px;
}

.hourly-label {
  font-size: 10px;
  color: var(--report-secondary);
  margin-top: 4px;
}

.hourly-axis {
  text-align: center;
  font-size: 11px;
  color: var(--report-secondary);
  margin-top: 8px;
}

/* ============================================
   INSIGHTS BOX
   ============================================ */
.insights-box {
  background: var(--report-bg);
  border-radius: 12px;
  padding: 20px;
  margin-top: 24px;
}

.insights-box h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--report-primary);
}

.insights-box ul {
  margin: 0;
  padding-left: 20px;
}

.insights-box li {
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.insights-box p {
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  color: var(--report-secondary);
}

/* ============================================
   FINAL PAGE
   ============================================ */
.conclusion-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

.summary-stats,
.recommendations {
  background: var(--report-bg);
  border-radius: 12px;
  padding: 20px;
}

.summary-stats h4,
.recommendations h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: var(--report-primary);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--report-border);
  font-size: 13px;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  color: var(--report-secondary);
}

.stat-value {
  font-weight: 600;
}

.recommendations ol {
  margin: 0;
  padding-left: 20px;
}

.recommendations li {
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 12px;
}

.report-signature {
  text-align: center;
  padding: 24px;
  border: 1px dashed var(--report-border);
  border-radius: 12px;
  margin-bottom: 40px;
}

.report-signature p {
  margin: 4px 0;
  font-size: 13px;
  color: var(--report-secondary);
}

.final-footer {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid var(--report-border);
}

.footer-logo {
  height: 32px;
  margin-bottom: 12px;
}

.final-footer p {
  margin: 4px 0;
  font-size: 12px;
  color: var(--report-secondary);
}

.footer-small {
  font-size: 11px !important;
}

/* ============================================
   PRINT ACTIONS (screen only)
   ============================================ */
.print-actions {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  gap: 12px;
  z-index: 1000;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.print-btn {
  background: var(--report-primary);
  color: white;
}

.print-btn:hover {
  background: #2d3349;
}

.action-btn.back-btn {
  background: white;
  color: var(--report-primary);
  border: 1px solid var(--report-border);
}

.action-btn.back-btn:hover {
  background: var(--report-bg);
}

/* ============================================
   PRINT STYLES
   ============================================ */
@media print {
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  html, body {
    width: 8.5in;
    height: 11in;
    margin: 0;
    padding: 0;
  }

  .report-print-container {
    background: white;
    width: 100%;
    height: auto;
  }

  .report-document {
    box-shadow: none;
    max-width: 100%;
    width: 100%;
  }

  .page {
    width: 100%;
    height: 100vh;
    min-height: 11in;
    padding: 0.5in 0.4in;
    margin: 0;
    page-break-after: always;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .page:last-child {
    page-break-after: auto;
  }

  .print-actions {
    display: none !important;
  }

  .page-footer {
    margin-top: auto !important;
    padding-top: 12px;
  }

  @page {
    size: letter portrait;
    margin: 0;
  }

  /* Evitar cortes de página en elementos importantes */
  .kpi-card,
  .kpi-grid,
  .accuracy-box,
  .accuracy-content,
  .bar-item,
  .bar-chart,
  .chart-container,
  .insights-box,
  .data-table,
  .hourly-chart,
  .summary-stats,
  .recommendations,
  .conclusion-content,
  .report-signature,
  .cover-info-box,
  .cover-title-section,
  tr {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
  }

  /* Forzar nueva página antes de secciones */
  .section-title {
    page-break-after: avoid;
    break-after: avoid;
  }

  /* Ajustar tamaños para impresión */
  .cover-title {
    font-size: 36px;
  }

  .section-title {
    font-size: 20px;
  }

  .kpi-value {
    font-size: 26px;
  }

  .data-table {
    font-size: 10px;
  }

  .data-table th,
  .data-table td {
    padding: 6px 4px;
  }

  .bar-item {
    margin-bottom: 6px;
  }

  .bar-name {
    font-size: 11px;
  }

  .hourly-bars {
    height: 150px;
  }

  .accuracy-chart {
    width: 80px;
    height: 80px;
  }

  .accuracy-value {
    font-size: 20px;
  }

  /* Portada ajustada */
  .cover-page {
    height: 100%;
  }

  .cover-content {
    height: 100%;
  }

  .cover-main-title {
    font-size: 44px;
  }

  .cover-description {
    font-size: 14px;
  }

  .info-grid {
    gap: 16px;
  }

  .cover-kpi-value {
    font-size: 28px;
  }

  .cover-kpi-label {
    font-size: 10px;
  }

  .cover-info-section {
    padding: 20px;
  }

  .cover-footer {
    padding-top: 20px;
  }

  /* Secciones internas */
  .section-intro {
    font-size: 12px;
    margin-bottom: 16px;
  }

  .kpi-card {
    padding: 12px;
  }

  .kpi-description {
    font-size: 10px;
  }

  .insights-box {
    padding: 12px;
    margin-top: 16px;
  }

  .insights-box h4 {
    font-size: 12px;
  }

  .insights-box li,
  .insights-box p {
    font-size: 11px;
  }
}

/* ============================================
   SCREEN RESPONSIVE
   ============================================ */
@media screen and (max-width: 900px) {
  .report-document {
    max-width: 100%;
  }

  .page {
    width: auto;
    min-height: auto;
    padding: 24px;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .bar-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .bar-label {
    order: 1;
  }

  .bar-track {
    order: 3;
  }

  .bar-value,
  .bar-percent {
    order: 2;
  }

  .conclusion-content {
    grid-template-columns: 1fr;
  }

  .accuracy-content {
    flex-direction: column;
    text-align: center;
  }

  .print-actions {
    bottom: 16px;
    right: 16px;
    left: 16px;
    justify-content: center;
  }
}

/* Reset estilos para impresión - sobrescribir responsive */
@media print {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr) !important;
  }

  .bar-item {
    grid-template-columns: 160px 1fr 70px 50px !important;
    gap: 8px !important;
  }

  .bar-label,
  .bar-track,
  .bar-value,
  .bar-percent {
    order: unset !important;
  }

  .conclusion-content {
    grid-template-columns: 1fr 1fr !important;
  }

  .accuracy-content {
    flex-direction: row !important;
    text-align: left !important;
  }
}
</style>
