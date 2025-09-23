"use client";

import * as React from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

export type TeamPreset = {
  key: string;
  name: string;
  roles: string[];
};

export function TeamPresetSelect({
  presets,
  value,
  onChange,
  onApply,
  className,
}: {
  presets: TeamPreset[];
  value?: string | null;
  onChange: (key: string) => void;
  onApply: (roles: string[]) => void;
  className?: string;
}) {
  const selected = React.useMemo(() => presets.find((p) => p.key === value) || null, [presets, value]);

  return (
    <div className={className}>
      <div className="space-y-2">
        <Select value={value ?? undefined} onValueChange={onChange}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="体制プリセットを選択" />
          </SelectTrigger>
          <SelectContent position="popper" className="z-50 bg-white shadow-lg border">
            {presets.map((p) => (
              <SelectItem key={p.key} value={p.key}>
                {p.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {selected && (
          <div className="bg-blue-50 border border-blue-200 rounded-md px-3 py-2">
            <p className="text-xs text-blue-700">
              適用メンバー: {selected.roles.join(", ")}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
