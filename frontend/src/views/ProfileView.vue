<template>
  <div class="profile-page">
    <section class="card">
      <h1>Mi Perfil</h1>
      <p>{{ user?.email }}</p>
      <div class="badges">
        <span class="badge">Rol: {{ user?.role }}</span>
        <span class="badge" :class="user?.is_active ? 'active' : 'inactive'">
          {{ user?.is_active ? 'Activo' : 'Inactivo' }}
        </span>
      </div>
    </section>

    <section class="card form-grid">
      <h3>Datos personales</h3>
      <input v-model="form.first_name" placeholder="Nombre" />
      <input v-model="form.last_name" placeholder="Apellido" />
      <input v-model="form.email" type="email" placeholder="Correo" />
      <button class="btn btn-primary" @click="saveProfile">Guardar cambios</button>
    </section>

    <section class="card form-grid">
      <h3>Cambiar contraseña</h3>
      <input v-model="password.old_password" type="password" placeholder="Contraseña actual" />
      <input v-model="password.new_password" type="password" placeholder="Nueva contraseña" />
      <button class="btn btn-primary" @click="savePassword">Cambiar contraseña</button>
    </section>

    <p v-if="success" class="success">{{ success }}</p>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { api } from "@/lib/api";

const auth = useAuthStore();
const user = computed(() => auth.me);
const error = ref("");
const success = ref("");

const form = reactive({
  first_name: "",
  last_name: "",
  email: "",
});

const password = reactive({
  old_password: "",
  new_password: "",
});

function syncForm() {
  form.first_name = auth.me?.first_name || "";
  form.last_name = auth.me?.last_name || "";
  form.email = auth.me?.email || "";
}

async function saveProfile() {
  error.value = "";
  success.value = "";
  try {
    await api.patch("/api/auth/me/", form);
    await auth.fetchMe();
    syncForm();
    success.value = "Perfil actualizado";
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo actualizar el perfil";
  }
}

async function savePassword() {
  error.value = "";
  success.value = "";
  try {
    await api.post("/api/auth/change-password/", password);
    password.old_password = "";
    password.new_password = "";
    success.value = "Contraseña actualizada";
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo cambiar la contraseña";
  }
}

onMounted(async () => {
  if (!auth.me) await auth.fetchMe();
  syncForm();
});
</script>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 20px;
  box-shadow: var(--minttu-shadow-soft);
}
.badges {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}
.badge {
  background: var(--minttu-border);
  color: var(--minttu-primary);
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 500;
}
.badge.active {
  background: #E8F0EB;
  color: var(--minttu-primary);
}
.badge.inactive {
  background: #FEF2F2;
  color: #DC2626;
}
.form-grid {
  display: grid;
  gap: 8px;
}
input {
  border: 1px solid var(--minttu-border);
  border-radius: var(--minttu-radius-sm);
  padding: 10px 14px;
  background: var(--minttu-white);
  color: var(--minttu-text);
  font-family: inherit;
  transition: all 0.2s ease;
}
input:focus {
  border-color: var(--minttu-primary);
  box-shadow: 0 0 0 3px rgba(27, 67, 50, 0.1);
  outline: none;
}
.success {
  color: #0f6b45;
}
.error {
  color: #c0392b;
}
</style>
