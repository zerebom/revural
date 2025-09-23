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
      <div className="flex items-center justify-between gap-3">
        <div className="flex-1">
          <Select value={value ?? undefined} onValueChange={onChange}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="体制プリセットを選択" />
            </SelectTrigger>
            <SelectContent>
              {presets.map((p) => (
                <SelectItem key={p.key} value={p.key}>
                  {p.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button
          type="button"
          variant="secondary"
          disabled={!selected}
          onClick={() => {
            if (selected) onApply(selected.roles);
          }}
        >
          プリセットを適用
        </Button>
      </div>
      {selected && (
        <p className="text-xs text-muted-foreground mt-2">
          適用メンバー: {selected.roles.join(", ")}
        </p>
      )}
    </div>
  );
}
