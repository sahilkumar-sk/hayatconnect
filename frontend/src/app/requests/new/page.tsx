"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { apiError } from "@/lib/auth";

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

export default function NewRequest() {
  const router = useRouter();
  const [f, setF] = useState({
    patient_name: "", blood_group_needed: "O+", units_needed: 1, urgency: "urgent",
    hospital_name: "", hospital_address: "", contact_phone: "+92", notes: "",
  });
  const [coords, setCoords] = useState<{ hospital_latitude?: number; hospital_longitude?: number }>({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const set = (k: string) => (e: any) => setF({ ...f, [k]: e.target.value });

  function locate() {
    navigator.geolocation?.getCurrentPosition(
      (p) => setCoords({ hospital_latitude: p.coords.latitude, hospital_longitude: p.coords.longitude }),
      () => setError("Could not get location. Allow location access and retry.")
    );
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const body: any = { ...f, units_needed: Number(f.units_needed), ...coords };
      if (!body.hospital_address) delete body.hospital_address;
      if (!body.notes) delete body.notes;
      const { data } = await api.post("/requests/", body);
      router.push(`/requests/${data.id}`);
    } catch (err) {
      setError(apiError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-8">
      <div className="card">
        <h1 className="text-2xl font-bold mb-4">New blood request</h1>
        <form onSubmit={submit} className="space-y-4">
          <input className="input-field" placeholder="Patient name" value={f.patient_name} onChange={set("patient_name")} required />
          <div className="grid grid-cols-2 gap-3">
            <select className="input-field" value={f.blood_group_needed} onChange={set("blood_group_needed")}>
              {BLOOD_GROUPS.map((g) => <option key={g}>{g}</option>)}
            </select>
            <input className="input-field" type="number" min={1} max={10} value={f.units_needed} onChange={set("units_needed")} />
          </div>
          <select className="input-field" value={f.urgency} onChange={set("urgency")}>
            <option value="routine">Routine (72h)</option>
            <option value="urgent">Urgent (48h)</option>
            <option value="emergency">Emergency (24h)</option>
          </select>
          <input className="input-field" placeholder="Hospital (e.g. JPMC)" value={f.hospital_name} onChange={set("hospital_name")} required />
          <input className="input-field" placeholder="Hospital address / area" value={f.hospital_address} onChange={set("hospital_address")} />
          <input className="input-field" placeholder="Contact phone +92..." value={f.contact_phone} onChange={set("contact_phone")} required />
          <textarea className="input-field" rows={3} placeholder="Notes (ward, bed, attendant name)" value={f.notes} onChange={set("notes")} />
          <button type="button" onClick={locate} className="btn-secondary w-full">
            {coords.hospital_latitude ? "Location captured ✓" : "Use hospital/my current location"}
          </button>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button className="btn-primary w-full" disabled={loading}>
            {loading ? "Submitting..." : "Submit request"}
          </button>
        </form>
      </div>
    </div>
  );
}