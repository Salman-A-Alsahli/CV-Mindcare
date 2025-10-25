import React from 'react'
import {motion} from 'framer-motion'
import AffectDisplay from './AffectDisplay'

export default function Hero({sample}){
  const emotion = sample?.dominant_emotion ?? '—'
  const noise = sample?.avg_db ?? '—'
  const green = sample?.avg_green_pct ?? sample?.greenery ?? '—'

  return (
    <motion.section initial={{opacity:0, y:6}} animate={{opacity:1, y:0}} transition={{duration:0.4}} className="hero-bg rounded-xl p-6 mb-6">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">CV Mindcare</h1>
          <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">A local-first mental wellness dashboard — live affect, environment and suggestions.</p>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-center">
            <div className="text-xs text-gray-500 dark:text-gray-400">Affect</div>
            <div className="mt-1"><AffectDisplay emotion={emotion} /></div>
          </div>

          <div className="text-center">
            <div className="text-xs text-gray-500 dark:text-gray-400">Noise</div>
            <div className="mt-1 text-lg font-semibold">{noise === '—' ? '—' : Math.round(noise) + ' dB'}</div>
          </div>

          <div className="text-center">
            <div className="text-xs text-gray-500 dark:text-gray-400">Greenery</div>
            <div className="mt-1 text-lg font-semibold">{green === '—' ? '—' : Math.round(green) + '%'}</div>
          </div>
        </div>
      </div>
    </motion.section>
  )
}
