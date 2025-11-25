import React from "react";

const Input = ({
  type = "text",
  placeholder = "",
  value,
  onChange,
  label,
  error,
  className = "",
  ...props
}) => {
  return (
    <div className="mb-5">
      {label && (
        <label className="block text-sm font-medium text-gray-300 mb-1 tracking-wide">
          {label}
        </label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={`w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-gray-100 placeholder-gray-500 shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all ${
          error ? "border-red-500 ring-red-500/40" : ""
        } ${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
    </div>
  );
};

export default Input;
