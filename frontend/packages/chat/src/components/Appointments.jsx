import React, { useState } from "react";

export default function Appointments() {
  const [query, setQuery] = useState("");
  const doctors = [
    { id: 1, name: "Dr. Aisha Khan", specialty: "Cardiologist", availability: "Mon, Wed, Fri" },
    { id: 2, name: "Dr. Luis García", specialty: "Dermatologist", availability: "Tue, Thu" },
    { id: 3, name: "Dr. Mei Lin", specialty: "Neurologist", availability: "Daily" },
    { id: 4, name: "Dr. Ravi Patel", specialty: "General Physician", availability: "Weekends" },
  ];

  const filtered = doctors.filter(
    (d) =>
      d.name.toLowerCase().includes(query.toLowerCase()) ||
      d.specialty.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="p-4">
      <div className="mb-4 flex items-center gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search doctors or specialties"
          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm placeholder:text-gray-500 outline-none"
        />
        <button className="px-3 py-2 bg-teal-600 text-white rounded-lg text-sm">Search</button>
      </div>
      <div className="space-y-3">
        {filtered.map((d) => (
          <div key={d.id} className="bg-white/5 border border-white/10 rounded-xl p-3 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-gray-200">{d.name}</div>
              <div className="text-xs text-gray-400">{d.specialty}</div>
              <div className="text-xs text-gray-500">Availability: {d.availability}</div>
            </div>
            <button className="px-3 py-1 rounded-lg bg-teal-600 text-white text-xs">Book</button>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="text-sm text-gray-400">No doctors found</div>
        )}
      </div>
    </div>
  );
}
