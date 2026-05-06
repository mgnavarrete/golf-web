<template>
  <RouterView v-if="shouldShowWithoutLayout" />

  <AppLayout v-else @logout="onLogout">
    <RouterView />
  </AppLayout>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import AppLayout from "@/layouts/AppLayout.vue";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const auth = useAuthStore();

const shouldShowWithoutLayout = computed(() => {
  return (
    route.path === "/login" ||
    route.path === "/help" ||
    route.path === "/health" ||
    route.meta.isNotFound === true ||
    route.meta.hideLayout === true
  );
});

function onLogout() {
  auth.logout();
  window.location.replace("/login");
}
</script>
