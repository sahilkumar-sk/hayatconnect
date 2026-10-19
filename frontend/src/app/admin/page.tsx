"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { apiError, fetchMe } from "@/lib/auth";

type Stats = {
  total_users: number;
  users_by_role: Record<string, number>;
  available_donors: number;
  total_requests: number;
  requests_last_7_days: number;
  requests_by_status: Record<string, number>;
  requests_by_urgency: Record<string, number>;
  requests_by_blood_group: Record<string, number>;
  units_needed: number;
  units_fulfilled: number;
  fulfilment_rate: number;
  responses_by_status: Record<string, number>;
  acceptance_rate: number;
  recent_requests: {
    id: string;
    blood_group: string;
    hospital_name: string;
    urgency: string;
    status: string;
    units_needed: number;
    units_fulfilled: number;
    created_at: string | null;
  }[];
};

function StatCard({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <div className="card">
      <p className="text-sm text-gray-600">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
    </div>
  );
}

function Breakdown({ title, data }: { title: string; data: Record<string, number> }) {
  const rows = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = Math.max(1, ...rows.map(([, n]) => n));
  return (
    <div className="card">
      <h2 className="font-semibold mb-3">{title}</h2>
      {rows.length === 0 ? (
        <p className="text-sm text-gray-500">No data yet.</p>
      ) : (
        <ul className="space-y-2">
          {rows.map(([k, n]) => (
            <li key={k} className="text-sm">
              <div className="flex justify-between">
                <span>{k.replace("_", " ")}</span>
                <span className="text-gray-600">{n}</span>
              </div>
              <div className="h-2 rounded bg-gray-100 mt-1">
                <div className="h-2 rounded bg-red-600" style={{ width: `${(n / max) * 100}%` }} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function AdminDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("access_token")) { router.replace("/login"); return; }
    (async () => {
      try {
        const me = await fetchMe();
        if (me.role !== "admin") { router.replace("/dashboard"); return; }
        const { data } = await api.get("/admin/stats");
        setStats(data);
      } catch (e) {
        setError(apiError(e));
      }
    })();
  }, [router]);

  if (error) return <p className="p-8 text-red-600">{error}</p>;
  if (!stats) return <p className="p-8">Loading...</p>;

  return (
    <div className="max-w-5xl mx-auto space-y-6 px-4 py-6">
      <div className="flex items-center justify-between"><h1 className="text-2xl font-bold">Admin dashboard</h1><Link href="/admin/users" className="btn-secondary">Manage users</Link></div>

      <div className="grid gap-4 grid-cols-2 md:grid-cols-3">
        <StatCard label="Total users" value={stats.total_users}
          hint={Object.entries(stats.users_by_role).map(([r, n]) => `${n} ${r}`).join(" · ")} />
        <StatCard label="Available donors" value={stats.available_donors} />
        <StatCard label="Total requests" value={stats.total_requests}
          hint={`${stats.requests_last_7_days} in the last 7 days`} />
        <StatCard label="Fulfilment rate" value={`${stats.fulfilment_rate}%`}
          hint={`${stats.units_fulfilled} of ${stats.units_needed} units`} />
        <StatCard label="Donor acceptance rate" value={`${stats.acceptance_rate}%`}
          hint="Of donors who responded" />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Breakdown title="Requests by status" data={stats.requests_by_status} />
        <Breakdown title="Requests by urgency" data={stats.requests_by_urgency} />
        <Breakdown title="Requests by blood group" data={stats.requests_by_blood_group} />
        <Breakdown title="Donor responses" data={stats.responses_by_status} />
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-3">Recent requests</h2>
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="text-left text-gray-600">
              <tr>
                <th className="p-3">Blood</th>
                <th className="p-3">Hospital</th>
                <th className="p-3">Urgency</th>
                <th className="p-3">Status</th>
                <th className="p-3">Units</th>
                <th className="p-3">Created</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_requests.map((r) => (
                <tr key={r.id} className="border-t">
                  <td className="p-3 font-semibold text-red-600">
                    <Link href={`/requests/${r.id}`}>{r.blood_group}</Link>
                  </td>
                  <td className="p-3">{r.hospital_name}</td>
                  <td className="p-3"><span className={`badge-${r.urgency}`}>{r.urgency}</span></td>
                  <td className="p-3">{r.status.replace("_", " ")}</td>
                  <td className="p-3">{r.units_fulfilled}/{r.units_needed}</td>
                  <td className="p-3 text-gray-500">
                    {r.created_at ? new Date(r.created_at).toLocaleString() : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}


