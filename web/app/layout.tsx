import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { LocaleProvider } from "@/lib/i18n";
import { AnalysisStoreProvider } from "@/lib/store";
import { LocaleToggle } from "@/components/LocaleToggle";
import { Toaster } from "@/components/ui/sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "triagepath",
  description: "Agentic operations & knowledge copilot",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <LocaleProvider>
          <AnalysisStoreProvider>
            <header className="flex items-center justify-between border-b border-border px-6 py-3">
              <span className="text-lg font-semibold tracking-tight">triagepath</span>
              <LocaleToggle />
            </header>
            <main className="flex flex-1 flex-col items-center px-6 py-8">{children}</main>
            <Toaster />
          </AnalysisStoreProvider>
        </LocaleProvider>
      </body>
    </html>
  );
}
