import React from "react";

const Button = ({
  children,
  onClick,
  type = "button",
  variant = "primary",
  disabled = false,
  className = "",
}) => {
  const baseClasses =
    "px-4 py-2 rounded-lg font-semibold transition-all duration-200 focus:outline-none active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed";

  const variantClasses = {
    primary:
      "bg-teal-600 text-white hover:bg-teal-500",
    secondary:
      "bg-white/10 border border-white/10 text-gray-300 hover:bg-white/15",
    danger:
      "bg-red-600 text-white hover:bg-red-500",
    success:
      "bg-emerald-600 text-white hover:bg-emerald-500",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;
