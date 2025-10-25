import React from 'react'

export default function Toggle({checked=false, onChange=()=>{}, className=''}){
  return (
    <label className={`inline-flex items-center cursor-pointer ${className}`}>
      <input type="checkbox" checked={checked} onChange={e=>onChange(e.target.checked)} className="sr-only" />
      <span className={`w-9 h-5 rounded-full inline-block ${checked? 'bg-primary' : 'bg-gray-300'}`}>
        <span className={`block w-4 h-4 bg-white rounded-full transform transition-transform ${checked? 'translate-x-4' : 'translate-x-1'}`} />
      </span>
    </label>
  )
}
