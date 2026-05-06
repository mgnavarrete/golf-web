<template>
  <div class="health-container">
    <div class="health-content">
      <img :src="logo" alt="Minttu" class="health-logo" @click="goToHome" />
      <div class="health-status-wrapper">
        <p class="health-label">Server Status</p>
        <p class="health-message">OK</p>
      </div>
      <button @click="goBack" class="health-button">
        {{ buttonText }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// ============================================
// IMPORTS
// ============================================
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import logo from "@/assets/brand/logo_main.svg";

// ============================================
// COMPOSABLES
// ============================================
const router = useRouter();
const auth = useAuthStore();

// ============================================
// COMPUTED
// ============================================
const buttonText = computed(() => {
  return auth.isAuthenticated ? "Volver a Home" : "Volver al Login";
});

// ============================================
// METHODS
// ============================================
function goBack() {
  if (auth.isAuthenticated) {
    router.push("/");
  } else {
    router.push("/login");
  }
}

function goToHome() {
  router.push("/");
}
</script>

<style scoped>
.health-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--minttu-bg, #f5f5f5);
}

.health-content {
  text-align: center;
  padding: var(--minttu-spacing-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--minttu-spacing-xl);
}

.health-logo {
  height: 120px;
  width: auto;
  margin-bottom: var(--minttu-spacing-lg);
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.health-logo:hover {
  opacity: 0.8;
}

.health-status-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--minttu-spacing-sm);
}

.health-label {
  font-size: 16px;
  font-weight: 500;
  color: var(--minttu-gray, #666);
  margin: 0;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.health-message {
  font-size: 64px;
  font-weight: 700;
  color: #10b981;
  margin: 0;
  line-height: 1;
  letter-spacing: 4px;
}

.health-button {
  margin-top: var(--minttu-spacing-md);
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: var(--minttu-primary);
  border: none;
  border-radius: var(--minttu-radius, 8px);
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.health-button:hover {
  background: rgba(29, 33, 49, 0.9);
  transform: translateY(-1px);
}

.health-button:active {
  transform: translateY(0);
}
</style>
