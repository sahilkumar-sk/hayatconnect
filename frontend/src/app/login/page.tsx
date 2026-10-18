"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { saveTokens, apiError } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [phone, setPhone] = useState("+92");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", { phone, password });
      saveTokens(data);
      router.push("/dashboard");
    } catch (err) {
      setError(apiError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto mt-10 card">
      <h1 className="text-2xl font-bold mb-4">Log in</h1>
      <form onSubmit={submit} className="space-y-4">
        <input className="input-field" placeholder="+923001234567" value={phone}
          onChange={(e) => setPhone(e.target.value)} required />
        <input className="input-field" type="password" placeholder="Password" value={password}
          onChange={(e) => setPassword(e.target.value)} required />
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button className="btn-primary w-full" disabled={loading}>
          {loading ? "Logging in..." : "Log in"}
        </button>
      </form>
      <p className="text-sm mt-4">
        New here? <Link href="/register" className="text-primary-600 underline">Create an account</Link>
      </p>
    </div>
  );
}