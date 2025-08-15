import React, { useEffect, useState } from 'react'

function Chip({children}) { return <span className='badge'>{children}</span> }

function Card({m, onVote}) {
  return (
    <div className='card'>
      <div className='flex items-start justify-between'>
        <div>
          <div className='text-sm text-gray-500'>{m.from}</div>
          <div className='font-semibold'>{m.subject || '(no subject)'}</div>
          <div className='text-sm text-gray-600 mt-1'>{m.snippet}</div>
          <div className='mt-2 space-x-1'>
            {(m.reasons||[]).map((r,i)=><Chip key={i}>{r}</Chip>)}
            <Chip>Score {m.score}</Chip>
          </div>
        </div>
        <div className='flex gap-2'>
          <button onClick={()=>onVote(m.id,1)} className='px-3 py-1 rounded-xl border'>👍</button>
          <button onClick={()=>onVote(m.id,-1)} className='px-3 py-1 rounded-xl border'>👎</button>
        </div>
      </div>
    </div>
  )
}

export function App(){
  const [msgs, setMsgs] = useState([])
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(1)

  const [meta, setMeta] = useState({shown:0,total:0})
  const load = async () => {
    setLoading(true)
    const r = await fetch(`/api/digest?days=${days}`)
    const j = await r.json()
    setMsgs(j.messages || [])
    setMeta({shown: j.shown||0, total: j.total||0})
    setLoading(false)
  }
  useEffect(()=>{ load() }, [days])

  const onVote = (id, v) => {
    setMsgs(prev => prev.map(x => x.id===id ? {...x, score: +(x.score + v).toFixed(3)} : x))
  }

  return (
    <div className='max-w-5xl mx-auto p-6 space-y-6'>
      <header className='flex items-center justify-between'>
        <h1 className='text-2xl font-bold'>Your Gmail Digest</h1><div className='text-sm text-gray-500'>Showing {meta.shown} of {meta.total}</div>
        <nav className='flex gap-4'>
          <a className='text-blue-600 underline' href='/logout'>Logout</a>
          <a className='text-blue-600 underline' href='/settings'>Settings</a>
          <a className='text-blue-600 underline' href='/admin'>Admin</a>
        </nav>
      </header>

      <section className='card flex items-center gap-4'>
        <label>Look back:</label>
        <select className='border rounded-lg p-1' value={days} onChange={e=>setDays(+e.target.value)}>
          <option value={1}>24 hours</option>
          <option value={3}>3 days</option>
          <option value={7}>7 days</option>
        </select>
      </section>

      {loading ? <div>Loading…</div> :
        <div className='space-y-4'>{msgs.map(m => <Card key={m.id} m={m} onVote={onVote} />)}</div>
      }
    </div>
  )
}
