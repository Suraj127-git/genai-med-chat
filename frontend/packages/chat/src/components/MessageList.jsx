import React from "react";

export default function MessageList({ refEl, messages, loading }) {
  return (
    <div
      ref={refEl}
      className="h-[60vh] md:h-[68vh] overflow-y-auto px-4 py-6 space-y-4"
    >
      {messages.map((msg, i) => (
        <div key={i} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
          <div
            className={`max-w-[78%] md:max-w-[70%] rounded-2xl px-4 py-3 text-sm ${
              msg.sender === "user"
                ? "bg-teal-600 text-white"
                : "bg-white/5 text-gray-200 border border-white/10"
            }`}
          >
            {msg.content}
          </div>
        </div>
      ))}
      {loading && (
        <div className="flex justify-start">
          <div className="bg-white/5 text-gray-300 px-4 py-3 rounded-2xl border border-white/10 animate-pulse">
            Thinking...
          </div>
        </div>
      )}
    </div>
  );
}

