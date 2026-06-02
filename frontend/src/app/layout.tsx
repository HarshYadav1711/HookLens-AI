import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HookLens AI",
  description: "Creator intelligence — compare YouTube vs Instagram with cited evidence.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
