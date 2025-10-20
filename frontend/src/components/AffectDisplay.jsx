import React from 'react'

function emojiFor(em){
  if(!em) return '🙂'
  const e = em.toLowerCase();
  if(e.includes('happy')) return '😄'
  if(e.includes('sad')) return '😢'
  if(e.includes('angry')) return '😠'
  if(e.includes('neutral')) return '😐'
  return '🙂'
}

export default function AffectDisplay({emotion}){
  return (
    <div className="flex items-center gap-4">
      <div className="text-4xl">{emojiFor(emotion)}</div>
      <div className="text-lg font-medium">{emotion ?? 'neutral'}</div>
    </div>
  )
}
