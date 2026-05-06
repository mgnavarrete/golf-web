import { api } from "@/lib/api";

export type PaymentMethod = "CASH" | "CARD" | "TRANSFER" | "OTHER";

export interface AppPermissions {
  can_view_dashboard: boolean;
  can_manage_course_entries: boolean;
  can_manage_range_orders: boolean;
  can_view_reports: boolean;
  can_export_excel: boolean;
  can_close_day: boolean;
  can_manage_users: boolean;
  can_edit_course_entries: boolean;
  can_delete_course_entries: boolean;
  can_edit_range_orders: boolean;
  can_delete_range_orders: boolean;
  can_reopen_closure: boolean;
  can_patch_settings: boolean;
}

export interface CourseEntry {
  id: number;
  customer_name: string;
  people_count: number;
  amount_clp: number;
  payment_method: PaymentMethod;
  notes: string;
  created_by: number;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface RangeOrder {
  id: number;
  customer_name: string;
  baskets_count: number;
  unit_price_clp: number;
  total_amount_clp: number;
  payment_method: PaymentMethod;
  notes: string;
  created_by: number;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface DailySummary {
  operational_date: string;
  total_course_clp: number;
  total_range_clp: number;
  total_general_clp: number;
  total_people: number;
  total_course_records: number;
  total_range_orders: number;
  total_baskets: number;
  total_cash_clp: number;
  total_card_clp: number;
  total_transfer_clp: number;
  total_other_clp: number;
  latest_course_entries: CourseEntry[];
  latest_range_orders: RangeOrder[];
}

export interface CashClosure {
  id: number;
  operational_date: string;
  scope: "COURSE" | "RANGE" | "FINAL";
  status: "CLOSED" | "REOPENED";
  total_course_clp: number;
  total_range_clp: number;
  total_general_clp: number;
  total_cash_clp: number;
  total_card_clp: number;
  total_transfer_clp: number;
  total_other_clp: number;
  total_people: number;
  total_course_records: number;
  total_range_orders: number;
  total_baskets: number;
  adjustment_clp: number;
  notes: string;
  closed_by_name: string;
  closed_at: string;
  reopened_by_name?: string | null;
  reopened_at?: string | null;
  reopen_reason?: string;
}

export interface ClosuresStatusResponse {
  operational_date: string;
  closures: CashClosure[];
  can_close_course: boolean;
  can_close_range: boolean;
  can_close_final: boolean;
}

export interface ReportsSummaryResponse {
  filters: {
    date_from: string;
    date_to: string;
    record_type: "COURSE" | "RANGE" | "BOTH";
    user_id: number | null;
    payment_method: PaymentMethod | null;
  };
  totals: {
    course_clp: number;
    range_clp: number;
    general_clp: number;
    people_count: number;
    baskets_count: number;
    course_records: number;
    range_records: number;
  };
  payment_totals: Record<PaymentMethod, number>;
  series: {
    by_day: Array<{
      date: string;
      course_total_clp: number;
      range_total_clp: number;
      people_count: number;
      baskets_count: number;
    }>;
  };
}

export interface ReportsRecordsResponse {
  course_entries?: CourseEntry[];
  range_orders?: RangeOrder[];
  closures: CashClosure[];
}

export interface BusinessSettings {
  default_range_unit_price_clp: number;
  course_price_weekday_clp: number;
  course_price_weekend_clp: number;
  updated_by_name?: string | null;
  updated_at: string;
}

export interface UserAdmin {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  profile_icon: number;
  role: "ADMIN" | "COURSE" | "RANGE" | "MIXED";
  permission_overrides: Record<string, boolean>;
  permissions: AppPermissions;
  date_joined: string;
  last_login?: string | null;
}

export async function fetchDashboardSummary(operationalDate?: string): Promise<DailySummary> {
  const { data } = await api.get<DailySummary>("/api/dashboard/summary/", {
    params: operationalDate ? { operational_date: operationalDate } : {},
  });
  return data;
}

export async function listCourseEntries(params: Record<string, string | number> = {}): Promise<CourseEntry[]> {
  const { data } = await api.get<CourseEntry[]>("/api/course-entries/", { params });
  return data;
}

export async function createCourseEntry(payload: Omit<CourseEntry, "id" | "created_by" | "created_by_name" | "created_at" | "updated_at">) {
  const { data } = await api.post<CourseEntry>("/api/course-entries/", payload);
  return data;
}

export async function updateCourseEntry(id: number, payload: Partial<CourseEntry>) {
  const { data } = await api.patch<CourseEntry>(`/api/course-entries/${id}/`, payload);
  return data;
}

export async function deleteCourseEntry(id: number) {
  await api.delete(`/api/course-entries/${id}/`);
}

export async function listRangeOrders(params: Record<string, string | number> = {}): Promise<RangeOrder[]> {
  const { data } = await api.get<RangeOrder[]>("/api/range-orders/", { params });
  return data;
}

export async function createRangeOrder(payload: Partial<RangeOrder>) {
  const { data } = await api.post<RangeOrder>("/api/range-orders/", payload);
  return data;
}

export async function updateRangeOrder(id: number, payload: Partial<RangeOrder>) {
  const { data } = await api.patch<RangeOrder>(`/api/range-orders/${id}/`, payload);
  return data;
}

export async function deleteRangeOrder(id: number) {
  await api.delete(`/api/range-orders/${id}/`);
}

export async function fetchClosuresStatus(operationalDate?: string): Promise<ClosuresStatusResponse> {
  const { data } = await api.get<ClosuresStatusResponse>("/api/closures/status/", {
    params: operationalDate ? { operational_date: operationalDate } : {},
  });
  return data;
}

export async function closeDayScope(payload: {
  scope: "COURSE" | "RANGE" | "FINAL";
  operational_date?: string;
  notes?: string;
  adjustment_clp?: number;
}) {
  const { data } = await api.post<CashClosure>("/api/closures/close/", payload);
  return data;
}

export async function reopenDayScope(payload: {
  scope: "COURSE" | "RANGE" | "FINAL";
  operational_date?: string;
  reason: string;
}) {
  const { data } = await api.post<CashClosure>("/api/closures/reopen/", payload);
  return data;
}

export async function fetchReportsSummary(params: Record<string, string | number> = {}) {
  const { data } = await api.get<ReportsSummaryResponse>("/api/reports/summary/", { params });
  return data;
}

export async function fetchReportsRecords(params: Record<string, string | number> = {}) {
  const { data } = await api.get<ReportsRecordsResponse>("/api/reports/records/", { params });
  return data;
}

export function buildExportXlsxUrl(params: Record<string, string | number> = {}) {
  const baseUrl = api.defaults.baseURL || "http://127.0.0.1:8000";
  const url = new URL("/api/exports/xlsx/", baseUrl);
  Object.entries(params).forEach(([key, value]) => url.searchParams.append(key, String(value)));
  return url.pathname + url.search;
}

export function buildExportPdfUrl(params: Record<string, string | number> = {}) {
  const baseUrl = api.defaults.baseURL || "http://127.0.0.1:8000";
  const url = new URL("/api/exports/pdf/", baseUrl);
  Object.entries(params).forEach(([key, value]) => url.searchParams.append(key, String(value)));
  return url.pathname + url.search;
}

export async function downloadBinary(urlPath: string, filename: string, contentType: string) {
  const response = await api.get(urlPath, { responseType: "blob" });
  const blob = new Blob([response.data], { type: contentType });
  const objectUrl = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = objectUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(objectUrl);
}

export async function getBusinessSettings(): Promise<BusinessSettings> {
  const { data } = await api.get<BusinessSettings>("/api/business-settings/");
  return data;
}

export async function updateBusinessSettings(payload: Partial<BusinessSettings>) {
  const { data } = await api.patch<BusinessSettings>("/api/business-settings/", payload);
  return data;
}

export async function listUsers(): Promise<UserAdmin[]> {
  const { data } = await api.get<UserAdmin[]>("/api/users/");
  return data;
}

export async function createUser(payload: Record<string, unknown>) {
  const { data } = await api.post<UserAdmin>("/api/users/", payload);
  return data;
}

export async function updateUser(id: number, payload: Record<string, unknown>) {
  const { data } = await api.patch<UserAdmin>(`/api/users/${id}/`, payload);
  return data;
}

export async function deleteUser(id: number) {
  await api.delete(`/api/users/${id}/`);
}
