import React from "react";

export default function Sidebar({ active = "interview", onSelect = () => {} }) {
  const Item = ({ id, icon, label }) => (
    <button
      onClick={() => onSelect(id)}
      className={`w-full flex items-center gap-2 px-2 py-2 rounded-lg text-left ${
        active === id ? "bg-white/10 text-teal-300" : "text-gray-300 hover:bg-white/5"
      }`}
    >
      <span className="text-lg">{icon}</span>
      <span className="text-sm">{label}</span>
    </button>
  );

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
        <Item id="appointments" icon="�" label="Appointments" />
        <Item id="interview" icon="💬" label="Interview" />
        <Item id="profile" icon="👤" label="Profile" />
      </div>
      <div className="mt-auto pt-3 border-t border-white/10">
        <div className="text-xs text-gray-400">GenAI Medical Chat</div>
      </div>
    </aside>
  );
}
