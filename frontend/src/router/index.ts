import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

import HomeView from "@/views/HomeView.vue";
import CourseEntriesView from "@/views/CourseEntriesView.vue";
import CourseEntryFormView from "@/views/CourseEntryFormView.vue";
import RangeOrdersView from "@/views/RangeOrdersView.vue";
import RangeOrderFormView from "@/views/RangeOrderFormView.vue";
import ClosuresView from "@/views/ClosuresView.vue";
import ReportsView from "@/views/ReportsView.vue";
import ConfigView from "@/views/ConfigView.vue";
import ProfileView from "@/views/ProfileView.vue";
import LoginView from "@/views/LoginView.vue";
import HelpView from "@/views/HelpView.vue";
import HealthView from "@/views/HealthView.vue";
import NotFoundView from "@/views/NotFoundView.vue";

declare module "vue-router" {
  interface RouteMeta {
    title?: string;
    requiresAuth?: boolean;
    hideLayout?: boolean;
    isNotFound?: boolean;
    permission?: string;
  }
}

const routes = [
  { path: "/login", component: LoginView, meta: { title: "Login", requiresAuth: false } },
  {
    path: "/",
    component: HomeView,
    meta: { title: "Inicio", requiresAuth: true, permission: "can_view_dashboard" },
  },
  {
    path: "/course-entries",
    component: CourseEntriesView,
    meta: { title: "Entradas Cancha", requiresAuth: true, permission: "can_manage_course_entries" },
  },
  {
    path: "/course-entries/new",
    component: CourseEntryFormView,
    meta: { title: "Nueva Entrada Cancha", requiresAuth: true, permission: "can_manage_course_entries" },
  },
  {
    path: "/range-orders",
    component: RangeOrdersView,
    meta: { title: "Pedidos Range", requiresAuth: true, permission: "can_manage_range_orders" },
  },
  {
    path: "/range-orders/new",
    component: RangeOrderFormView,
    meta: { title: "Nuevo Pedido Range", requiresAuth: true, permission: "can_manage_range_orders" },
  },
  {
    path: "/closures",
    component: ClosuresView,
    meta: { title: "Cierre de Caja", requiresAuth: true, permission: "can_close_day" },
  },
  {
    path: "/reports",
    component: ReportsView,
    meta: { title: "Reportes", requiresAuth: true, permission: "can_view_reports" },
  },
  {
    path: "/config",
    component: ConfigView,
    meta: { title: "Configuración", requiresAuth: true, permission: "can_manage_users" },
  },
  {
    path: "/profile",
    component: ProfileView,
    meta: { title: "Mi Perfil", requiresAuth: true },
  },
  { path: "/help", component: HelpView, meta: { title: "Ayuda", requiresAuth: false } },
  { path: "/health", component: HealthView, meta: { title: "Health", requiresAuth: false } },
  {
    path: "/:pathMatch(.*)*",
    component: NotFoundView,
    meta: { title: "404", requiresAuth: false, isNotFound: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});


function firstAllowedPath(authStore: ReturnType<typeof useAuthStore>) {
  const perms = authStore.me?.permissions;
  if (!perms) return "/profile";
  if (perms.can_view_dashboard) return "/";
  if (perms.can_manage_course_entries) return "/course-entries";
  if (perms.can_manage_range_orders) return "/range-orders";
  if (perms.can_close_day) return "/closures";
  if (perms.can_view_reports) return "/reports";
  if (perms.can_manage_users) return "/config";
  return "/profile";
}

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore();
  const token = localStorage.getItem("access_token");
  const isAuthenticated = !!token;

  if (to.path === "/login") {
    if (!isAuthenticated) {
      next();
      return;
    }
    next("/");
    return;
  }

  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      next({ path: "/login", replace: true });
      return;
    }

    if (!auth.me) {
      try {
        await auth.fetchMe();
      } catch {
        next({ path: "/login", replace: true });
        return;
      }
    }

    if (to.meta.permission) {
      const hasPermission = auth.me?.permissions?.[to.meta.permission as keyof typeof auth.me.permissions];
      if (!hasPermission && !auth.isAdmin) {
        const target = firstAllowedPath(auth);
        if (target === to.path) {
          next({ path: "/profile", replace: true });
          return;
        }
        next({ path: target, replace: true });
        return;
      }
    }
  }

  next();
});

export default router;
