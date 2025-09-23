"use client";

import * as React from "react";
import { AgentRole } from "@/lib/types";

interface MemberSelectGridProps {
  agents: AgentRole[];
  selectedRoles: string[];
  onToggleRole: (role: string) => void;
  className?: string;
}

function ProfileCard({
  agent,
  selected,
  onToggle,
}: {
  agent: AgentRole;
  selected: boolean;
  onToggle: (role: string) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onToggle(agent.role)}
      aria-pressed={selected}
      className={[
        "group relative w-full overflow-hidden rounded-2xl border transition-all",
        "bg-white text-left shadow-sm hover:shadow-lg p-4",
        selected ? "border-blue-600 ring-2 ring-blue-600" : "border-gray-200",
        "focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600",
      ].join(" ")}
    >
      {/* Selected badge */}
      <div
        className={[
          "absolute right-2 top-2 flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium",
          selected ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600 opacity-0 group-hover:opacity-100",
          "transition-opacity",
        ].join(" ")}
      >
        {selected ? "✓ 選択中" : "選択"}
      </div>

      {/* Avatar and Content */}
      <div className="flex flex-col gap-3">
        {/* Avatar */}
        <div className="flex justify-center">
          {agent.avatar_url ? (
            <img
              src={agent.avatar_url}
              alt={`${agent.display_name}のアバター`}
              className="w-16 h-16 rounded-full object-cover border-2 border-gray-200"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-xl font-bold">
              {agent.display_name.charAt(0)}
            </div>
          )}
        </div>

        {/* Text Content */}
        <div className="flex flex-col gap-2">
          <div className="text-lg font-semibold leading-tight text-gray-900 text-center">
            {agent.display_name}
          </div>

          {agent.role_label && (
            <div className="text-sm font-medium text-blue-600 text-center">
              {agent.role_label}
            </div>
          )}

          <p className="text-sm text-gray-700 line-clamp-3">
            {agent.bio || agent.description}
          </p>

          {agent.tags && agent.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {agent.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
                >
                  {tag}
                </span>
              ))}
              {agent.tags.length > 3 && (
                <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-500 rounded-full">
                  +{agent.tags.length - 3}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </button>
  );
}

export function MemberSelectGrid({
  agents,
  selectedRoles,
  onToggleRole,
  className,
}: MemberSelectGridProps) {
  return (
    <div className={className}>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {agents.map((agent) => (
          <ProfileCard
            key={agent.role}
            agent={agent}
            selected={selectedRoles.includes(agent.role)}
            onToggle={onToggleRole}
          />
        ))}
      </div>
    </div>
  );
}
