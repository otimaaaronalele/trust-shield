import type { TxPayload, BackendResponse } from "./types";

export async function callBackend(
  payload: TxPayload,
  useMock: boolean,
  apiUrl: string
): Promise<BackendResponse> {
  if (useMock) {
    const old = payload.oldbalanceOrg;
    const ratio = old > 0 ? payload.amount / old : 0;
    const flagged = ratio > 0.98;
    return {
      action_routing: flagged ? "HARD_INTERCEPT_ESCROW" : "SETTLE_IMMEDIATELY",
      fraud_probability: flagged ? 0.92 : 0.04,
      system_latency_ms: 0.0,
      plain_language_brief: "MOCK RESPONSE: replace with the real backend.",
    };
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);
  try {
    const res = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    if (!res.ok) {
      throw new Error(`${res.status} ${res.statusText}`);
    }
    return (await res.json()) as BackendResponse;
  } finally {
    clearTimeout(timeout);
  }
}

export async function testConnection(apiUrl: string): Promise<boolean> {
  const base = apiUrl.split("/api/")[0];
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 3000);
  try {
    await fetch(base + "/docs", { signal: controller.signal });
    return true;
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
}
