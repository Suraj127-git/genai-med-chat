import React from "react";

function Item({ id, icon, label, active, onSelect }) {
  const isActive = active === id;
  return (
    <button
      onClick={() => onSelect && onSelect(id)}
      className={`w-full flex items-center gap-2 px-2 py-1 rounded-lg text-sm ${
        isActive ? "bg-teal-600/20 text-teal-300" : "text-gray-300 hover:bg-white/10"
      }`}
    >
      <span className="h-6 w-6 grid place-items-center rounded bg-white/10">{icon}</span>
      <span>{label}</span>
    </button>
  );
}

export default function Sidebar({ active, onSelect }) {
  return (
    <aside className="hidden md:flex md:w-64 flex-col bg-black/20 border-r border-white/10 p-3">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="h-6 w-6 rounded bg-teal-500/30" />
          <span className="text-sm text-gray-300">Menu</span>
        </div>
        <button className="text-xs text-gray-400">⋯</button>
      </div>
      <div className="space-y-1">
        <Item id="appointments" icon="📅" label="Appointments" active={active} onSelect={onSelect} />
        <Item id="interview" icon="💬" label="Interview" active={active} onSelect={onSelect} />
        <Item id="profile" icon="👤" label="Profile" active={active} onSelect={onSelect} />
      </div>
      <div className="mt-auto pt-3 border-t border-white/10">
        <div className="text-xs text-gray-400">GenAI Medical Chat</div>
      </div>
    </aside>
  );
}
