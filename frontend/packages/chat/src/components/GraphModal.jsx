import React from "react";

export default function GraphModal({ onClose, graph, convId }) {
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="bg-[#0b0f14] border border-white/10 rounded-2xl p-6 w-[92%] max-w-2xl max-h-[80vh] overflow-auto relative text-gray-100">
        <button onClick={onClose} className="absolute top-3 right-4 text-gray-400 hover:text-gray-200">✖</button>
        <div className="text-lg font-semibold text-teal-300 mb-3">Reasoning Graph (Conv: {convId})</div>
        <pre className="text-xs bg-white/5 border border-white/10 rounded-lg p-3 overflow-auto text-gray-300">
          {JSON.stringify(graph, null, 2)}
        </pre>
      </div>
    </div>
  );
}

