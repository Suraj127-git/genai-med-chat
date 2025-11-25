import React from "react";

export default function Sidebar() {
  return (
    <aside className="hidden md:flex md:w-64 flex-col bg-black/20 border-r border-white/10 p-3">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="h-6 w-6 rounded bg-teal-500/30" />
          <span className="text-sm text-gray-300">Home</span>
        </div>
        <button className="text-xs text-gray-400">⋯</button>
      </div>
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-gray-300">
          <span className="text-lg">📚</span>
          <span className="text-sm">Library</span>
        </div>
        <div className="flex items-center gap-2 text-gray-300">
          <span className="text-lg">🧪</span>
          <span className="text-sm">Academic</span>
        </div>
        <div className="flex items-center gap-2 text-gray-300">
          <span className="text-lg">⚙️</span>
          <span className="text-sm">Settings</span>
        </div>
      </div>
      <div className="mt-auto pt-3 border-t border-white/10">
        <button className="w-full text-left text-xs text-gray-400">Upgrade</button>
      </div>
    </aside>
  );
}

