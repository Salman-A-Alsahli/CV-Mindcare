import React, {useEffect, useState} from 'react'
import {Sun, Moon} from 'lucide-react'

export default function ThemeToggle(){
  const [dark, setDark] = useState(()=>{
    try{ return localStorage.getItem('cvmindcare:dark') === '1' || document.documentElement.classList.contains('dark') }catch(e){return false}
  })

  useEffect(()=>{
    try{
      if(dark) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('cvmindcare:dark','1')
      } else {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('cvmindcare:dark','0')
      }
    }catch(e){ }
  }, [dark])

  return (
    <button onClick={()=>setDark(d=>!d)} className="p-2 rounded bg-gray-100 dark:bg-gray-700">
      {dark ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  )
}
