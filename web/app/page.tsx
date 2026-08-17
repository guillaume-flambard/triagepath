"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AnalysisForm } from "@/components/AnalysisForm";
import { useAnalysisStore } from "@/lib/store";
import type { AnalysisRequest } from "@/lib/types";

export default function Home() {
  const router = useRouter();
  const { start } = useAnalysisStore();
  const [running, setRunning] = useState(false);

  const onStart = async (req: AnalysisRequest) => {
    setRunning(true);
    const threadId = await start(req);
    router.push(`/run/${threadId}`);
  };

  return (
    <div className="flex w-full flex-1 justify-center">
      <AnalysisForm onStart={onStart} running={running} />
    </div>
  );
}
