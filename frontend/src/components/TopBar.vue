<template>
  <header class="topbar">
    <button class="mobile-menu-button" @click="$emit('toggle-sidebar')" title="Menú">
      <i class="pi pi-bars"></i>
    </button>

    <div class="topbar-left">
      <span class="page-title">{{ currentPageTitle }}</span>
    </div>

    <div class="topbar-right">
      <Breadcrumb :home="home" :model="items" class="topbar-breadcrumb">
        <template #item="{ item, props }">
          <router-link v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
            <a :href="href" v-bind="props.action" @click="navigate">
              <span
                v-if="item.materialIcon"
                class="material-symbols-outlined text-color breadcrumb-icon"
                aria-hidden="true"
              >
                {{ item.materialIcon }}
              </span>
              <span v-else :class="[item.icon, 'text-color', 'breadcrumb-icon']" />
              <span class="text-primary font-semibold breadcrumb-label">{{ item.label }}</span>
            </a>
          </router-link>
        </template>
      </Breadcrumb>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import Breadcrumb from "primevue/breadcrumb";

import "@/styles/components/topbar.css";

interface RouteInfo {
  label: string;
  icon?: string;
  materialIcon?: string;
  route: string;
}

defineEmits<{ (e: "toggle-sidebar"): void }>();

const route = useRoute();

const home = {
  materialIcon: "home",
  route: "/",
};

const routeMap: Record<string, RouteInfo> = {
  "/": { label: "Inicio", materialIcon: "home", route: "/" },
  "/course-entries": { label: "Entradas Cancha", materialIcon: "golf_course", route: "/course-entries" },
  "/course-entries/new": { label: "Nueva Entrada", icon: "pi pi-plus", route: "/course-entries/new" },
  "/range-orders": { label: "Pedidos Range", materialIcon: "sports_golf", route: "/range-orders" },
  "/range-orders/new": { label: "Nuevo Pedido", icon: "pi pi-plus", route: "/range-orders/new" },
  "/closures": { label: "Cierre de Caja", materialIcon: "point_of_sale", route: "/closures" },
  "/reports": { label: "Reportes", materialIcon: "analytics", route: "/reports" },
  "/profile": { label: "Perfil", icon: "pi pi-user", route: "/profile" },
  "/config": { label: "Configuración", icon: "pi pi-cog", route: "/config" },
};

const currentPageTitle = computed(() => {
  const currentRoute = route.path;
  if (currentRoute.startsWith("/closures/")) return "Detalle de Cierre";
  return routeMap[currentRoute]?.label || "Inicio";
});

const items = computed(() => {
  const currentRoute = route.path;
  if (currentRoute.startsWith("/closures/")) {
    const closuresRoute = routeMap["/closures"]!;
    return [
      closuresRoute,
      { label: "Detalle de Cierre", materialIcon: "receipt_long", route: currentRoute },
    ];
  }
  const routeInfo = routeMap[currentRoute];
  if (routeInfo && currentRoute !== "/") {
    return [routeInfo];
  }
  return [];
});
</script>

<style>
.topbar .p-breadcrumb,
.topbar .p-breadcrumb *,
.topbar .p-breadcrumb ul,
.topbar .p-breadcrumb li,
.topbar .p-breadcrumb-list,
.topbar .p-breadcrumb-item,
.topbar .p-breadcrumb-root,
.topbar .p-breadcrumb-link,
.topbar .p-breadcrumb-link *,
.topbar .p-breadcrumb-separator,
.topbar .p-breadcrumb-separator * {
  background: transparent !important;
  background-color: transparent !important;
  background-image: none !important;
}
</style>
