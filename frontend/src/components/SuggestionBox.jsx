import React from 'react'

export default function SuggestionBox({suggestions}){
  return (
    <div>
      <ul className="list-disc pl-5 text-sm">
        {(suggestions||[]).map((s, i)=> <li key={i} className="mb-1">{s}</li>)}
      </ul>
    </div>
  )
}
