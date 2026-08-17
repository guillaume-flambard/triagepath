"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLocale } from "@/lib/i18n";
import type { ReviewResponse } from "@/lib/types";

interface Props {
  review: ReviewResponse;
}

export function FinalReport({ review }: Props) {
  const { t } = useLocale();
  const final = review.final ?? {};
  const report = final.report ?? "";

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{t("report_title")}</CardTitle>
      </CardHeader>
      <CardContent>
        {report ? (
          <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{report}</pre>
        ) : (
          <p className="text-sm text-muted-foreground">—</p>
        )}
      </CardContent>
    </Card>
  );
}
