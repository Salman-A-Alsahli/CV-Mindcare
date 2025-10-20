import React, {useEffect, useState} from 'react'
import SensorCard from '../components/SensorCard'
import NoiseMeter from '../components/NoiseMeter'
import GreeneryMeter from '../components/GreeneryMeter'
import AffectDisplay from '../components/AffectDisplay'
import SuggestionBox from '../components/SuggestionBox'

export default function Dashboard(){
  const [live, setLive] = useState(null)
  const [ctx, setCtx] = useState(null)
  const [loading, setLoading] = useState(true)

  async function fetchData(){
    setLoading(true)
    try{
      const L = await fetch('/api/live').then(r=>r.json())
      setLive(L)
      const C = await fetch('/api/context').then(r=>r.json())
      setCtx(C)
    }catch(e){
      console.error(e)
    }
    setLoading(false)
  }

  useEffect(()=>{ fetchData(); const id = setInterval(fetchData, 3000); return ()=>clearInterval(id); }, [])

  return (
    <div className="p-6 min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">CV Mindcare</h1>
          <div className="text-sm">Dashboard</div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <SensorCard title="Greenery">
            <GreeneryMeter value={live?.avg_green_pct} />
          </SensorCard>
          <SensorCard title="Noise">
            <NoiseMeter value={live?.avg_db} />
          </SensorCard>
          <SensorCard title="Affect">
            <AffectDisplay emotion={live?.dominant_emotion} />
          </SensorCard>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-1">
            <SensorCard title="Suggestions">
              <SuggestionBox suggestions={['Open a window for 2 minutes','Place a green plant near your desk','Lower background noise where possible']} />
            </SensorCard>
          </div>
          <div>
            <SensorCard title="Context Summary">
              <pre className="text-xs">{JSON.stringify(ctx, null, 2)}</pre>
            </SensorCard>
          </div>
        </div>
      </div>
    </div>
  )
}
