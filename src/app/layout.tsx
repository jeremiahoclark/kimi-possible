import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kimi Possible - AI Research Assistant",
  description: "AI Research Assistant powered by Kimi-K2",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
