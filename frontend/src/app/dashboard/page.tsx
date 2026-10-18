"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { fetchMe, Me } from "@/lib/auth";
import RequestCard, { BloodRequest } from "@/components/RequestCard";

export default function Dashboard() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [mine, setMine] = useState<BloodRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [locMsg, setLocMsg] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("access_token")) { router.replace("/login"); return; }
    (async () => {
      try {
        const user = await fetchMe();
        setMe(user);
        const { data } = await api.get("/requests/", { params: { requester_id: user.id } });
        setMine(Array.isArray(data) ? data : data.items ?? []);
      } finally {
        setLoading(false);
      }
    })();
  }, [router]);

  async function toggleAvailability() {
    if (!me) return;
    const { data } = await api.patch("/donors/me/availability", { is_available: !me.is_available });
    setMe({ ...me, is_available: data.is_available ?? !me.is_available });
  }

  function updateLocation() {
    setLocMsg("Getting location...");
    navigator.geolocation.getCurrentPosition(
      async (p) => {
        try {
          await api.patch("/donors/me", { latitude: p.coords.latitude, longitude: p.coords.longitude });
          setLocMsg("Location updated ✓");
        } catch {
          setLocMsg("Could not save location.");
        }
      },
      () => setLocMsg("Location permission denied."),
      { timeout: 8000 }
    );
  }

  if (loading) return <p className="p-8">Loading...</p>;
  if (!me) return null;

  return (
    <div className="mx-auto max-w-5xl space-y-6 px-4 py-8">
      <div>
        <h1 className="text-2xl font-bold">Salam, {me.name}</h1>
        <p className="text-sm text-gray-600">
          {me.role} {me.blood_group && `· ${me.blood_group}`} {me.area && `· ${me.area}`}
        </p>
      </div>

      {me.role === "donor" && (
        <div className="card flex items-center justify-between">
          <div>
            <p className="font-medium">Donor availability</p>
            <p className="text-sm text-gray-600">
              Reliability score: {me.reliability_score ?? 50}/100
            </p>
            <button onClick={updateLocation} className="mt-2 text-sm text-primary-600 underline">
              Update my location
            </button>
            {locMsg && <p className="text-xs text-gray-500">{locMsg}</p>}
          </div>
          <button onClick={toggleAvailability} className={me.is_available ? "btn-primary" : "btn-secondary"}>
            {me.is_available ? "Available" : "Unavailable"}
          </button>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <Link href="/requests/new" className="btn-primary">+ New blood request</Link>
        <Link href="/requests" className="btn-secondary">Browse open requests</Link>
        {me.role === "donor" && <Link href="/inbox" className="btn-secondary">My matches</Link>}
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-3">My requests</h2>
        {mine.length === 0 ? (
          <p className="text-gray-500">No requests yet.</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {mine.map((r) => <RequestCard key={r.id} r={r} />)}
          </div>
        )}
      </section>
    </div>
  );
}
