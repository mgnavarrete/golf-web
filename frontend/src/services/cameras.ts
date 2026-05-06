import { api } from "@/lib/api";

// ============================================
// TYPES
// ============================================

export interface Camera {
  id: number;
  code: string;
  name: string;
  location_name: string | null;
  latitude: number | string | null;
  longitude: number | string | null;
  is_active: boolean;
  status: "ONLINE" | "OFFLINE" | "UNKNOWN";
  last_seen_at: string | null;
}

export interface CameraFilters {
  search?: string;
  status?: string;
  is_active?: boolean;
}

export interface CameraStats {
  total: number;
  online: number;
  offline: number;
  unknown: number;
  active: number;
  inactive: number;
}

// ============================================
// API FUNCTIONS
// ============================================

export async function fetchAllCameras(): Promise<Camera[]> {
  const { data } = await api.get<Camera[]>("/api/cameras/");
  return data;
}

export async function fetchCameraDetail(id: number): Promise<Camera> {
  const { data } = await api.get<Camera>(`/api/cameras/${id}/`);
  return data;
}

export async function updateCamera(id: number, updateData: Partial<Camera>): Promise<Camera> {
  const { data } = await api.patch<Camera>(`/api/cameras/${id}/`, updateData);
  return data;
}

export async function createCamera(cameraData: Omit<Camera, "id" | "last_seen_at">): Promise<Camera> {
  const { data } = await api.post<Camera>("/api/cameras/", cameraData);
  return data;
}

// ============================================
// HELPER FUNCTIONS
// ============================================

export function calculateCameraStats(cameras: Camera[]): CameraStats {
  return {
    total: cameras.length,
    online: cameras.filter((c) => c.status === "ONLINE").length,
    offline: cameras.filter((c) => c.status === "OFFLINE").length,
    unknown: cameras.filter((c) => c.status === "UNKNOWN").length,
    active: cameras.filter((c) => c.is_active).length,
    inactive: cameras.filter((c) => !c.is_active).length,
  };
}

export function filterCameras(cameras: Camera[], filters: CameraFilters): Camera[] {
  let filtered = [...cameras];

  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    filtered = filtered.filter(
      (c) =>
        c.name.toLowerCase().includes(searchLower) ||
        c.code.toLowerCase().includes(searchLower) ||
        (c.location_name && c.location_name.toLowerCase().includes(searchLower))
    );
  }

  if (filters.status) {
    filtered = filtered.filter((c) => c.status === filters.status);
  }

  if (filters.is_active !== undefined) {
    filtered = filtered.filter((c) => c.is_active === filters.is_active);
  }

  return filtered;
}

export function sortCameras(cameras: Camera[], sortBy: string = "status"): Camera[] {
  const sorted = [...cameras];

  switch (sortBy) {
    case "status":
      // Online primero, luego offline, luego unknown
      sorted.sort((a, b) => {
        const order = { ONLINE: 0, OFFLINE: 1, UNKNOWN: 2 };
        return order[a.status] - order[b.status] || a.name.localeCompare(b.name);
      });
      break;
    case "name":
      sorted.sort((a, b) => a.name.localeCompare(b.name));
      break;
    case "code":
      sorted.sort((a, b) => a.code.localeCompare(b.code));
      break;
    case "location":
      sorted.sort((a, b) => (a.location_name || "").localeCompare(b.location_name || ""));
      break;
    case "last_seen":
      sorted.sort((a, b) => {
        if (!a.last_seen_at && !b.last_seen_at) return 0;
        if (!a.last_seen_at) return 1;
        if (!b.last_seen_at) return -1;
        return new Date(b.last_seen_at).getTime() - new Date(a.last_seen_at).getTime();
      });
      break;
  }

  return sorted;
}
