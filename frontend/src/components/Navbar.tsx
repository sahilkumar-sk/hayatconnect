"use client";

import { useState } from "react";
import Link from "next/link";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl">🩸</span>
          <span className="text-xl font-bold text-primary-600">
            Hayat<span className="text-gray-900">Connect</span>
          </span>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden items-center gap-6 md:flex">
          <Link href="/request" className="text-sm font-medium text-gray-700 hover:text-primary-600">
            Request Blood
          </Link>
          <Link href="/donors" className="text-sm font-medium text-gray-700 hover:text-primary-600">
            Find Donors
          </Link>
          <Link href="/dashboard" className="text-sm font-medium text-gray-700 hover:text-primary-600">
            Dashboard
          </Link>
          <Link href="/login" className="btn-secondary text-sm">
            Log In
          </Link>
          <Link href="/register" className="btn-primary text-sm">
            Register
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          <svg className="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {menuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="border-t border-gray-100 bg-white px-4 pb-4 md:hidden">
          <div className="flex flex-col gap-3 pt-3">
            <Link href="/request" className="text-sm font-medium text-gray-700" onClick={() => setMenuOpen(false)}>
              Request Blood
            </Link>
            <Link href="/donors" className="text-sm font-medium text-gray-700" onClick={() => setMenuOpen(false)}>
              Find Donors
            </Link>
            <Link href="/dashboard" className="text-sm font-medium text-gray-700" onClick={() => setMenuOpen(false)}>
              Dashboard
            </Link>
            <hr className="border-gray-200" />
            <Link href="/login" className="btn-secondary text-center text-sm" onClick={() => setMenuOpen(false)}>
              Log In
            </Link>
            <Link href="/register" className="btn-primary text-center text-sm" onClick={() => setMenuOpen(false)}>
              Register
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
