import React from 'react'
import clsx from 'clsx'

export default function ChartCard({title, children, className=''}){
  return (
    <div className={clsx('glass-card backdrop-blur-sm bg-white/60 dark:bg-gray-800/40 shadow-lg rounded-xl p-4 border border-white/20', className)}>
      <h3 className="font-semibold text-sm text-gray-700 dark:text-gray-200">{title}</h3>
      <div className="mt-2 h-48">{children}</div>
    </div>
  )
}
