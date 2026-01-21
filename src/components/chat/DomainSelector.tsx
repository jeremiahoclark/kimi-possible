"use client";

import type { Domain } from "@/lib/types";

interface DomainSelectorProps {
  value: Domain;
  onChange: (domain: Domain) => void;
}

const domains: { value: Domain; label: string; description: string }[] = [
  { value: "general", label: "General", description: "General research" },
  { value: "content_research", label: "Content", description: "Movies, TV, entertainment" },
  { value: "technical_research", label: "Technical", description: "Code, docs, APIs" },
  { value: "market_research", label: "Market", description: "Business, trends" },
];

export function DomainSelector({ value, onChange }: DomainSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <label className="text-sm text-gray-400">Mode:</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as Domain)}
        className="bg-[#1a1a1a] border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 focus:outline-none focus:border-purple-500 cursor-pointer"
      >
        {domains.map((domain) => (
          <option key={domain.value} value={domain.value}>
            {domain.label}
          </option>
        ))}
      </select>
    </div>
  );
}
