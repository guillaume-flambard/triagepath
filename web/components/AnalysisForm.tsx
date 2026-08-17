"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLocale } from "@/lib/i18n";
import type { AnalysisRequest, LlmProvider } from "@/lib/types";

type InputMode = "preset" | "manual" | "url";

interface Props {
  onStart: (req: AnalysisRequest) => void;
  running: boolean;
}

export function AnalysisForm({ onStart, running }: Props) {
  const { t } = useLocale();
  const [mode, setMode] = useState<InputMode>("preset");
  const [preset, setPreset] = useState("lumea");
  const [name, setName] = useState("");
  const [sector, setSector] = useState("");
  const [freeText, setFreeText] = useState("");
  const [url, setUrl] = useState("");
  const [teamSize, setTeamSize] = useState(1);
  const [hourlyRate, setHourlyRate] = useState(50);
  const [weeks, setWeeks] = useState(4.33);
  const [provider, setProvider] = useState<LlmProvider>("mock");

  const submit = () => {
    const base: AnalysisRequest = {
      llm_provider: provider,
      hourly_rate: hourlyRate,
      weeks_per_month: weeks,
    };
    if (mode === "preset") {
      onStart({ ...base, preset });
    } else if (mode === "url") {
      onStart({ ...base, url });
    } else {
      onStart({ ...base, name, sector, free_text: freeText, team_size: teamSize });
    }
  };

  return (
    <Card className="w-full max-w-xl">
      <CardHeader>
        <CardTitle>{t("input_title")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <RadioGroup
          value={mode}
          onValueChange={(v) => setMode(v as InputMode)}
          className="flex flex-wrap gap-2"
        >
          <div className="flex items-center gap-2">
            <RadioGroupItem value="preset" id="m-preset" />
            <Label htmlFor="m-preset">{t("input_preset_label")}</Label>
          </div>
          <div className="flex items-center gap-2">
            <RadioGroupItem value="manual" id="m-manual" />
            <Label htmlFor="m-manual">{t("input_manual")}</Label>
          </div>
          <div className="flex items-center gap-2">
            <RadioGroupItem value="url" id="m-url" />
            <Label htmlFor="m-url">{t("input_url")}</Label>
          </div>
        </RadioGroup>

        {mode === "preset" && (
          <div className="space-y-2">
            <Label>{t("input_preset_label")}</Label>
            <Select value={preset} onValueChange={setPreset}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="lumea">{t("input_preset_lumea")}</SelectItem>
                <SelectItem value="saas">{t("input_preset_saas")}</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        {mode === "manual" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="name">{t("input_name")}</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sector">{t("input_sector")}</Label>
              <Input id="sector" value={sector} onChange={(e) => setSector(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="free_text">{t("input_free_text")}</Label>
              <Textarea
                id="free_text"
                value={freeText}
                onChange={(e) => setFreeText(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="team_size">{t("input_team_size")}</Label>
              <Input
                id="team_size"
                type="number"
                min={1}
                value={teamSize}
                onChange={(e) => setTeamSize(Number(e.target.value))}
              />
            </div>
          </>
        )}

        {mode === "url" && (
          <div className="space-y-2">
            <Label htmlFor="url">{t("input_url")}</Label>
            <Input
              id="url"
              placeholder={t("input_url_ph")}
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="hourly_rate">{t("input_hourly_rate")}</Label>
            <Input
              id="hourly_rate"
              type="number"
              step="0.5"
              value={hourlyRate}
              onChange={(e) => setHourlyRate(Number(e.target.value))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="weeks">{t("input_weeks")}</Label>
            <Input
              id="weeks"
              type="number"
              step="0.01"
              value={weeks}
              onChange={(e) => setWeeks(Number(e.target.value))}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label>{t("input_provider")}</Label>
          <Select
            value={provider}
            onValueChange={(v) => setProvider(v as LlmProvider)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="mock">{t("provider_mock")}</SelectItem>
              <SelectItem value="ollama">{t("provider_ollama")}</SelectItem>
              <SelectItem value="groq">{t("provider_groq")}</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Button onClick={submit} disabled={running} className="w-full">
          {running ? t("input_running") : t("input_submit")}
        </Button>
      </CardContent>
    </Card>
  );
}
