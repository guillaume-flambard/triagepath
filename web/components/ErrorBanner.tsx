"use client";

import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useLocale } from "@/lib/i18n";

interface Props {
  message: string;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onRetry }: Props) {
  const { t } = useLocale();
  return (
    <Alert variant="destructive" className="w-full">
      <AlertTitle>{t("error_title")}</AlertTitle>
      <AlertDescription className="flex items-center justify-between gap-4">
        <span className="break-words">{message}</span>
        {onRetry && (
          <Button size="sm" variant="outline" onClick={onRetry}>
            {t("error_retry")}
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}
