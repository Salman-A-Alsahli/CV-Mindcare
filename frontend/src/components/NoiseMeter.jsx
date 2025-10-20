import React from 'react'

export default function NoiseMeter({value}){
  const pct = Math.min(100, Math.max(0, (value || 0)));
  return (
    <div>
      <div className="text-2xl font-bold">{value ?? 'N/A'} dB</div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 h-3 rounded mt-2">
        <div className="h-3 bg-green-400 rounded" style={{width: `${pct}%`}} />
      </div>
    </div>
  )
}
