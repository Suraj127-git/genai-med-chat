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
        <label className="block text-sm font-medium text-gray-700 mb-1 tracking-wide">
          {label}
        </label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={`w-full px-4 py-2.5 bg-white/80 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all ${
          error ? "border-red-500 ring-red-200" : ""
        } ${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
};

export default Input;
