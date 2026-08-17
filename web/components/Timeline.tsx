"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useLocale } from "@/lib/i18n";
import type { SseEvent } from "@/lib/types";

interface Props {
  events: SseEvent[];
}

export function Timeline({ events }: Props) {
  const { t } = useLocale();
  const nodes = events.filter((e) => e.type === "node");
  const status = nodes.length === 0 ? "idle" : "running";

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{t("timeline_title")}</CardTitle>
        {nodes.length > 0 && (
          <Badge variant="secondary">
            {nodes.length} · {t("status_running")}
          </Badge>
        )}
      </CardHeader>
      <CardContent className="space-y-2">
        {nodes.length === 0 && (
          <p className="text-sm text-muted-foreground">…</p>
        )}
        {nodes.map((e, i) => (
          <NodeStep
            key={i}
            node={e.node}
            message={e.message}
            active={i === nodes.length - 1 && status === "running"}
          />
        ))}
      </CardContent>
    </Card>
  );
}

function NodeStep({ node, message, active }: { node: string; message: string; active: boolean }) {
  return (
    <div className="flex items-start gap-3 border-l-2 border-border pl-3">
      <span className="mt-0.5 inline-flex h-2 w-2 shrink-0 rounded-full bg-primary" />
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-semibold">{node}</span>
          {active && <Badge variant="secondary" className="text-[10px]">live</Badge>}
        </div>
        {message && <p className="text-sm text-muted-foreground">{message}</p>}
      </div>
    </div>
  );
}
