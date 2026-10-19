"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { apiError, fetchMe } from "@/lib/auth";

type AdminUser = {
  id: string;
  name: string;
  phone: string;
  email?: string | null;
  role: string;
  blood_group?: string | null;
  area?: string | null;
  is_available: boolean;
  is_phone_verified: boolean;
  is_active: boolean;
  ban_reason?: string | null;
  reliability_score?: number | null;
  last_donation_date?: string | null;
  created_at?: string | null;
};

export default function AdminUsers() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("access_token")) { router.replace("/login"); return; }
    fetchMe()
      .then((me) => {
        if (me.role !== "admin") router.replace("/dashboard");
        else setReady(true);
      })
      .catch((e) => setError(apiError(e)));
  }, [router]);

  useEffect(() => {
    if (!ready) return;
    setLoading(true);
    const timer = setTimeout(() => {
      api
        .get("/admin/users", { params: { search: search || undefined, role: role || undefined } })
        .then(({ data }) => { setUsers(data); setError(""); })
        .catch((e) => setError(apiError(e)))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [ready, search, role]);

  async function toggleVerify(id: string) {
    try {
      const { data } = await api.patch(`/admin/users/${id}/verify`);
      setUsers((list) => list.map((u) => (u.id === id ? { ...u, is_phone_verified: data.is_phone_verified } : u)));
    } catch (e) {
      setError(apiError(e));
    }
  }

  async function toggleBan(u: AdminUser) {
    try {
      if (u.is_active) {
        const reason = window.prompt(`Reason for banning ${u.name}?`);
        if (!reason) return;
        await api.post(`/admin/users/${u.id}/ban`, null, { params: { reason } });
        setUsers((list) =>
          list.map((x) => (x.id === u.id ? { ...x, is_active: false, ban_reason: reason, is_available: false } : x))
        );
      } else {
        await api.post(`/admin/users/${u.id}/unban`);
        setUsers((list) => list.map((x) => (x.id === u.id ? { ...x, is_active: true, ban_reason: null } : x)));
      }
    } catch (e) {
      setError(apiError(e));
    }
  }

  if (!ready && !error) return <p className="p-8">Loading...</p>;

  return (
    <div className="max-w-5xl mx-auto space-y-5 px-4 py-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Users</h1>
        <Link href="/admin" className="btn-secondary">Back to dashboard</Link>
      </div>

      <div className="flex gap-3">
        <input
          className="input-field"
          placeholder="Search name, phone or email"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select className="input-field" value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="">All roles</option>
          <option value="donor">Donor</option>
          <option value="requester">Requester</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="text-left text-gray-600">
            <tr>
              <th className="p-3">User</th>
              <th className="p-3">Role</th>
              <th className="p-3">Blood</th>
              <th className="p-3">Area</th>
              <th className="p-3">Reliability</th>
              <th className="p-3">Verified</th>
              <th className="p-3">Joined</th>
              <th className="p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td className="p-3 text-gray-500" colSpan={8}>Loading...</td></tr>
            ) : users.length === 0 ? (
              <tr><td className="p-3 text-gray-500" colSpan={8}>No users match.</td></tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} className="border-t">
                  <td className="p-3">
                    <p className="font-medium">{u.name}</p>
                    <p className="text-xs text-gray-500">{u.phone}{u.email ? ` · ${u.email}` : ""}</p>
                    {!u.is_active && (
                      <p className="text-xs text-red-600">Banned{u.ban_reason ? `: ${u.ban_reason}` : ""}</p>
                    )}
                  </td>
                  <td className="p-3">{u.role}</td>
                  <td className="p-3 font-semibold text-red-600">{u.blood_group ?? "-"}</td>
                  <td className="p-3">{u.area ?? "-"}</td>
                  <td className="p-3">{u.reliability_score != null ? `${u.reliability_score}/100` : "-"}</td>
                  <td className="p-3">
                    <button
                      onClick={() => toggleVerify(u.id)}
                      className={u.is_phone_verified ? "btn-primary" : "btn-secondary"}
                    >
                      {u.is_phone_verified ? "Verified" : "Verify"}
                    </button>
                  </td>
                  <td className="p-3 text-gray-500">
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : "-"}
                  </td>
                  <td className="p-3">
                    {u.role === "admin" ? (
                      <span className="text-xs text-gray-400">-</span>
                    ) : (
                      <button onClick={() => toggleBan(u)} className="btn-secondary">
                        {u.is_active ? "Ban" : "Unban"}
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
