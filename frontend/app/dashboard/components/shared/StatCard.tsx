'use client';

import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

export function StatCard({
  title,
  value,
  subtitle,
  icon,
  trend
}: StatCardProps) {
  return (
    <div className="relative group overflow-hidden bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-blue-100/50">
      {/* Mirror/Glass Effect Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-blue-700 opacity-90 group-hover:opacity-100 transition-opacity" />

      {/* Shine Effect Overlay */}
      <div className="absolute inset-0 bg-gradient-to-tr from-white/10 via-transparent to-transparent opacity-0 group-hover:opacity-20 transition-opacity duration-500" />

      {/* Top Glass Highlight */}
      <div className="absolute top-0 left-0 right-0 h-1/2 bg-gradient-to-b from-white/10 to-transparent" />

      <div className="relative p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <p className="text-blue-100 text-sm font-medium tracking-wide uppercase">{title}</p>
            <div className="mt-2 flex items-baseline">
              <p className="text-4xl font-bold text-white tracking-tight drop-shadow-sm">
                {value}
              </p>
            </div>
            {subtitle && (
              <p className="text-blue-200 text-xs mt-1 font-medium">{subtitle}</p>
            )}

            {trend && (
              <div className="flex items-center gap-2 mt-3">
                <div className={`
                  flex items-center px-2 py-0.5 rounded-full text-xs font-bold backdrop-blur-sm
                  ${trend.isPositive ? 'bg-green-400/20 text-green-100' : 'bg-red-400/20 text-red-100'}
                `}>
                  {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
                </div>
                <span className="text-xs text-blue-200/80 font-medium">vs last month</span>
              </div>
            )}
          </div>

          <div className="p-3 bg-white/10 rounded-xl backdrop-blur-md shadow-inner border border-white/20 text-white group-hover:scale-110 transition-transform duration-300">
            {icon}
          </div>
        </div>
      </div>

      {/* Bottom decorative line */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-300/50 to-white/50" />
    </div>
  );
}
