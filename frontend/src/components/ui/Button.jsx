import React from 'react'
import {motion} from 'framer-motion'
import clsx from 'clsx'

export default function Button({children, className = '', variant = 'primary', ...props}){
  const base = 'inline-flex items-center justify-center px-3 py-1.5 rounded-md font-medium focus:outline-none'
  const variants = {
    primary: 'bg-teal-500 text-white hover:bg-teal-600 shadow-sm',
    secondary: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100 hover:bg-gray-200',
    destructive: 'bg-red-500 text-white hover:bg-red-600'
  }

  return (
    <motion.button
      whileTap={{scale:0.98}}
      whileHover={{scale:1.02}}
      transition={{type:'spring', stiffness:300, damping:20}}
      className={clsx(base, variants[variant] ?? variants.primary, className)}
      {...props}
    >
      {children}
    </motion.button>
  )
}
