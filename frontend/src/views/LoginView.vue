<template>
  <div class="login-page">
    <!-- Panel izquierdo con formulario -->
    <div class="form-panel">
      <div class="form-wrapper">
        <!-- Logo para móvil - fuera de la carta -->
        <div class="mobile-logo">
          <img :src="logo" alt="Minttu" />
        </div>
        <div class="form-container">
          <div class="form-header">
            <h2 class="form-title">Inicio de Sesión</h2>
            <p class="form-subtitle">Ingresa tus credenciales para acceder</p>
          </div>

          <form @submit.prevent="submit" class="form">
            <div class="field">
              <label for="email" class="field-label">Correo electrónico</label>
              <InputText
                id="email"
                v-model="email"
                placeholder="Ingresa tu correo electrónico"
                class="w-full input-field"
                :class="{ 'p-invalid': error }"
                @keyup.enter="submit"
              />
            </div>

            <div class="field">
              <label for="password" class="field-label">Contraseña</label>
              <Password
                id="password"
                v-model="password"
                :feedback="false"
                toggleMask
                placeholder="Ingresa tu contraseña"
                class="w-full input-field"
                :class="{ 'p-invalid': error }"
                inputClass="w-full"
                @keyup.enter="submit"
              />
            </div>

            <Message v-if="error" severity="error" :closable="false" class="error-message">
              {{ error }}
            </Message>

            <Button
              type="submit"
              label="Ingresar"
              icon="pi pi-sign-in"
              :loading="auth.loading"
              class="w-full submit-button"
              @click="submit"
            />

            <div class="form-footer">
              <p class="footer-text">
                ¿Necesitas ayuda? <a href="#" class="footer-link">Contacta a soporte</a>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Panel derecho con imágenes -->
    <div class="image-panel">
      <div class="image-carousel">
        <div
          v-for="(img, index) in images"
          :key="index"
          class="carousel-slide"
          :class="{ active: currentImageIndex === index }"
        >
          <img :src="img" :alt="`Imagen ${index + 1}`" class="carousel-image" />
        </div>
      </div>
      <img :src="logo" class="image-panel-logo" alt="Minttu" />
    </div>
  </div>
</template>

<script setup lang="ts">
// ============================================
// IMPORTS
// ============================================
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

// PrimeVue Components
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Button from "primevue/button";
import Message from "primevue/message";

// Stores
import { useAuthStore } from "@/stores/auth";

// Assets
import logo from "@/assets/brand/logo_dark.svg";
import log1 from "@/assets/images/login/log1.png";
import log2 from "@/assets/images/login/log2.png";
import log3 from "@/assets/images/login/log3.png";
import log4 from "@/assets/images/login/log4.png";

// Styles
import "@/styles/login.css";

// ============================================
// COMPOSABLES
// ============================================
const router = useRouter();
const auth = useAuthStore();

// ============================================
// STATE
// ============================================
const email = ref("");
const password = ref("");
const error = ref("");
const currentImageIndex = ref(0);

// ============================================
// CONSTANTS
// ============================================
const images = [log1, log2, log3, log4];

// ============================================
// LIFECYCLE
// ============================================
let carouselInterval: number | null = null;

onMounted(() => {
  carouselInterval = window.setInterval(() => {
    currentImageIndex.value = (currentImageIndex.value + 1) % images.length;
  }, 5000);
});

onUnmounted(() => {
  if (carouselInterval) {
    clearInterval(carouselInterval);
  }
});

// ============================================
// METHODS
// ============================================
async function submit() {
  error.value = "";
  if (!email.value.trim()) {
    error.value = "Por favor ingresa tu correo electrónico.";
    return;
  }
  if (!password.value) {
    error.value = "Por favor ingresa tu contraseña.";
    return;
  }
  try {
    // Login incluye fetchMe() internamente
    await auth.login(email.value.trim(), password.value);
    
    // Todos los usuarios van directamente a home después del login
    // El backend se encarga de asignar automáticamente la empresa activa
    router.push("/");
  } catch (e: any) {
    console.error("Login error:", e);
    error.value = "Credenciales Inválidas";
  }
}
</script>

<style scoped>
/* Login-specific button overrides */
.submit-button :deep(.p-button),
.submit-button :deep(button.p-button),
.submit-button :deep(.p-component),
.submit-button :deep(button.p-component),
.submit-button :deep(.p-button.p-button-success),
.submit-button :deep(button.p-button-success),
.submit-button :deep(.p-button[type="submit"]),
.submit-button :deep(button[type="submit"]) {
  background: var(--minttu-primary) !important;
  background-color: var(--minttu-primary) !important;
  border-color: var(--minttu-primary) !important;
  color: #ffffff !important;
  border: none !important;
}

.submit-button :deep(.p-button[style*="background"]),
.submit-button :deep(button[style*="background"]) {
  background: var(--minttu-primary) !important;
  background-color: var(--minttu-primary) !important;
}

.submit-button :deep(.p-button:hover:not(:disabled)),
.submit-button :deep(button.p-button:hover:not(:disabled)),
.submit-button :deep(.p-component:hover:not(:disabled)),
.submit-button :deep(button.p-component:hover:not(:disabled)),
.submit-button :deep(.p-button.p-button-success:hover:not(:disabled)),
.submit-button :deep(button.p-button-success:hover:not(:disabled)) {
  background: rgba(29, 33, 49, 0.95) !important;
  background-color: rgba(29, 33, 49, 0.95) !important;
  border-color: rgba(29, 33, 49, 0.95) !important;
  color: #ffffff !important;
}

.submit-button :deep(.p-button:active:not(:disabled)),
.submit-button :deep(button.p-button:active:not(:disabled)),
.submit-button :deep(.p-component:active:not(:disabled)),
.submit-button :deep(button.p-component:active:not(:disabled)),
.submit-button :deep(.p-button.p-button-success:active:not(:disabled)),
.submit-button :deep(button.p-button-success:active:not(:disabled)) {
  background: var(--minttu-primary) !important;
  background-color: var(--minttu-primary) !important;
  border-color: var(--minttu-primary) !important;
  color: #ffffff !important;
}

.submit-button :deep(.p-button:focus),
.submit-button :deep(button.p-button:focus),
.submit-button :deep(.p-component:focus),
.submit-button :deep(button.p-component:focus),
.submit-button :deep(.p-button.p-button-success:focus),
.submit-button :deep(button.p-button-success:focus) {
  background: var(--minttu-primary) !important;
  background-color: var(--minttu-primary) !important;
  border-color: var(--minttu-primary) !important;
  color: #ffffff !important;
  box-shadow: 0 0 0 3px rgba(29, 33, 49, 0.1) !important;
  outline: none !important;
}

.submit-button :deep(.p-button:disabled),
.submit-button :deep(button.p-button:disabled),
.submit-button :deep(.p-component:disabled),
.submit-button :deep(button.p-component:disabled) {
  background: #868786 !important;
  background-color: #868786 !important;
  border-color: #868786 !important;
  color: #ffffff !important;
  opacity: 0.6;
}
</style>

<style>
/* Global styles for login page button */
.login-page .submit-button.p-button,
.login-page .submit-button button.p-button,
.login-page .submit-button .p-button.p-button-success,
.login-page .submit-button button.p-button-success {
  background: var(--minttu-primary) !important;
  background-color: var(--minttu-primary) !important;
  border-color: var(--minttu-primary) !important;
  color: #ffffff !important;
}

.login-page .submit-button.p-button:hover:not(:disabled),
.login-page .submit-button button.p-button:hover:not(:disabled) {
  background: rgba(29, 33, 49, 0.95) !important;
  background-color: rgba(29, 33, 49, 0.95) !important;
  border-color: rgba(29, 33, 49, 0.95) !important;
  color: #ffffff !important;
}
</style>
