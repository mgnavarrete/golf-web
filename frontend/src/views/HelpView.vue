<template>
  <div class="help-container">
    <div class="help-content">
      <img :src="logo" alt="Minttu" class="help-logo" @click="goToHome" />
      <h1 class="help-title">¿Necesitas ayuda?</h1>
      <p class="help-message">
        Ponte en contacto con <a href="https://minttu.cl" target="_blank" class="help-link">soporte</a>
      </p>
      <button @click="goBack" class="help-button">
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
.help-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--minttu-bg, #f5f5f5);
}

.help-content {
  text-align: center;
  padding: var(--minttu-spacing-xl);
  max-width: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--minttu-spacing-lg);
}

.help-logo {
  height: 120px;
  width: auto;
  margin-bottom: var(--minttu-spacing-lg);
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.help-logo:hover {
  opacity: 0.8;
}

.help-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--minttu-primary);
  margin: 0;
}

.help-message {
  font-size: 18px;
  font-weight: 400;
  color: var(--minttu-gray, #666);
  margin: 0;
  line-height: 1.6;
}

.help-link {
  color: var(--minttu-primary);
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.help-link:hover {
  color: #10b981;
  text-decoration: underline;
}

.help-button {
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

.help-button:hover {
  background: rgba(29, 33, 49, 0.9);
  transform: translateY(-1px);
}

.help-button:active {
  transform: translateY(0);
}
</style>
