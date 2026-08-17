"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useLocale } from "@/lib/i18n";
import type { ReviewAction, ReviewPayload, ScoredTask } from "@/lib/types";

interface Props {
  payload: ReviewPayload;
  busy: boolean;
  onReview: (action: ReviewAction, overrides?: { hourly_rate?: number; weeks_per_month?: number }) => void;
}

export function ReviewPanel({ payload, busy, onReview }: Props) {
  const { t } = useLocale();
  const [editing, setEditing] = useState(false);
  const [hourlyRate, setHourlyRate] = useState(50);
  const [weeks, setWeeks] = useState(4.33);
  const tasks = payload.scored_tasks ?? [];

  const taskName = (t: ScoredTask): string => {
    const raw = t.task ?? t.name;
    if (typeof raw === "string") return raw;
    if (raw && typeof raw === "object" && "name" in raw) {
      return String((raw as { name: unknown }).name);
    }
    return String(raw ?? "");
  };

  return (
    <Card className="w-full border-primary/40">
      <CardHeader>
        <CardTitle>{t("review_title")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-1">
          {tasks.map((task: ScoredTask, i) => (
            <div
              key={i}
              className="flex items-center justify-between rounded border border-border px-3 py-2 text-sm"
            >
              <span className="font-medium">{taskName(task)}</span>
              <span className="text-muted-foreground">
                {task.eur_per_month != null && `${Math.round(task.eur_per_month)} EUR/mois`}
                {task.priority_score != null &&
                  ` · ${task.priority_score} pts`}
              </span>
            </div>
          ))}
        </div>

        {editing && (
          <div className="grid grid-cols-2 gap-4 rounded border border-border p-3">
            <div className="space-y-1">
              <Label htmlFor="rv_hourly">{t("review_hourly")}</Label>
              <Input
                id="rv_hourly"
                type="number"
                step="0.5"
                value={hourlyRate}
                onChange={(e) => setHourlyRate(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="rv_weeks">{t("review_weeks")}</Label>
              <Input
                id="rv_weeks"
                type="number"
                step="0.01"
                value={weeks}
                onChange={(e) => setWeeks(Number(e.target.value))}
              />
            </div>
          </div>
        )}

        <Separator />

        <div className="flex flex-wrap gap-2">
          <Button
            disabled={busy}
            onClick={() =>
              editing
                ? onReview("edit", { hourly_rate: hourlyRate, weeks_per_month: weeks })
                : onReview("approve")
            }
          >
            {editing ? t("review_submit_edit") : t("review_approve")}
          </Button>
          {!editing && (
            <Button variant="secondary" disabled={busy} onClick={() => setEditing(true)}>
              {t("review_edit")}
            </Button>
          )}
          <Button variant="destructive" disabled={busy} onClick={() => onReview("reject")}>
            {t("review_reject")}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
