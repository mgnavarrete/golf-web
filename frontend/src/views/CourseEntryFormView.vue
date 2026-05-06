<template>
  <div class="page">
    <div class="header">
      <button class="btn btn-secondary" @click="$router.push('/course-entries')">
        <i class="pi pi-arrow-left"></i> Volver
      </button>
      <h1>Nueva Entrada a Cancha</h1>
    </div>

    <section class="card">
      <CourseEntryForm :saving="saving" :error="error" submit-label="Guardar Entrada" @submit="submit" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import CourseEntryForm from "@/components/forms/CourseEntryForm.vue";
import { createCourseEntry, type CourseEntryPayload } from "@/services/golf";

const router = useRouter();

const saving = ref(false);
const error = ref("");

async function submit(payload: CourseEntryPayload) {
  saving.value = true;
  error.value = "";

  try {
    await createCourseEntry(payload);
    router.push("/course-entries");
  } catch (err: any) {
    error.value = err.response?.data?.detail || "No se pudo guardar";
    saving.value = false;
  }
}
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 600px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--minttu-text);
}

.card {
  background: var(--minttu-white);
  border: none;
  border-radius: var(--minttu-radius-lg);
  padding: 32px;
  box-shadow: var(--minttu-shadow-soft);
}
</style>
