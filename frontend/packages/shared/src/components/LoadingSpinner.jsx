import React from "react";

const LoadingSpinner = ({ size = "medium", className = "" }) => {
  const sizeClasses = {
    small: "w-5 h-5 border-2",
    medium: "w-8 h-8 border-3",
    large: "w-12 h-12 border-4",
  };

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div
        className={`${sizeClasses[size]} border-t-transparent border-blue-500 rounded-full animate-spin border-solid`}
        style={{ animationDuration: "0.8s" }}
      ></div>
    </div>
  );
};

export default LoadingSpinner;
