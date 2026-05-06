<template>
  <div class="sidebar-container" :class="{ 'mobile-open': isMobileOpen }">
    <div class="sidebar-panel">
      <div class="sidebar-logo-wrapper">
        <RouterLink to="/" class="sidebar-logo" title="Inicio" @click="emit('close-mobile')">
          <img :src="logoIcon" class="logo-icon" alt="Golf" />
          <img :src="logoFull" class="logo-full" alt="Golf" />
        </RouterLink>

        <button class="mobile-close-button" @click="emit('close-mobile')" title="Cerrar menú">
          <i class="pi pi-times"></i>
        </button>
      </div>

      <nav class="sidebar-nav">
        <RouterLink
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          :title="item.label"
          @click="emit('close-mobile')"
        >
          <span
            v-if="item.materialIcon"
            class="material-symbols-outlined nav-material-icon"
            aria-hidden="true"
          >
            {{ item.materialIcon }}
          </span>
          <i v-else :class="item.icon"></i>
          <span class="nav-label">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-bottom" :class="{ 'menu-open': isUserMenuOpen }">
        <div class="sidebar-separator"></div>

        <Transition name="slide-down">
          <div v-if="isUserMenuOpen" class="user-menu-buttons">
            <button class="nav-item profile-item" @click="handleProfile" title="Perfil">
              <i class="pi pi-user"></i>
              <span class="nav-label">Perfil</span>
            </button>
            <button
              v-if="canAccessConfig"
              class="nav-item settings-item"
              @click="handleSettings"
              title="Configuración"
            >
              <i class="pi pi-cog"></i>
              <span class="nav-label">Configuración</span>
            </button>
            <button class="nav-item logout-item" @click="handleLogout" title="Cerrar sesión">
              <i class="pi pi-sign-out"></i>
              <span class="nav-label">Cerrar sesión</span>
            </button>
          </div>
        </Transition>

        <div class="user-avatar-container" @click="toggleUserMenu" title="Usuario">
          <div class="user-avatar">
            <img v-if="userIcon" :src="userIcon" :alt="userName" />
            <div v-else class="avatar-placeholder">
              <i class="pi pi-user"></i>
            </div>
          </div>
          <span class="user-name">{{ userName }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

import logoIcon from "@/assets/brand/ico_dark.svg";
import logoFull from "@/assets/brand/logo_dark.svg";
import userIcon1 from "@/assets/images/user_icon/user_1.png";
import userIcon2 from "@/assets/images/user_icon/user_2.png";
import userIcon3 from "@/assets/images/user_icon/user_3.png";
import userIcon4 from "@/assets/images/user_icon/user_4.png";
import userIcon5 from "@/assets/images/user_icon/user_5.png";
import userIcon6 from "@/assets/images/user_icon/user_6.png";
import userIcon7 from "@/assets/images/user_icon/user_7.png";
import userIcon8 from "@/assets/images/user_icon/user_8.png";
import userIcon9 from "@/assets/images/user_icon/user_9.png";
import userIcon10 from "@/assets/images/user_icon/user_10.png";

import "@/styles/components/sidebar.css";
import "@/styles/utilities/transitions.css";

interface MenuItem {
  path: string;
  label: string;
  icon?: string;
  materialIcon?: string;
}

const props = defineProps<{
  isMobileOpen?: boolean;
}>();

const emit = defineEmits<{
  (e: "logout"): void;
  (e: "close-mobile"): void;
}>();

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const isUserMenuOpen = ref(false);

const userIcons: Record<number, string> = {
  1: userIcon1,
  2: userIcon2,
  3: userIcon3,
  4: userIcon4,
  5: userIcon5,
  6: userIcon6,
  7: userIcon7,
  8: userIcon8,
  9: userIcon9,
  10: userIcon10,
};

const menuItems = computed<MenuItem[]>(() => {
  const permissions = auth.me?.permissions;
  const items: MenuItem[] = [];

  if (permissions?.can_view_dashboard) {
    items.push({ path: "/", label: "Inicio", materialIcon: "home" });
  }
  if (permissions?.can_manage_course_entries) {
    items.push({ path: "/course-entries", label: "Entradas Cancha", materialIcon: "golf_course" });
  }
  if (permissions?.can_manage_range_orders) {
    items.push({ path: "/range-orders", label: "Driving Range", materialIcon: "sports_golf" });
  }
  if (permissions?.can_close_day) {
    items.push({ path: "/closures", label: "Cierre Caja", materialIcon: "point_of_sale" });
  }
  if (permissions?.can_view_reports) {
    items.push({ path: "/reports", label: "Reportes", materialIcon: "analytics" });
  }

  return items;
});

const canAccessConfig = computed(() => auth.me?.permissions?.can_manage_users || false);

const userName = computed(() => {
  if (!auth.me) return "Usuario";
  const firstName = String(auth.me.first_name || "").trim();
  const lastName = String(auth.me.last_name || "").trim();
  if (firstName && lastName) return `${firstName} ${lastName}`;
  if (firstName) return firstName;
  if (lastName) return lastName;
  return auth.me.email.split("@")[0];
});

const userIcon = computed(() => {
  const iconNumber = auth.me?.profile_icon;
  if (!iconNumber) return null;
  return userIcons[Math.max(1, Math.min(10, iconNumber))] || null;
});

const isActive = (path: string) => {
  if (path === "/") return route.path === "/";
  return route.path.startsWith(path);
};

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value;
};

const handleProfile = () => {
  router.push("/profile");
  isUserMenuOpen.value = false;
  emit("close-mobile");
};

const handleSettings = () => {
  router.push("/config");
  isUserMenuOpen.value = false;
  emit("close-mobile");
};

const handleLogout = () => {
  emit("logout");
};

onMounted(async () => {
  if (auth.isAuthenticated && !auth.me) {
    try {
      await auth.fetchMe();
    } catch {
      // ignore
    }
  }
});
</script>
