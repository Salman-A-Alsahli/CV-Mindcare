import React from 'react'
import {motion} from 'framer-motion'
import Navbar from '../components/Navbar'
import SensorCard from '../components/SensorCard'
import NoiseMeter from '../components/NoiseMeter'
import GreeneryMeter from '../components/GreeneryMeter'
import AffectDisplay from '../components/AffectDisplay'
import SuggestionBox from '../components/SuggestionBox'
import ChartCard from '../components/ChartCard'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import useFetch from '../hooks/useFetch'
import StartStop from '../components/StartStop'
import Hero from '../components/Hero'
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, ResponsiveContainer, PolarGrid, PolarAngleAxis, Radar, RadarChart} from 'recharts'

const emotionToScore = (e) => {
  if(!e) return 2
  const s = e.toLowerCase()
  if(s.includes('happy') || s.includes('joy')) return 4
  if(s.includes('calm') || s.includes('content')) return 3
  if(s.includes('neutral')) return 2
  if(s.includes('sad') || s.includes('down')) return 1
  if(s.includes('angry') || s.includes('frustr')) return 0
  return 2
}

export default function Dashboard(){
  const {data: live, loading: liveLoading} = useFetch('/api/live_simple', {interval: 2000})
  const {data: ctx} = useFetch('/api/context')
  const {data: status} = useFetch('/api/status', {interval: 2000})

  const lastSample = status?.last_sample ?? null

  // accumulate last N samples for charts
  const [history, setHistory] = React.useState([])
  React.useEffect(()=>{
    if(!live) return
    if(live.status === 'idle') return
    setHistory(h => {
      const next = [...h, {time: new Date().toLocaleTimeString(), emotion: live.emotion ?? 'neutral', emotionScore: emotionToScore(live.emotion), noise: live.noise_level ?? 0, greenery: live.greenery ?? 0}]
      return next.slice(-60)
    })
  }, [live])

  // sample fallback data when empty
  const sampleHistory = history.length ? history : Array.from({length:10}).map((_,i)=>({time: `${i}`, emotionScore: 2 + Math.round(Math.sin(i/2)*1), noise: 30 + i*2, greenery: 40 + i}))

  const cardMotion = {initial:{opacity:0, y:8}, animate:{opacity:1, y:0}, whileHover:{scale:1.02, boxShadow:'0 10px 30px rgba(2,6,23,0.08)'}}

  return (
    <div className="p-6 min-h-screen bg-gradient-to-b from-white to-slate-50 dark:from-gray-900 dark:to-gray-800 text-gray-900 dark:text-gray-100">
      <div className="max-w-6xl mx-auto">
        <Navbar />

        <Hero sample={lastSample} />

        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <motion.div {...cardMotion} transition={{duration:0.35}}>
            <SensorCard title="Greenery">
              <GreeneryMeter value={live?.greenery} />
            </SensorCard>
          </motion.div>

          <motion.div {...cardMotion} transition={{duration:0.35, delay:0.05}}>
            <SensorCard title="Noise">
              <NoiseMeter value={live?.noise_level} />
            </SensorCard>
          </motion.div>

          <motion.div {...cardMotion} transition={{duration:0.35, delay:0.1}}>
            <SensorCard title="Affect">
              <AffectDisplay emotion={live?.emotion} />
            </SensorCard>
          </motion.div>
        </div>

        <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
          <motion.div {...cardMotion} transition={{duration:0.4}}>
            <ChartCard title="Emotion Trend">
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={sampleHistory} margin={{top:8, right:12, left:0, bottom:0}}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" hide />
                  <YAxis domain={[0,4]} ticks={[0,1,2,3,4]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="emotionScore" stroke="#0ea5a4" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
          </motion.div>

          <motion.div {...cardMotion} transition={{duration:0.45}}>
            <ChartCard title="Noise Overview">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={sampleHistory} margin={{top:8, right:12, left:0, bottom:0}}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" hide />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="noise" fill="#fb923c" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </motion.div>
        </div>

        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
          <motion.div {...cardMotion} transition={{duration:0.5}}>
            <Card title="Suggestions">
              <SuggestionBox suggestions={['Open a window for 2 minutes','Place a green plant near your desk','Lower background noise where possible']} />
            </Card>
          </motion.div>

          <motion.div {...cardMotion} className="lg:col-span-2" transition={{duration:0.5, delay:0.05}}>
            <ChartCard title="Greenery Radar">
              <div className="flex items-center justify-center h-48">
                <ResponsiveContainer width="100%" height={200}>
                  <RadarChart cx="50%" cy="50%" outerRadius={70} data={sampleHistory.map((s,i)=>({subject:`t${i}`, A: s.greenery, fullMark:100}))}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <Radar name="Greenery" dataKey="A" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>
          </motion.div>
        </div>

        <div className="mt-6">
          <SensorCard title="Context Summary">
            <pre className="text-xs max-h-48 overflow-auto">{JSON.stringify(ctx, null, 2)}</pre>
          </SensorCard>
        </div>
      </div>
    </div>
  )
}
