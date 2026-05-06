<template>
  <div class="dashboard-layout">
    <div v-if="isMobileSidebarOpen" class="sidebar-overlay" @click="closeMobileSidebar"></div>

    <Sidebar :is-mobile-open="isMobileSidebarOpen" @logout="onLogout" @close-mobile="closeMobileSidebar" />

    <div class="main-content">
      <TopBar @toggle-sidebar="toggleMobileSidebar" />
      <main class="content-area">
        <slot />
      </main>
    </div>

    <button
      v-if="showFloatingButton && isMobile"
      class="floating-sidebar-button"
      @click="toggleMobileSidebar"
      title="Abrir menú"
    >
      <i class="pi pi-bars"></i>
    </button>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import Sidebar from "@/components/Sidebar.vue";
import TopBar from "@/components/TopBar.vue";

const emit = defineEmits<{ (e: "logout"): void }>();
const auth = useAuthStore();

const isMobileSidebarOpen = ref(false);
const showFloatingButton = ref(false);
const isMobile = ref(false);

function toggleMobileSidebar() {
  isMobileSidebarOpen.value = !isMobileSidebarOpen.value;
}

function closeMobileSidebar() {
  isMobileSidebarOpen.value = false;
}

function onLogout() {
  auth.logout();
  window.location.replace("/login");
  emit("logout");
}

function checkMobile() {
  isMobile.value = window.innerWidth <= 1024;
}

function handleScroll() {
  if (!isMobile.value) {
    showFloatingButton.value = false;
    return;
  }
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  showFloatingButton.value = scrollTop > 100;
}

onMounted(() => {
  checkMobile();
  window.addEventListener("resize", checkMobile);
  window.addEventListener("scroll", handleScroll);
});

onUnmounted(() => {
  window.removeEventListener("resize", checkMobile);
  window.removeEventListener("scroll", handleScroll);
});
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background: var(--minttu-bg);
  gap: 24px;
  position: relative;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding-right: 32px;
}

.content-area {
  flex: 1;
  padding: 0 0 32px 0;
  overflow-y: auto;
}

.sidebar-overlay {
  display: none;
}

@media (max-width: 1024px) {
  .dashboard-layout {
    gap: 0;
  }

  .main-content {
    padding-left: 16px;
    padding-right: 16px;
    width: 100%;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 998;
    backdrop-filter: blur(2px);
  }
}

.floating-sidebar-button {
  position: fixed;
  bottom: var(--minttu-spacing-lg);
  left: var(--minttu-spacing-lg);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--minttu-primary);
  color: var(--minttu-white);
  border: none;
  box-shadow: var(--minttu-shadow-medium);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 997;
}

.floating-sidebar-button i {
  font-size: 24px;
}

@media (min-width: 1025px) {
  .floating-sidebar-button {
    display: none;
  }
}
</style>
