<template>
  <div class="page">
    <div class="header">
      <h1>Configuración</h1>
      <p>Usuarios, roles, permisos y ajustes de negocio.</p>
    </div>

    <section class="card" v-if="canPatchSettings">
      <div class="settings-header">
        <h3>Precios y Tarifas</h3>
        <button v-if="!isEditingSettings" class="btn btn-secondary" @click="startEditSettings">
          <i class="pi pi-pencil"></i> Editar Precios
        </button>
      </div>

      <div v-if="!isEditingSettings" class="prices-grid">
        <div class="price-card">
          <span class="price-label">Cancha (Día de semana)</span>
          <strong class="price-value">{{ formatClp(settings.course_price_weekday_clp) }}</strong>
        </div>
        <div class="price-card">
          <span class="price-label">Cancha (Finde / Festivo)</span>
          <strong class="price-value">{{ formatClp(settings.course_price_weekend_clp) }}</strong>
        </div>
        <div class="price-card">
          <span class="price-label">Canasto Range (Unidad)</span>
          <strong class="price-value">{{ formatClp(settings.default_range_unit_price_clp) }}</strong>
        </div>
      </div>

      <div v-else class="settings-form">
        <div class="row">
          <label>Cancha (Día de semana)</label>
          <input v-model.number="settingsEdit.course_price_weekday_clp" type="number" min="1" />
        </div>
        <div class="row">
          <label>Cancha (Finde / Festivo)</label>
          <input v-model.number="settingsEdit.course_price_weekend_clp" type="number" min="1" />
        </div>
        <div class="row">
          <label>Canasto Range (Unidad)</label>
          <input v-model.number="settingsEdit.default_range_unit_price_clp" type="number" min="1" />
        </div>
        <div class="form-actions" style="margin-top: 16px">
          <button class="btn btn-secondary" @click="cancelEditSettings">Cancelar</button>
          <button class="btn btn-primary" @click="saveSettings">Guardar Cambios</button>
        </div>
      </div>

      <small v-if="settings.updated_at && !isEditingSettings" class="updated-at">
        Última actualización: {{ new Date(settings.updated_at).toLocaleString("es-CL") }}
      </small>
    </section>

    <section class="card">
      <div class="users-header">
        <h3>Usuarios</h3>
        <button class="btn btn-accent" @click="openCreate"><i class="pi pi-plus"></i> Nuevo usuario</button>
      </div>

      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Email</th>
              <th>Nombre</th>
              <th>Rol</th>
              <th>Activo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.email }}</td>
              <td>{{ user.first_name }} {{ user.last_name }}</td>
              <td>{{ user.role }}</td>
              <td>{{ user.is_active ? "Sí" : "No" }}</td>
              <td class="actions-cell">
                <button class="action" @click="openEdit(user)">Editar</button>
                <button class="action danger" :disabled="user.id === meId" @click="askRemove(user.id)">Eliminar</button>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="5" class="empty">Sin usuarios</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="showUserForm" class="card form-grid">
      <h3>{{ editingId ? "Editar Usuario" : "Nuevo Usuario" }}</h3>
      <input v-model="userForm.email" type="email" placeholder="Email" />
      <input v-model="userForm.first_name" placeholder="Nombre" />
      <input v-model="userForm.last_name" placeholder="Apellido" />
      <input v-model="userForm.password" type="password" placeholder="Contraseña" />
      <select v-model="userForm.role">
        <option value="ADMIN">Admin</option>
        <option value="COURSE">Cancha</option>
        <option value="RANGE">Range</option>
        <option value="MIXED">Mixto</option>
      </select>
      <label class="check">
        <input v-model="userForm.is_active" type="checkbox" /> Activo
      </label>

      <div class="permissions-grouped">
        <div v-for="group in permissionGroups" :key="group.title" class="perm-group">
          <h4>{{ group.title }}</h4>
          <div class="perm-items">
            <label v-for="item in group.keys" :key="item.key" class="switch-row">
              <span class="switch-label">{{ item.label }}</span>
              <div class="switch">
                <input
                  type="checkbox"
                  :checked="!!userForm.permission_overrides[item.key]"
                  @change="togglePermission(item.key, $event)"
                />
                <span class="slider"></span>
              </div>
            </label>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn btn-secondary" @click="cancelUserForm">Cancelar</button>
        <button class="btn btn-primary" @click="saveUser">Guardar</button>
      </div>
    </section>

    <p v-if="error" class="error">{{ error }}</p>

    <ConfirmActionModal
      :visible="deleteTargetUserId !== null"
      title="Eliminar Usuario"
      message="¿Seguro que deseas eliminar este usuario? Esta acción no se puede deshacer."
      confirm-label="Eliminar"
      confirm-class="btn-danger"
      :loading="deletingUser"
      @cancel="cancelRemove"
      @confirm="confirmRemove"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  createUser,
  deleteUser,
  getBusinessSettings,
  listUsers,
  updateBusinessSettings,
  updateUser,
  type BusinessSettings,
  type UserAdmin,
} from "@/services/golf";
import { useAuthStore } from "@/stores/auth";
import ConfirmActionModal from "@/components/modals/ConfirmActionModal.vue";

const auth = useAuthStore();
const canPatchSettings = computed(() => auth.me?.permissions?.can_patch_settings || auth.isAdmin);
const meId = computed(() => auth.me?.id || 0);

const users = ref<UserAdmin[]>([]);
const error = ref("");
const showUserForm = ref(false);
const editingId = ref<number | null>(null);

const settings = reactive<BusinessSettings>({
  default_range_unit_price_clp: 5000,
  course_price_weekday_clp: 20000,
  course_price_weekend_clp: 25000,
  updated_at: "",
});

const isEditingSettings = ref(false);
const settingsEdit = reactive<BusinessSettings>({
  default_range_unit_price_clp: 5000,
  course_price_weekday_clp: 20000,
  course_price_weekend_clp: 25000,
  updated_at: "",
});

function formatClp(value: number) {
  return new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP", maximumFractionDigits: 0 }).format(value);
}

const userForm = reactive<any>({
  email: "",
  first_name: "",
  last_name: "",
  password: "",
  role: "MIXED",
  is_active: true,
  permission_overrides: {},
});

const permissionGroups = [
  {
    title: "Módulo Cancha",
    keys: [
      { key: "can_manage_course_entries", label: "Ver Registros" },
      { key: "can_edit_course_entries", label: "Editar Registros" },
      { key: "can_delete_course_entries", label: "Eliminar Registros" },
    ],
  },
  {
    title: "Módulo Range",
    keys: [
      { key: "can_manage_range_orders", label: "Ver Pedidos" },
      { key: "can_edit_range_orders", label: "Editar Pedidos" },
      { key: "can_delete_range_orders", label: "Eliminar Pedidos" },
    ],
  },
  {
    title: "Reportes e Historial",
    keys: [
      { key: "can_view_dashboard", label: "Ver Dashboard" },
      { key: "can_view_reports", label: "Ver Reportes" },
      { key: "can_export_excel", label: "Exportar Excel/PDF" },
    ],
  },
  {
    title: "Administración y Cierres",
    keys: [
      { key: "can_close_day", label: "Generar Cierre de Caja" },
      { key: "can_reopen_closure", label: "Reabrir Cierre de Caja" },
      { key: "can_manage_users", label: "Administrar Usuarios" },
      { key: "can_patch_settings", label: "Modificar Precios/Config" },
    ],
  },
];

function resetUserForm() {
  userForm.email = "";
  userForm.first_name = "";
  userForm.last_name = "";
  userForm.password = "";
  userForm.role = "MIXED";
  userForm.is_active = true;
  userForm.permission_overrides = {};
}

async function loadUsers() {
  users.value = await listUsers();
}

async function loadSettings() {
  const data = await getBusinessSettings();
  settings.default_range_unit_price_clp = data.default_range_unit_price_clp;
  settings.course_price_weekday_clp = data.course_price_weekday_clp;
  settings.course_price_weekend_clp = data.course_price_weekend_clp;
  settings.updated_at = data.updated_at;
}

async function loadAll() {
  error.value = "";
  try {
    await Promise.all([loadUsers(), loadSettings()]);
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo cargar configuración";
  }
}

function startEditSettings() {
  settingsEdit.course_price_weekday_clp = settings.course_price_weekday_clp;
  settingsEdit.course_price_weekend_clp = settings.course_price_weekend_clp;
  settingsEdit.default_range_unit_price_clp = settings.default_range_unit_price_clp;
  isEditingSettings.value = true;
}

function cancelEditSettings() {
  isEditingSettings.value = false;
  error.value = "";
}

async function saveSettings() {
  error.value = "";
  try {
    const data = await updateBusinessSettings({
      default_range_unit_price_clp: settingsEdit.default_range_unit_price_clp,
      course_price_weekday_clp: settingsEdit.course_price_weekday_clp,
      course_price_weekend_clp: settingsEdit.course_price_weekend_clp,
    });
    settings.default_range_unit_price_clp = data.default_range_unit_price_clp;
    settings.course_price_weekday_clp = data.course_price_weekday_clp;
    settings.course_price_weekend_clp = data.course_price_weekend_clp;
    settings.updated_at = data.updated_at;
    isEditingSettings.value = false;
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo guardar configuración";
  }
}

function openCreate() {
  editingId.value = null;
  resetUserForm();
  showUserForm.value = true;
}

function openEdit(user: UserAdmin) {
  editingId.value = user.id;
  userForm.email = user.email;
  userForm.first_name = user.first_name;
  userForm.last_name = user.last_name;
  userForm.password = "";
  userForm.role = user.role;
  userForm.is_active = user.is_active;
  userForm.permission_overrides = { ...(user.permission_overrides || {}) };
  showUserForm.value = true;
}

function cancelUserForm() {
  showUserForm.value = false;
  editingId.value = null;
}

function togglePermission(key: string, event: Event) {
  const checked = (event.target as HTMLInputElement).checked;
  userForm.permission_overrides[key] = checked;
}

async function saveUser() {
  error.value = "";
  const payload: Record<string, unknown> = {
    email: userForm.email,
    first_name: userForm.first_name,
    last_name: userForm.last_name,
    role: userForm.role,
    is_active: userForm.is_active,
    permission_overrides: userForm.permission_overrides,
  };

  if (userForm.password) payload.password = userForm.password;

  try {
    if (editingId.value) {
      await updateUser(editingId.value, payload);
    } else {
      await createUser(payload);
    }
    showUserForm.value = false;
    editingId.value = null;
    await loadUsers();
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo guardar usuario";
  }
}

const deleteTargetUserId = ref<number | null>(null);
const deletingUser = ref(false);

function askRemove(id: number) {
  deleteTargetUserId.value = id;
}

function cancelRemove() {
  if (deletingUser.value) return;
  deleteTargetUserId.value = null;
}

async function confirmRemove() {
  if (!deleteTargetUserId.value) return;

  error.value = "";
  deletingUser.value = true;
  try {
    await deleteUser(deleteTargetUserId.value);
    deleteTargetUserId.value = null;
    await loadUsers();
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo eliminar usuario";
  } finally {
    deletingUser.value = false;
  }
}

onMounted(loadAll);
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.header h1 {
  margin: 0;
  color: var(--minttu-text);
  font-size: 1.5rem;
}
.header p {
  margin: 4px 0 0;
  color: var(--minttu-gray);
}
.card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 32px;
  box-shadow: var(--minttu-shadow-soft);
}
.card h3 {
  margin-top: 0;
  color: var(--minttu-primary);
  border-bottom: 1px solid var(--minttu-border);
  padding-bottom: 8px;
  margin-bottom: 20px;
}
.row {
  display: grid;
  grid-template-columns: 1fr 200px;
  gap: 16px;
  align-items: center;
  margin-bottom: 12px;
}
.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--minttu-border);
  padding-bottom: 8px;
  margin-bottom: 20px;
}
.settings-header h3 {
  margin: 0;
  border: none;
  padding: 0;
}
.prices-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.price-card {
  background: var(--minttu-bg);
  padding: 16px;
  border-radius: var(--minttu-radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  border: 1px solid var(--minttu-border);
}
.price-label {
  font-size: 13px;
  color: var(--minttu-gray);
  margin-bottom: 4px;
}
.price-value {
  font-size: 20px;
  color: var(--minttu-primary);
  font-weight: 700;
}
.updated-at {
  display: block;
  margin-top: 12px;
  color: var(--minttu-gray);
  font-size: 12px;
  text-align: center;
}
.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}
th,
td {
  text-align: left;
  border-bottom: 1px solid var(--minttu-border);
  padding: 14px 16px;
  font-size: 14px;
}
th {
  background: var(--minttu-bg);
  color: var(--minttu-primary);
  font-weight: 600;
}
th:first-child {
  border-top-left-radius: 8px;
}
th:last-child {
  border-top-right-radius: 8px;
}
tbody tr:hover {
  background-color: var(--minttu-bg);
}
.action {
  border: none;
  background: var(--minttu-border);
  color: var(--minttu-primary);
  border-radius: 6px;
  padding: 6px 12px;
  margin-right: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}
.action:hover {
  background: var(--minttu-primary);
  color: var(--minttu-white);
}
.action.danger {
  background: #fef2f2;
  color: #dc2626;
}
.action.danger:hover {
  background: #dc2626;
  color: var(--minttu-white);
}
.form-grid {
  display: grid;
  gap: 8px;
}
input,
select {
  border: 1px solid var(--minttu-border);
  border-radius: var(--minttu-radius-sm);
  padding: 10px 14px;
  background: var(--minttu-white);
  color: var(--minttu-text);
  font-family: inherit;
  transition: all 0.2s ease;
}
input:focus,
select:focus {
  border-color: var(--minttu-primary);
  box-shadow: 0 0 0 3px rgba(27, 67, 50, 0.1);
  outline: none;
}
.permissions-grouped {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  background: var(--minttu-bg);
  padding: 16px;
  border-radius: var(--minttu-radius-md);
  border: 1px solid var(--minttu-border);
}
.perm-group h4 {
  margin-top: 0;
  margin-bottom: 8px;
  color: var(--minttu-primary);
  font-size: 14px;
}
.perm-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.switch-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  cursor: pointer;
}
.switch {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 20px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: var(--minttu-primary);
}
input:checked + .slider:before {
  transform: translateX(16px);
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
}
.empty {
  text-align: center;
  color: var(--minttu-gray);
}
.error {
  color: #c0392b;
}

@media (max-width: 1024px) {
  .prices-grid,
  .permissions-grouped {
    grid-template-columns: 1fr;
  }
  .row {
    grid-template-columns: 1fr;
  }
}
</style>
