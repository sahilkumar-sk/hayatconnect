import Link from "next/link";

export type BloodRequest = {
  id: string;
  requester_id: string;
  patient_name: string;
  blood_group_needed: string;
  units_needed: number;
  units_fulfilled: number;
  urgency: "routine" | "urgent" | "emergency";
  status: string;
  hospital_name: string;
  created_at: string;
  expires_at: string;
};

export default function RequestCard({ r }: { r: BloodRequest }) {
  return (
    <Link href={`/requests/${r.id}`} className="card block hover:shadow-md transition">
      <div className="flex items-center justify-between">
        <span className="text-2xl font-bold text-primary-600">{r.blood_group_needed}</span>
        <span className={`badge-${r.urgency}`}>{r.urgency}</span>
      </div>
      <p className="mt-2 font-medium">{r.hospital_name}</p>
      <p className="text-sm text-gray-600">
        {r.units_fulfilled}/{r.units_needed} unit(s) · {r.status.replace("_", " ")}
      </p>
      <p className="text-xs text-gray-400 mt-1">{new Date(r.created_at).toLocaleString()}</p>
    </Link>
  );
}