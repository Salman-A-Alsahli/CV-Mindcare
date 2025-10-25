import {useState, useEffect, useRef} from 'react'

export default function useFetch(url, opts={interval:0}){
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const timerRef = useRef(null)

  async function fetchOnce(){
    setLoading(true)
    try{
      const res = await fetch(url)
      const j = await res.json()
      setData(j)
    }catch(e){ console.error(e) }
    setLoading(false)
  }

  useEffect(()=>{
    fetchOnce()
    if(opts.interval && opts.interval>0){
      timerRef.current = setInterval(fetchOnce, opts.interval)
      return ()=>clearInterval(timerRef.current)
    }
  }, [url])

  return {data, loading, refetch: fetchOnce}
}
