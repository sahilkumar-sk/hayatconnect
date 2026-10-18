"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();
  const [loggedIn, setLoggedIn] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    try { setLoggedIn(!!localStorage.getItem("access_token")); } catch { setLoggedIn(false); }
    setOpen(false);
  }, [pathname]);

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
  }

  const links = [
    { href: "/requests/new", label: "Request Blood" },
    { href: "/requests", label: "Find Donors" },
    ...(loggedIn ? [{ href: "/inbox", label: "My matches" }, { href: "/dashboard", label: "Dashboard" }] : []),
  ];

  return (
    <header className="border-b border-gray-200 bg-white">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2 text-xl font-bold">
          <svg width="22" height="28" viewBox="0 0 22 28" aria-hidden="true">
            <path d="M11 0C11 0 0 12 0 18a11 11 0 0022 0C22 12 11 0 11 0z" fill="#e11d48" />
          </svg>
          <span><span className="text-primary-600">Hayat</span>Connect</span>
        </Link>

        <div className="hidden items-center gap-6 md:flex">
          {links.map((l) => (
            <Link key={l.href} href={l.href}
              className={`text-sm hover:text-primary-600 ${pathname === l.href ? "font-semibold text-primary-600" : "text-gray-700"}`}>
              {l.label}
            </Link>
          ))}
          {loggedIn ? (
            <button onClick={logout} className="btn-secondary">Log out</button>
          ) : (
            <>
              <Link href="/login" className="btn-secondary">Log In</Link>
              <Link href="/register" className="btn-primary">Register</Link>
            </>
          )}
        </div>

        <button className="md:hidden" onClick={() => setOpen(!open)} aria-label="Menu">
          <span className="text-2xl">{open ? "✕" : "☰"}</span>
        </button>
      </nav>

      {open && (
        <div className="space-y-3 border-t border-gray-200 px-4 py-4 md:hidden">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="block text-gray-700">{l.label}</Link>
          ))}
          {loggedIn ? (
            <button onClick={logout} className="btn-secondary w-full">Log out</button>
          ) : (
            <div className="flex gap-3">
              <Link href="/login" className="btn-secondary flex-1 text-center">Log In</Link>
              <Link href="/register" className="btn-primary flex-1 text-center">Register</Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
