import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "HayatConnect — Blood Donation Matching for Karachi",
  description:
    "Connecting patients with nearby verified blood donors in Karachi using AI-powered matching.",
  keywords: ["blood donation", "Karachi", "donor matching", "hayat"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="min-h-screen">{children}</main>
        <footer className="border-t border-gray-200 bg-white py-6 text-center text-sm text-gray-500">
          <p>&copy; {new Date().getFullYear()} HayatConnect. Saving lives, one match at a time.</p>
        </footer>
      </body>
    </html>
  );
}
