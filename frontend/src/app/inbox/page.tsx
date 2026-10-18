"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

type Item = {
  response_id: string;
  request_id: string;
  status: string;
  blood_group_needed: string;
  hospital_name: string;
  urgency: "routine" | "urgent" | "emergency";
  units_needed: number;
  units_fulfilled: number;
  request_status: string;
  expires_at: string;
};

export default function Inbox() {
  const router = useRouter();
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem("access_token")) { router.replace("/login"); return; }
    api.get("/matching/inbox")
      .then(({ data }) => setItems(data))
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <div className="mx-auto max-w-3xl space-y-4 px-4 py-8">
      <h1 className="text-2xl font-bold">My matches</h1>
      <p className="text-sm text-gray-600">Requests where you were picked as a suitable donor.</p>
      {loading ? <p>Loading...</p> : items.length === 0 ? (
        <p className="text-gray-500">No matches yet. We'll list requests here when you're a fit.</p>
      ) : (
        <div className="space-y-3">
          {items.map((i) => (
            <Link key={i.response_id} href={`/requests/${i.request_id}`} className="card flex items-center justify-between hover:shadow-md transition">
              <div>
                <span className="text-2xl font-bold text-primary-600">{i.blood_group_needed}</span>
                <p className="font-medium">{i.hospital_name}</p>
                <p className="text-sm text-gray-600">
                  {i.units_fulfilled}/{i.units_needed} unit(s) · {i.request_status.replace("_", " ")}
                </p>
              </div>
              <div className="text-right">
                <span className={`badge-${i.urgency}`}>{i.urgency}</span>
                <p className="mt-2 text-sm font-medium">
                  {i.status === "notified" ? "Awaiting your reply" : `You: ${i.status}`}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}