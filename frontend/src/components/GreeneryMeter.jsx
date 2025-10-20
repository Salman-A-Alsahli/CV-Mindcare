import React from 'react'

export default function GreeneryMeter({value}){
  const pct = Math.min(100, Math.max(0, (value || 0)));
  return (
    <div className="flex items-center gap-4">
      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-200 to-green-400 flex items-center justify-center text-xl font-bold">{value ?? 'N/A'}%</div>
      <div className="text-sm text-gray-600 dark:text-gray-300">Greenery in view</div>
    </div>
  )
}
