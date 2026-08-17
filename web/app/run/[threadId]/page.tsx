"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { notFound } from "next/navigation";
import { Timeline } from "@/components/Timeline";
import { ReviewPanel } from "@/components/ReviewPanel";
import { FinalReport } from "@/components/FinalReport";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Button } from "@/components/ui/button";
import { useAnalysisStore } from "@/lib/store";
import { useLocale } from "@/lib/i18n";
import type { ReviewAction } from "@/lib/types";

export default function RunPage({
  params,
}: {
  params: Promise<{ threadId: string }>;
}) {
  const { threadId } = use(params);
  const router = useRouter();
  const { runs, review } = useAnalysisStore();
  const { t } = useLocale();
  const run = runs[threadId];

  if (!run) {
    notFound();
  }

  const onReview = (
    action: ReviewAction,
    overrides?: { hourly_rate?: number; weeks_per_month?: number },
  ) => {
    void review(threadId, action, overrides);
  };

  return (
    <div className="flex w-full max-w-2xl flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">triagepath</h1>
        {run.threadId && (
          <span className="font-mono text-xs text-muted-foreground">{run.threadId}</span>
        )}
      </div>

      {run.error && (
        <ErrorBanner message={run.error} onRetry={() => onReview("approve")} />
      )}

      <Timeline events={run.events} />

      {run.interrupt && !run.review && (
        <ReviewPanel
          key={run.interruptNonce}
          payload={run.interrupt}
          busy={run.running}
          onReview={onReview}
        />
      )}

      {run.review && <FinalReport review={run.review} />}

      <div className="flex justify-end">
        <Button variant="link" size="sm" onClick={() => router.push("/")}>
          ← {t("input_title")}
        </Button>
      </div>
    </div>
  );
}
