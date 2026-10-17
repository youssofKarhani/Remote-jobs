import React from "react";

interface BrandIconProps {
  className?: string;
  size?: number;
}

export function BrandIcon({ className = "h-5 w-5", size }: BrandIconProps) {
  return (
    <svg
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      width={size}
      height={size}
      aria-label="FindJobFit Logo"
    >
      <defs>
        <linearGradient id="fj-violet" x1="11" y1="8" x2="28" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#c084fc" />
          <stop offset="100%" stopColor="#7c3aed" />
        </linearGradient>
        <linearGradient id="fj-cyan" x1="20" y1="24" x2="30" y2="31" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#38bdf8" />
          <stop offset="100%" stopColor="#6366f1" />
        </linearGradient>
      </defs>

      {/* Primary 'F' Element (Evidence / Candidate Foundation) */}
      <path
        d="M11 10C11 8.89543 11.8954 8 13 8H26C27.1046 8 28 8.89543 28 10V12C28 13.1046 27.1046 14 26 14H17V17H23C24.1046 17 25 17.8954 25 19V20C25 21.1046 24.1046 22 23 22H17V30C17 31.1046 16.1046 32 15 32H13C11.8954 32 11 31.1046 11 30V10Z"
        fill="url(#fj-violet)"
      />

      {/* Interlocking Job-Fit Latch (Role Match Nexus) */}
      <path
        d="M22 25L28 25C29.1046 25 30 25.8954 30 27V29C30 30.1046 29.1046 31 28 31H22C20.8954 31 20 30.1046 20 29V27C20 25.8954 20.8954 25 22 25Z"
        fill="url(#fj-cyan)"
      />

      {/* Central Precision Fit Spark */}
      <path
        d="M20 18L21.5 19.5L20 21L18.5 19.5L20 18Z"
        fill="#ffffff"
      />
    </svg>
  );
}
