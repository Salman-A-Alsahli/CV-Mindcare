import React from 'react'
import {Settings} from 'lucide-react'
import ThemeToggle from './ThemeToggle'
import StartStop from './StartStop'
import Button from './ui/Button'

export default function Navbar(){
  return (
    <header className="flex items-center justify-between py-4">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-blue-500 flex items-center justify-center text-white font-bold">CM</div>
        <div className="text-lg font-semibold">CV Mindcare</div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden sm:block">
          <StartStop />
        </div>
        <ThemeToggle />
        <Button variant="secondary" className="p-2"><Settings size={16} /></Button>
      </div>
    </header>
  )
}
