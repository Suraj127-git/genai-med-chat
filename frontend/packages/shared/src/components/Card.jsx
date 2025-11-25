import React from "react";

const Card = ({ children, className = "", title, subtitle }) => {
  return (
    <div
      className={`bg-white/5 border border-white/10 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-shadow duration-300 text-gray-100 ${className}`}
    >
      {(title || subtitle) && (
        <div className="mb-5 text-center">
          {title && (
            <h2 className="text-2xl font-semibold text-teal-300 tracking-tight">
              {title}
            </h2>
          )}
          {subtitle && (
            <p className="text-gray-400 mt-1 text-sm">{subtitle}</p>
          )}
        </div>
      )}
      {children}
    </div>
  );
};

export default Card;
