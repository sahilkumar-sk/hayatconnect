"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import api from "@/lib/api";
import { fetchMe, logout } from "@/lib/auth";

export default function Navbar() {
  const pathname = usePathname();
  const [loggedIn, setLoggedIn] = useState(false);
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(0);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const has = !!localStorage.getItem("access_token");
    setLoggedIn(has);
    setOpen(false);
    if (!has) { setPending(0); setIsAdmin(false); return; }
    fetchMe().then((m) => setIsAdmin(m.role === "admin")).catch(() => setIsAdmin(false));
    api
      .get("/matching/inbox")
      .then(({ data }) => {
        const list = Array.isArray(data) ? data : data.items ?? [];
        setPending(list.filter((m: any) => m.status === "notified").length);
      })
      .catch(() => setPending(0));
  }, [pathname]);

  const Badge = () =>
    pending > 0 ? (
      <span className="ml-1 inline-flex items-center justify-center rounded-full bg-red-600 text-white text-xs font-semibold min-w-[1.25rem] h-5 px-1">
        {pending}
      </span>
    ) : null;

  const links = (
    <>
      <Link href="/requests/new" className="hover:text-red-600">Request Blood</Link>
      <Link href="/requests" className="hover:text-red-600">Find Donors</Link>
      {loggedIn && (
        <Link href="/inbox" className="hover:text-red-600 inline-flex items-center">
          My matches<Badge />
        </Link>
      )}
      {loggedIn ? (
        <>
          {isAdmin && <Link href="/admin" className="hover:text-red-600">Admin</Link>}
          <Link href="/dashboard" className="hover:text-red-600">Dashboard</Link>
          <button onClick={logout} className="btn-secondary">Log out</button>
        </>
      ) : (
        <>
          <Link href="/login" className="hover:text-red-600">Log in</Link>
          <Link href="/register" className="btn-primary">Register</Link>
        </>
      )}
    </>
  );

  return (
    <nav className="bg-white border-b">
      <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold flex items-center gap-2"><svg width="22" height="28" viewBox="0 0 24 30" fill="#e11d48"><path d="M12 0C12 0 0 14 0 20a12 12 0 0024 0C24 14 12 0 12 0z"/></svg>
          <span><span className="text-red-600">Hayat</span>Connect</span>
        </Link>
        <div className="hidden md:flex items-center gap-6 text-sm">{links}</div>
        <button className="md:hidden p-2" onClick={() => setOpen(!open)} aria-label="Menu">
          {open ? "✕" : "☰"}
        </button>
      </div>
      {open && <div className="md:hidden flex flex-col gap-4 px-4 pb-4 text-sm">{links}</div>}
    </nav>
  );
}



