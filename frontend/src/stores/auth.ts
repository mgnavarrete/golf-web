import { defineStore } from "pinia";
import { api } from "@/lib/api";
import type { AppPermissions } from "@/services/golf";

export type Me = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  role: "ADMIN" | "COURSE" | "RANGE" | "MIXED";
  roles: string[];
  profile_icon: number;
  permissions: AppPermissions;
};

export const useAuthStore = defineStore("auth", {
  state: () => ({
    me: null as Me | null,
    loading: false,
  }),

  getters: {
    isAuthenticated: () => !!localStorage.getItem("access_token"),
    displayName: (s) => (s.me?.first_name ? s.me.first_name : s.me?.email ?? ""),
    isAdmin: (s) => s.me?.role === "ADMIN" || !!s.me?.is_superuser,
  },

  actions: {
    async login(email: string, password: string) {
      this.loading = true;
      try {
        const { data } = await api.post(
          "/api/auth/token/",
          { email, password },
          { headers: { "Content-Type": "application/json" } }
        );
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        await this.fetchMe();
      } finally {
        this.loading = false;
      }
    },

    async fetchMe() {
      const { data } = await api.get<Me>("/api/auth/me/");
      this.me = data;
      return data;
    },

    logout() {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      this.me = null;
    },
  },
});
