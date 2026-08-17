"use client";

import { Button } from "@/components/ui/button";
import { useLocale } from "@/lib/i18n";

export function LocaleToggle() {
  const { locale, setLocale } = useLocale();
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => setLocale(locale === "fr" ? "en" : "fr")}
    >
      {locale === "fr" ? "EN" : "FR"}
    </Button>
  );
}
