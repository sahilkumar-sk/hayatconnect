import api from "@/lib/api";

export type Me = {
  id: string;
  name: string;
  phone: string;
  email?: string;
  role: "donor" | "requester" | "admin";
  blood_group?: string;
  area?: string;
  is_available?: boolean;
  reliability_score?: number;
};

export function saveTokens(t: { access_token: string; refresh_token: string }) {
  localStorage.setItem("access_token", t.access_token);
  localStorage.setItem("refresh_token", t.refresh_token);
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
}

export async function fetchMe(): Promise<Me> {
  const { data } = await api.get("/donors/me");
  return data;
}

export function apiError(e: any): string {
  const d = e?.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d))
    return d.map((x) => `${(x.loc || []).slice(1).join(".")}: ${x.msg}`).join(", ");
  return "Something went wrong. Please try again.";
}