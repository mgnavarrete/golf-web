import { api } from "@/lib/api";

// ============================================
// TYPES
// ============================================

export type TimePeriod = "day" | "week" | "month";

export interface AlertByType {
  type_code: string;
  type_name: string;
  count: number;
}

export interface AlertByCamera {
  camera_code: string;
  camera_name: string;
  count: number;
}

export interface TimeChartData {
  label: string;
  value: number;
}

export interface LatestAlert {
  id: number;
  alert_type: string;
  alert_type_name: string;
  camera: string;
  camera_name: string;
  detected_at: string;
  confidence: number | null;
  status: string;
  snapshot_url: string | null;
}

export interface CameraStatus {
  id: number;
  code: string;
  name: string;
  location_name: string | null;
  latitude: number | null;
  longitude: number | null;
  status: string;
  last_seen_at: string | null;
}

export interface KPIs {
  total: number;
  pending: number;
  closed: number;
  false_positives: number;
  accuracy: number;
}

export interface HourlyDistribution {
  hour: number;
  label: string;
  value: number;
}

export interface StatusComparison {
  status: string;
  count: number;
  color: string;
}

export interface HeatmapData {
  day: string;
  day_index: number;
  hour: number;
  value: number;
}

export interface DashboardStats {
  period: TimePeriod;
  date_range: {
    from: string;
    to: string;
  };
  kpis: KPIs;
  // Compatibilidad con HomeView (estructura antigua)
  total_alerts?: number;
  alerts_by_type: AlertByType[];
  alerts_by_camera: AlertByCamera[];  // Nuevo: distribución por cámara
  time_chart_data: TimeChartData[];
  hourly_distribution: HourlyDistribution[];
  status_comparison: StatusComparison[];
  heatmap_data: HeatmapData[];
  latest_alerts: LatestAlert[];
  cameras: CameraStatus[];
}

export interface DashboardFilters {
  period?: TimePeriod;
  date_from?: string;
  date_to?: string;
  alert_types?: string[];
}

// ============================================
// API FUNCTIONS
// ============================================

export async function fetchDashboardStats(
  filtersOrPeriod: DashboardFilters | TimePeriod = {}
): Promise<DashboardStats> {
  // Compatibilidad: si se pasa un TimePeriod (string), convertirlo a DashboardFilters
  let filters: DashboardFilters;
  if (typeof filtersOrPeriod === "string") {
    filters = { period: filtersOrPeriod };
  } else {
    filters = filtersOrPeriod;
  }
  
  // Construir URL manualmente para asegurar que los arrays se envíen correctamente
  // Django espera: alert_types=CODE1&alert_types=CODE2 (sin corchetes)
  const baseURL = api.defaults.baseURL || "https://api.minttu.app";
  const url = new URL("/api/dashboard/stats/", baseURL);
  
  if (filters.period) {
    url.searchParams.append("period", filters.period);
  }
  if (filters.date_from) {
    url.searchParams.append("date_from", filters.date_from);
  }
  if (filters.date_to) {
    url.searchParams.append("date_to", filters.date_to);
  }
  
  // Agregar cada tipo de alerta como un parámetro separado
  // Esto genera: alert_types=CODE1&alert_types=CODE2 (formato que Django espera)
  if (filters.alert_types && filters.alert_types.length > 0) {
    filters.alert_types.forEach((type) => {
      url.searchParams.append("alert_types", type);
    });
    console.log("[DASHBOARD] Enviando tipos de alerta:", filters.alert_types);
    console.log("[DASHBOARD] URL completa:", url.pathname + url.search);
  }
  
  const { data } = await api.get<DashboardStats>(url.pathname + url.search);
  return data;
}
