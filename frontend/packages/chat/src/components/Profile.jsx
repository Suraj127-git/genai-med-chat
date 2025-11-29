import React from "react";
import { useSelector } from "react-redux";

export default function Profile() {
  const user = useSelector((state) => state.auth.user);

  return (
    <div className="p-4 space-y-4">
      <div className="text-lg font-semibold text-teal-300">Profile</div>
      {user ? (
        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
          <div className="text-sm text-gray-200">{user.full_name || user.name || "User"}</div>
          <div className="text-xs text-gray-400">{user.email}</div>
        </div>
      ) : (
        <div className="text-sm text-gray-400">No user information available</div>
      )}
    </div>
  );
}
