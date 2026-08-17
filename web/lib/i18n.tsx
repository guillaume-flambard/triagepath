"use client";

import { createContext, useContext, useState, ReactNode } from "react";

export type Locale = "fr" | "en";

interface LocaleContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
}

const strings: Record<Locale, Record<string, string>> = {
  fr: {
    app_title: "triagepath",
    app_tagline: "Copilote agentique d'operations et de knowledge",
    input_title: "Nouvelle analyse",
    input_preset_label: "Preset",
    input_preset_lumea: "Lumea (D2C)",
    input_preset_saas: "SaaS",
    input_manual: "Description libre",
    input_url: "Site web (URL)",
    input_name: "Nom de l'entreprise",
    input_sector: "Secteur",
    input_free_text: "Decrivez les operations",
    input_url_ph: "https://exemple.com",
    input_team_size: "Taille de l'equipe",
    input_hourly_rate: "Taux horaire (EUR)",
    input_weeks: "Semaines / mois",
    input_provider: "Modele LLM",
    provider_mock: "mock (hors ligne)",
    provider_ollama: "ollama (local)",
    provider_groq: "groq",
    input_submit: "Lancer l'analyse",
    input_running: "Analyse en cours...",
    timeline_title: "Timeline",
    review_title: "Revue humaine",
    review_approve: "Approuver",
    review_edit: "Modifier",
    review_reject: "Rejeter",
    review_hourly: "Taux horaire (EUR)",
    review_weeks: "Semaines / mois",
    review_submit_edit: "Valider la modification",
    report_title: "Rapport final",
    error_title: "Erreur",
    error_retry: "Relancer",
    task_col_task: "Tache",
    task_col_hours: "h/mois",
    task_col_eur: "EUR/mois",
    task_col_priority: "Priorite",
    status_running: "En cours",
    status_done: "Termine",
    status_interrupt: "En attente de revue",
  },
  en: {
    app_title: "triagepath",
    app_tagline: "Agentic operations & knowledge copilot",
    input_title: "New analysis",
    input_preset_label: "Preset",
    input_preset_lumea: "Lumea (D2C)",
    input_preset_saas: "SaaS",
    input_manual: "Free-form description",
    input_url: "Website (URL)",
    input_name: "Business name",
    input_sector: "Sector",
    input_free_text: "Describe the operations",
    input_url_ph: "https://example.com",
    input_team_size: "Team size",
    input_hourly_rate: "Hourly rate (EUR)",
    input_weeks: "Weeks / month",
    input_provider: "LLM provider",
    provider_mock: "mock (offline)",
    provider_ollama: "ollama (local)",
    provider_groq: "groq",
    input_submit: "Run analysis",
    input_running: "Analyzing...",
    timeline_title: "Timeline",
    review_title: "Human review",
    review_approve: "Approve",
    review_edit: "Edit",
    review_reject: "Reject",
    review_hourly: "Hourly rate (EUR)",
    review_weeks: "Weeks / month",
    review_submit_edit: "Submit edit",
    report_title: "Final report",
    error_title: "Error",
    error_retry: "Retry",
    task_col_task: "Task",
    task_col_hours: "h/month",
    task_col_eur: "EUR/month",
    task_col_priority: "Priority",
    status_running: "Running",
    status_done: "Done",
    status_interrupt: "Awaiting review",
  },
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>("fr");
  const t = (key: string) => strings[locale][key] ?? key;
  return (
    <LocaleContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LocaleContext.Provider>
  );
}

export function useLocale(): LocaleContextValue {
  const ctx = useContext(LocaleContext);
  if (!ctx) throw new Error("useLocale must be used within LocaleProvider");
  return ctx;
}
