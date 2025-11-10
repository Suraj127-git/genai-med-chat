import React from "react";

const Card = ({ children, className = "", title, subtitle }) => {
  return (
    <div
      className={`bg-white/70 backdrop-blur-lg border border-gray-200 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-shadow duration-300 ${className}`}
    >
      {(title || subtitle) && (
        <div className="mb-5 text-center">
          {title && (
            <h2 className="text-2xl font-bold text-blue-700 tracking-tight">
              {title}
            </h2>
          )}
          {subtitle && (
            <p className="text-gray-500 mt-1 text-sm">{subtitle}</p>
          )}
        </div>
      )}
      {children}
    </div>
  );
};

export default Card;
