import type { ReportSummaryResponse } from "./reports";

/**
 * Genera el nombre del archivo para el reporte
 */
export function generateReportFilename(reportData: ReportSummaryResponse, extension: string): string {
  const dateFrom = reportData.summary?.date_range?.from || "fecha";
  const dateTo = reportData.summary?.date_range?.to || "fecha";
  const companyName = (reportData.company_name || "Empresa").replace(/\s+/g, "_").replace(/[^a-zA-Z0-9_]/g, "");
  return `Reporte_${companyName}_${dateFrom}_al_${dateTo}.${extension}`;
}
