"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import RequestCard, { BloodRequest } from "@/components/RequestCard";

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

export default function BrowseRequests() {
  const [items, setItems] = useState<BloodRequest[]>([]);
  const [group, setGroup] = useState("");
  const [urgency, setUrgency] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .get("/requests/", {
        params: {
          blood_group: group || undefined,
          urgency: urgency || undefined,
        },
      })
      .then(({ data }) => setItems(Array.isArray(data) ? data : data.items ?? []))
      .finally(() => setLoading(false));
  }, [group, urgency]);

  return (
    <div className="mx-auto max-w-5xl space-y-4 px-4 py-8">
      <h1 className="text-2xl font-bold">Open blood requests</h1>
      <div className="flex gap-3">
        <select className="input-field" value={group} onChange={(e) => setGroup(e.target.value)}>
          <option value="">All blood groups</option>
          {BLOOD_GROUPS.map((g) => <option key={g}>{g}</option>)}
        </select>
        <select className="input-field" value={urgency} onChange={(e) => setUrgency(e.target.value)}>
          <option value="">Any urgency</option>
          <option value="emergency">Emergency</option>
          <option value="urgent">Urgent</option>
          <option value="routine">Routine</option>
        </select>
      </div>
      {loading ? (
        <p>Loading...</p>
      ) : items.length === 0 ? (
        <p className="text-gray-500">No open requests match.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {items.map((r) => <RequestCard key={r.id} r={r} />)}
        </div>
      )}
    </div>
  );
}
