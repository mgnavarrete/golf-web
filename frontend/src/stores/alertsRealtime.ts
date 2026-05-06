import { defineStore } from "pinia";
import { api } from "@/lib/api";

interface LatestAlertsResponse {
  results: Array<{
    id: number;
    status?: string;
    updated_at?: string | null;
  }>;
}

const DEFAULT_POLL_INTERVAL_MS = 10000;
const REALTIME_SIGNATURE_PAGE_SIZE = 20;

export const useAlertsRealtimeStore = defineStore("alertsRealtime", {
  state: () => ({
    refreshTick: 0,
    latestAlertsSignature: null as string | null,
    pollingIntervalId: null as number | null,
    isChecking: false,
    hasBootstrapped: false,
  }),

  actions: {
    async fetchLatestAlertsSignature(): Promise<string> {
      const { data } = await api.get<LatestAlertsResponse>("/api/alerts/", {
        params: {
          page: 1,
          page_size: REALTIME_SIGNATURE_PAGE_SIZE,
          ordering: "-detected_at",
        },
      });

      return data.results
        .map((alert) => `${alert.id}:${alert.status || ""}:${alert.updated_at || ""}`)
        .join("|");
    },

    async checkForUpdates() {
      if (this.isChecking) return;
      this.isChecking = true;

      try {
        const signature = await this.fetchLatestAlertsSignature();
        const hasChanged = this.latestAlertsSignature !== signature;
        this.latestAlertsSignature = signature;

        if (this.hasBootstrapped && hasChanged) {
          this.refreshTick += 1;
        }

        if (!this.hasBootstrapped) {
          this.hasBootstrapped = true;
        }
      } catch (error) {
        console.error("[Realtime] Error checking alerts updates:", error);
      } finally {
        this.isChecking = false;
      }
    },

    startPolling(intervalMs: number = DEFAULT_POLL_INTERVAL_MS) {
      if (this.pollingIntervalId !== null) return;

      void this.checkForUpdates();

      this.pollingIntervalId = window.setInterval(() => {
        void this.checkForUpdates();
      }, intervalMs);
    },

    stopPolling() {
      if (this.pollingIntervalId !== null) {
        window.clearInterval(this.pollingIntervalId);
        this.pollingIntervalId = null;
      }

      this.isChecking = false;
      this.hasBootstrapped = false;
      this.latestAlertsSignature = null;
    },

    notifyDataChanged() {
      this.refreshTick += 1;
    },
  },
});
