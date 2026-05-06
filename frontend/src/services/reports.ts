import { api } from "@/lib/api";
import { generateReportFilename } from "./pdfGenerator";

// ============================================
// TYPES
// ============================================

export interface ReportParams {
  date_from: string;
  date_to: string;
  alert_types: string[];
  summary?: ReportSummary;
}

export interface Report {
  id: number;
  status: "PENDING" | "READY" | "FAILED";
  format: "PDF" | "CSV";
  params: ReportParams;
  file_url: string | null;
  error_message: string | null;
  created_at: string;
  created_by: number;
  created_by_name: string;
}

export interface ReportKPIs {
  total: number;
  pending: number;
  in_review: number;
  closed: number;
  false_positives: number;
  accuracy: number;
}

export interface AlertByType {
  code: string;
  name: string;
  count: number;
}

export interface AlertByCamera {
  code: string;
  name: string;
  count: number;
}

export interface AlertsByStatus {
  pending: number;
  in_review: number;
  closed: number;
  false_positive: number;
}

export interface StatusByType {
  [typeCode: string]: {
    pending: number;
    in_review: number;
    closed: number;
    false_positive: number;
  };
}

export interface HourlyData {
  hour: number;
  count: number;
}

export interface ReportSummary {
  date_range: {
    from: string;
    to: string;
  };
  kpis: ReportKPIs;
  alerts_by_type: AlertByType[];
  alerts_by_camera: AlertByCamera[];
  alerts_by_status: AlertsByStatus;
  status_by_type: StatusByType;
  hourly_distribution: HourlyData[];
  generated_at: string;
}

export interface ReportCreateData {
  date_from: string;
  date_to: string;
  alert_types: string[];
  format?: "PDF" | "CSV";
}

export interface ReportsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Report[];
}

export interface ReportCreateResponse {
  id: number;
  status: string;
  message: string;
  summary: ReportSummary;
}

export interface AlertTypeSelected {
  code: string;
  name: string;
}

export interface ReportSummaryResponse {
  id: number;
  format: string;
  created_at: string;
  created_by: string | null;
  created_by_name: string | null;
  company_name: string | null;
  alert_types_selected: AlertTypeSelected[];
  summary: ReportSummary;
}

// ============================================
// API FUNCTIONS
// ============================================

export async function fetchReports(page: number = 1, pageSize: number = 25): Promise<ReportsResponse> {
  const { data } = await api.get<ReportsResponse>("/api/reports/", {
    params: { page, page_size: pageSize },
  });
  return data;
}

export async function createReport(reportData: ReportCreateData): Promise<ReportCreateResponse> {
  const { data } = await api.post<ReportCreateResponse>("/api/reports/create/", reportData);
  return data;
}

export async function fetchReportDetail(id: number): Promise<Report> {
  const { data } = await api.get<Report>(`/api/reports/${id}/`);
  return data;
}

export async function fetchReportSummary(id: number): Promise<ReportSummaryResponse> {
  const { data } = await api.get<ReportSummaryResponse>(`/api/reports/${id}/summary/`);
  return data;
}

export function getCSVDownloadUrl(id: number): string {
  return `/api/reports/${id}/download-csv/`;
}

export async function downloadReportCSV(id: number): Promise<void> {
  try {
    console.log(`[CSV] Iniciando descarga para reporte ${id}`);
    
    // Primero obtener el summary para generar el nombre del archivo
    const reportData = await fetchReportSummary(id);
    const filename = generateReportFilename(reportData, "csv");
    console.log(`[CSV] Nombre de archivo generado: ${filename}`);
    
    // Usar axios para obtener el CSV con el token correcto
    const response = await api.get(getCSVDownloadUrl(id), {
      responseType: 'blob',
      validateStatus: (status) => status < 500, // No lanzar error para 4xx
    });
    
    // Verificar si la respuesta es un error JSON en lugar de un CSV
    if (response.status >= 400) {
      // Intentar leer el blob como texto para obtener el mensaje de error
      const text = await response.data.text();
      console.error(`[CSV] Error del servidor (${response.status}):`, text);
      try {
        const errorData = JSON.parse(text);
        throw new Error(errorData.detail || `Error ${response.status}`);
      } catch {
        throw new Error(`Error del servidor: ${response.status}`);
      }
    }
    
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
    
    console.log(`[CSV] Descarga completada: ${filename}`);
  } catch (error) {
    console.error("[CSV] Error downloading CSV:", error);
    throw error instanceof Error ? error : new Error("Error al descargar el CSV");
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

export function getStatusLabel(status: string): string {
  switch (status) {
    case "PENDING":
      return "Pendiente";
    case "READY":
      return "Listo";
    case "FAILED":
      return "Error";
    default:
      return status;
  }
}

export function getStatusClass(status: string): string {
  switch (status) {
    case "PENDING":
      return "status-pending";
    case "READY":
      return "status-ready";
    case "FAILED":
      return "status-failed";
    default:
      return "";
  }
}

export function formatDateRange(from: string, to: string): string {
  const fromDate = new Date(from);
  const toDate = new Date(to);
  
  const formatDate = (date: Date) => {
    return date.toLocaleDateString("es-CL", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };
  
  return `${formatDate(fromDate)} - ${formatDate(toDate)}`;
}
