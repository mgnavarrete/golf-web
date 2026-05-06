import { api } from "@/lib/api";

export type Company = {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
};

export type ActiveCompany = {
  id: number;
  name: string;
  slug: string;
};

/**
 * Obtiene todas las empresas disponibles para el usuario actual
 */
export async function fetchCompanies(): Promise<Company[]> {
  const { data } = await api.get<Company[]>("/api/companies/");
  return data;
}

/**
 * Obtiene la empresa actualmente seleccionada
 */
export async function getActiveCompany(): Promise<ActiveCompany | null> {
  try {
    const { data } = await api.get<ActiveCompany>("/api/companies/select/");
    return data;
  } catch (error: any) {
    if (error.response?.status === 404) {
      return null;
    }
    throw error;
  }
}

/**
 * Selecciona una empresa como activa
 */
export async function selectCompany(companyId: number): Promise<ActiveCompany> {
  const { data } = await api.post<{ company: ActiveCompany }>("/api/companies/select/", {
    company_id: companyId,
  });
  return data.company;
}

/**
 * Limpia la selección de empresa (solo para super admins)
 */
export async function clearCompanySelection(): Promise<void> {
  await api.post("/api/companies/clear/");
}
