<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <img :src="logo" alt="Minttu" class="not-found-logo" @click="goToHome" />
      <h1 class="not-found-title">404: Página no encontrada</h1>
      <p class="not-found-description">
        La ruta que buscas no existe o ha sido movida.
      </p>
      <button @click="goBack" class="not-found-button">
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
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--minttu-bg, #f5f5f5);
}

.not-found-content {
  text-align: center;
  padding: var(--minttu-spacing-xl);
  max-width: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--minttu-spacing-lg);
}

.not-found-logo {
  height: 120px;
  width: auto;
  margin-bottom: var(--minttu-spacing-lg);
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.not-found-logo:hover {
  opacity: 0.8;
}

.not-found-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--minttu-primary);
  margin: 0;
  line-height: 1.2;
}

.not-found-description {
  font-size: 16px;
  font-weight: 400;
  color: var(--minttu-gray, #666);
  margin: 0;
  line-height: 1.6;
}

.not-found-button {
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

.not-found-button:hover {
  background: rgba(29, 33, 49, 0.9);
  transform: translateY(-1px);
}

.not-found-button:active {
  transform: translateY(0);
}
</style>
