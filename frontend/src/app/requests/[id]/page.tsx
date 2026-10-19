"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import api from "@/lib/api";
import { apiError, fetchMe, Me } from "@/lib/auth";
import { BloodRequest } from "@/components/RequestCard";

type Match = {
  donor_id: string;
  donor_name?: string;
  blood_group?: string;
  area?: string;
  score?: number;
  distance_km?: number;
  status?: string;
};

type Contact = { name: string; phone: string; status: string };

export default function RequestDetail() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [req, setReq] = useState<BloodRequest | null>(null);
  const [me, setMe] = useState<Me | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [myStatus, setMyStatus] = useState<string | null>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    const { data } = await api.get(`/requests/${id}`);
    setReq(data);
  }

  useEffect(() => {
    if (!localStorage.getItem("access_token")) { router.replace("/login"); return; }
    load().catch((e) => setMsg(apiError(e)));
    fetchMe().then(setMe).catch(() => {});
    api.get("/matching/inbox")
      .then(({ data }) => setMyStatus(data.find((x: any) => x.request_id === id)?.status ?? null))
      .catch(() => {});
  }, [id]);

  useEffect(() => {
    if (!me || !req) return;
    const owner = req.requester_id === me.id;
    if (!owner && myStatus !== "accepted") return;
    api.get(`/matching/${id}/contacts`)
      .then(({ data }) => setContacts(data.contacts ?? []))
      .catch(() => {});
  }, [me, req, myStatus, id]);

  async function runMatch() {
    setBusy(true); setMsg("");
    try {
      const { data } = await api.post(`/matching/${id}/match`);
      const list: Match[] = data.donors ?? [];
      setMatches(list);
      setMsg(list.length === 0 ? "No eligible donors found nearby yet." : `Matched ${list.length} donor(s).`);
    } catch (e) { setMsg(apiError(e)); } finally { setBusy(false); }
  }

  async function respond(action: "accept" | "decline" | "snooze") {
    setBusy(true); setMsg("");
    try {
      await api.post(`/matching/${id}/respond`, null, { params: { action } });
      setMsg(`You chose to ${action}.`);
      setMyStatus(action === "accept" ? "accepted" : action === "decline" ? "declined" : "snoozed");
      await load();
    } catch (e) { setMsg(apiError(e)); } finally { setBusy(false); }
  }

  async function cancel() {
    if (!confirm("Cancel this request?")) return;
    try { await api.patch(`/requests/${id}/cancel`); await load(); } catch (e) { setMsg(apiError(e)); }
  }

  if (!req) return <p className="p-8">{msg || "Loading..."}</p>;
  const isOwner = !!me && req.requester_id === me.id;
  const open = req.status === "open" || req.status === "partially_fulfilled";

  return (
    <div className="mx-auto max-w-2xl space-y-5 px-4 py-8">
      <div className="card">
        <div className="flex items-center justify-between">
          <span className="text-4xl font-bold text-primary-600">{req.blood_group_needed}</span>
          <span className={`badge-${req.urgency}`}>{req.urgency}</span>
        </div>
        <p className="mt-3 font-semibold">{req.hospital_name}</p>
        <p className="text-sm text-gray-600">
          {req.units_fulfilled}/{req.units_needed} unit(s) · {req.status.replace("_", " ")}
        </p>
        <p className="text-sm mt-1">Patient: {req.patient_name}</p>
        <p className="text-xs text-gray-400 mt-2">
          Expires {new Date(req.expires_at).toLocaleString()}
        </p>
      </div>

      {msg && <p className="text-sm text-gray-700">{msg}</p>}

      {open && isOwner && (
        <div className="flex gap-3">
          <button className="btn-primary" onClick={runMatch} disabled={busy}>
            {busy ? "Matching..." : "Find matching donors"}
          </button>
          <button className="btn-secondary" onClick={cancel}>Cancel request</button>
        </div>
      )}

      {open && me && !isOwner && myStatus && myStatus !== "notified" && (
        <p className="text-sm text-gray-700">Your response: <b>{myStatus}</b></p>
      )}

      {open && me && !isOwner && myStatus === "notified" && (
        <div className="card">
          <p className="font-medium mb-3">Can you help with this request?</p>
          <div className="flex gap-3">
            <button className="btn-primary" onClick={() => respond("accept")} disabled={busy}>Accept</button>
            <button className="btn-secondary" onClick={() => respond("snooze")} disabled={busy}>Later</button>
            <button className="btn-secondary" onClick={() => respond("decline")} disabled={busy}>Decline</button>
          </div>
        </div>
      )}

      {contacts.length > 0 && (
        <section className="card">
          <h2 className="text-lg font-semibold mb-2">
            {isOwner ? "Donors who accepted" : "Requester contact"}
          </h2>
          <ul className="space-y-2 text-sm">
            {contacts.map((c, i) => (
              <li key={i} className="flex justify-between">
                <span>{c.name}</span>
                <a href={`tel:${c.phone}`} className="text-primary-600 underline">{c.phone}</a>
              </li>
            ))}
          </ul>
        </section>
      )}

      {matches.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-2">Ranked donors</h2>
          <ol className="space-y-2">
            {matches.map((m, i) => (
              <li key={m.donor_id} className="card flex justify-between text-sm">
                <span>#{i + 1} {m.donor_name} {m.blood_group && `· ${m.blood_group}`} {m.area && `· ${m.area}`}</span>
                <span className="text-gray-600">
                  {m.distance_km != null && `${m.distance_km.toFixed(1)} km · `}
                  score {m.score?.toFixed(0) ?? "-"}{m.status && ` · ${m.status}`}
                </span>
              </li>
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}
