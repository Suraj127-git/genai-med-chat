import React from "react";

export default function Composer({ value, onChange, onSubmit, onVoice, recording, onUpload, onGraph, loading }) {
  return (
    <div className="px-4">
      <div className="bg-white/5 border border-white/10 rounded-2xl px-3 py-2 flex items-center gap-2">
        <button className="h-8 w-8 grid place-items-center rounded-lg bg-teal-600/20 text-teal-300">🔍</button>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onSubmit()}
          placeholder="Ask anything. Type @ for mentions and / for shortcuts."
          className="flex-1 bg-transparent outline-none text-sm placeholder:text-gray-500"
        />
        <label className="h-8 w-8 grid place-items-center rounded-lg bg-white/10 text-gray-300 cursor-pointer">
          📄
          <input type="file" accept="image/*" className="hidden" onChange={onUpload} />
        </label>
        <button
          onClick={onVoice}
          className={`h-8 w-8 grid place-items-center rounded-lg ${recording ? "bg-red-600 text-white" : "bg-white/10 text-gray-300"}`}
        >
          🎙
        </button>
        <button onClick={onGraph} className="h-8 w-8 grid place-items-center rounded-lg bg-white/10 text-gray-300">🧠</button>
        <button
          onClick={onSubmit}
          disabled={loading}
          className="h-8 w-8 grid place-items-center rounded-lg bg-teal-600 text-white disabled:opacity-60"
        >
          ➤
        </button>
      </div>
    </div>
  );
}

