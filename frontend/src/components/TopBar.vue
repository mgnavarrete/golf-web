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
              <span :class="[item.icon, 'text-color', 'breadcrumb-icon']" />
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
  icon: string;
  route: string;
}

defineEmits<{ (e: "toggle-sidebar"): void }>();

const route = useRoute();

const home = {
  icon: "pi pi-home",
  route: "/",
};

const routeMap: Record<string, RouteInfo> = {
  "/": { label: "Inicio", icon: "pi pi-home", route: "/" },
  "/course-entries": { label: "Entradas Cancha", icon: "pi pi-users", route: "/course-entries" },
  "/course-entries/new": { label: "Nueva Entrada", icon: "pi pi-plus", route: "/course-entries/new" },
  "/range-orders": { label: "Pedidos Range", icon: "pi pi-shopping-cart", route: "/range-orders" },
  "/range-orders/new": { label: "Nuevo Pedido", icon: "pi pi-plus", route: "/range-orders/new" },
  "/closures": { label: "Cierre de Caja", icon: "pi pi-wallet", route: "/closures" },
  "/reports": { label: "Reportes", icon: "pi pi-chart-line", route: "/reports" },
  "/profile": { label: "Perfil", icon: "pi pi-user", route: "/profile" },
  "/config": { label: "Configuración", icon: "pi pi-cog", route: "/config" },
};

const currentPageTitle = computed(() => {
  const currentRoute = route.path;
  return routeMap[currentRoute]?.label || "Inicio";
});

const items = computed(() => {
  const currentRoute = route.path;
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
