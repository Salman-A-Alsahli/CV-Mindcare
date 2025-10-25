import React, {useState, useEffect, useRef} from 'react'
import Button from './ui/Button'

export default function StartStop(){
  const [running, setRunning] = useState(false)
  const [lastSample, setLastSample] = useState(null)
  const timerRef = useRef(null)

  async function fetchStatus(){
    try{
      const r = await fetch('/api/status')
      const j = await r.json()
      setRunning(Boolean(j?.running))
      setLastSample(j?.last_sample ?? null)
    }catch(e){ /* ignore */ }
  }

  useEffect(()=>{
    fetchStatus()
    timerRef.current = setInterval(fetchStatus, 2000)
    return ()=> clearInterval(timerRef.current)
  }, [])

  async function start(){
    try{
      const r = await fetch('/api/start')
      const j = await r.json()
      if(j?.status === 'started') setRunning(true)
    }catch(e){ console.error(e) }
  }
  async function stop(){
    try{
      const r = await fetch('/api/stop')
      const j = await r.json()
      if(j?.status === 'stopped') setRunning(false)
    }catch(e){ console.error(e) }
  }

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2">
        <div aria-hidden className={`w-2 h-2 rounded-full ${running? 'bg-green-400' : 'bg-gray-400'}`} />
        <div className="text-sm text-gray-600 dark:text-gray-300">{running? 'Running' : 'Idle'}</div>
      </div>

      <div className="text-xs text-gray-600 dark:text-gray-300">
        {lastSample ? `${lastSample.dominant_emotion || ''} · ${lastSample.avg_db ? Math.round(lastSample.avg_db) + ' dB' : ''}` : ''}
      </div>

      <Button onClick={start} disabled={running} variant="primary" className="!px-4">
        Start
      </Button>
      <Button onClick={stop} disabled={!running} variant="destructive" className="!px-4">
        Stop
      </Button>
    </div>
  )
}
