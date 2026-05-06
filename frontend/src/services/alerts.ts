import { api } from "@/lib/api";

// ============================================
// TYPES
// ============================================

export interface Alert {
  id: number;
  alert_type: string;
  alert_type_name: string;
  camera: string;
  camera_name: string;
  detected_at: string;
  received_at: string;
  confidence: number | null;
  status: string;
  metadata: any;
  snapshot_path: string | null;
  snapshot_url: string | null;
  notes?: string | null;
  comments?: string | null;
  last_modified_by?: number | null;
  last_modified_by_name?: string | null;
  updated_at?: string;
}

export interface UpdateAlertData {
  status?: string;
  comments?: string;
}

export interface AlertFilters {
  search?: string;
  type?: string;
  camera?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
  confidenceMin?: number;
  ordering?: string;
}

export interface AlertsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Alert[];
}

export interface AlertType {
  code: string;
  name: string;
}

export interface Camera {
  code: string;
  name: string;
}

// ============================================
// API FUNCTIONS
// ============================================

export async function fetchAlerts(
  page: number = 1,
  filters: AlertFilters = {},
  pageSize: number = 20
): Promise<AlertsResponse> {
  const params: any = {
    page,
    page_size: pageSize,
  };

  // Agregar filtros solo si tienen valor
  if (filters.search) params.search = filters.search;
  if (filters.type) params.type = filters.type;
  if (filters.camera) params.camera = filters.camera;
  if (filters.status) params.status = filters.status;
  if (filters.dateFrom) params.from = filters.dateFrom;
  if (filters.dateTo) params.to = filters.dateTo;
  if (filters.confidenceMin !== undefined && filters.confidenceMin !== null) {
    params.confidenceMin = filters.confidenceMin;
  }
  if (filters.ordering) params.ordering = filters.ordering;

  const { data } = await api.get<AlertsResponse>("/api/alerts/", { params });
  return data;
}

export async function fetchAlertTypes(): Promise<AlertType[]> {
  const { data } = await api.get<AlertType[]>("/api/alert-types/");
  return data;
}

export async function fetchCameras(): Promise<Camera[]> {
  const { data } = await api.get<Camera[]>("/api/cameras/");
  return data;
}

export async function fetchAlertDetail(id: number): Promise<Alert> {
  const { data } = await api.get<Alert>(`/api/alerts/${id}/`);
  return data;
}

export async function updateAlert(id: number, updateData: UpdateAlertData): Promise<Alert> {
  const { data } = await api.patch<Alert>(`/api/alerts/${id}/`, updateData);
  return data;
}
