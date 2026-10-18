"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { saveTokens, apiError } from "@/lib/auth";

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

export default function RegisterPage() {
  const router = useRouter();
  const [f, setF] = useState({
    name: "", phone: "+92", email: "", password: "",
    role: "requester", blood_group: "", area: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const set = (k: string) => (e: any) => setF({ ...f, [k]: e.target.value });

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const body: any = { ...f };
      if (!body.email) delete body.email;
      if (!body.blood_group) delete body.blood_group;
      await new Promise<void>((res) =>
        navigator.geolocation
          ? navigator.geolocation.getCurrentPosition(
              (p) => { body.latitude = p.coords.latitude; body.longitude = p.coords.longitude; res(); },
              () => res(), { timeout: 4000 })
          : res()
      );
      const { data } = await api.post("/auth/register", body);
      saveTokens(data);
      router.push("/dashboard");
    } catch (err) {
      setError(apiError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-4 py-8">
      <div className="card">
        <h1 className="text-2xl font-bold mb-4">Create account</h1>
        <form onSubmit={submit} className="space-y-4">
          <input className="input-field" placeholder="Full name" value={f.name} onChange={set("name")} required />
          <input className="input-field" placeholder="+923001234567" value={f.phone} onChange={set("phone")} required />
          <input className="input-field" type="email" placeholder="Email (optional)" value={f.email} onChange={set("email")} />
          <input className="input-field" type="password" minLength={8} placeholder="Password (8+ chars)" value={f.password} onChange={set("password")} required />
          <select className="input-field" value={f.role} onChange={set("role")}>
            <option value="requester">I need blood (requester)</option>
            <option value="donor">I want to donate (donor)</option>
          </select>
          <select className="input-field" value={f.blood_group} onChange={set("blood_group")} required={f.role === "donor"}>
            <option value="">Blood group{f.role === "donor" ? "" : " (optional)"}</option>
            {BLOOD_GROUPS.map((g) => <option key={g}>{g}</option>)}
          </select>
          <input className="input-field" placeholder="Area (e.g. Saddar)" value={f.area} onChange={set("area")} />
          <p className="text-xs text-gray-500">We use your device location (if allowed) to match nearby donors.</p>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button className="btn-primary w-full" disabled={loading}>
            {loading ? "Creating..." : "Register"}
          </button>
        </form>
        <p className="text-sm mt-4">
          Already registered? <Link href="/login" className="text-primary-600 underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}