import React, { useEffect, useState } from 'react'

function Chip({label, onRemove}){
  return <span className='inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 border mr-2 mb-2'>
    {label}
    <button className='ml-2 text-gray-500' onClick={onRemove}>×</button>
  </span>
}

function ChipInput({label, value, onChange, placeholder}){
  const [chips, setChips] = React.useState(value||[])
  const [text, setText] = React.useState('')
  React.useEffect(()=>{ setChips(value||[]) }, [value])
  const add = () => {
    const v = text.trim()
    if(!v) return
    const next = Array.from(new Set([...(chips||[]), v]))
    setChips(next); onChange(next); setText('')
  }
  const remove = (i) => {
    const next = chips.filter((_,idx)=>idx!==i)
    setChips(next); onChange(next)
  }
  return (
    <div>
      <label className='block font-semibold mb-1'>{label}</label>
      <div className='flex gap-2'>
        <input className='border rounded-lg p-2 flex-1' placeholder={placeholder||''} value={text} onChange={e=>setText(e.target.value)} onKeyDown={e=>{ if(e.key==='Enter'){ e.preventDefault(); add() }}} />
        <button className='px-3 py-1 rounded-lg border' onClick={add}>Add</button>
      </div>
      <div className='mt-2'>{(chips||[]).map((c,i)=><Chip key={i} label={c} onRemove={()=>remove(i)} />)}</div>
    </div>
  )
}


function ChipEditor({label, value, onChange, placeholder}){
  const [input, setInput] = useState('')
  const add = () => {
    if(input && !value.includes(input)) onChange([...value, input])
    setInput('')
  }
  const remove = (v) => onChange(value.filter(x => x !== v))
  return (
    <div>
      <label className='block font-semibold mb-1'>{label}</label>
      <div className='flex gap-2 mb-2'>
        <input className='border rounded-lg p-2 flex-1' placeholder={placeholder||''} value={input} onChange={e=>setInput(e.target.value)} />
        <button className='px-3 py-1 rounded-lg border' onClick={add}>Add</button>
      </div>
      <div className='flex flex-wrap gap-2'>
        {value.map(v => (
          <span key={v} className='bg-gray-200 px-2 py-1 rounded-full flex items-center gap-1'>
            {v} <button onClick={()=>remove(v)}>×</button>
          </span>
        ))}
      </div>
    </div>
  )
}

export function Settings(){
  const [prefs, setPrefs] = useState(null)
  const [previewHtml, setPreviewHtml] = useState(null)
  const load = async () => {
    const r = await fetch('/api/prefs')
    setPrefs(await r.json())
  }
  useEffect(()=>{ load() }, [])


  const [reasonStats, setReasonStats] = useState([])
  useEffect(()=>{
    const fetchStats = async () => {
      const r = await fetch('/api/digest')
      const j = await r.json()
      const counts = {}
      for(const m of j.messages||[]){
        for(const reason of m.reasons||[]){
          counts[reason] = (counts[reason]||0) + 1
        }
      }
      setReasonStats(Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,5))
    }
    fetchStats()
  }, [prefs.min_score])

  const save = async () => {
    await fetch('/api/prefs', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(prefs)})
    alert('Saved')
  }
  const preview = async () => {
    const r = await fetch('/api/preview_digest')
    setPreviewHtml(await r.text())
  }

  if(!prefs) return <div className='max-w-3xl mx-auto p-6'>Loading…</div>

  return (
    <div className='max-w-3xl mx-auto p-6 space-y-6'>
      <header className='flex items-center justify-between'>
        <h1 className='text-2xl font-bold'>Settings</h1>
        <a className='text-blue-600 underline' href='/'>Back to Digest</a>
      </header>

      <div className='card space-y-4'>
        <div className='grid md:grid-cols-2 gap-6'>
          <ChipEditor label='VIP senders' value={prefs.vip_senders||[]} onChange={v=>setPrefs({...prefs, vip_senders:v})} placeholder='user@domain.com' />
          <ChipEditor label='Blocked senders' value={prefs.blocked_senders||[]} onChange={v=>setPrefs({...prefs, blocked_senders:v})} />
          <ChipEditor label='Always-show keywords' value={prefs.always_keywords||[]} onChange={v=>setPrefs({...prefs, always_keywords:v})} />
          <ChipEditor label='Mute keywords' value={prefs.mute_keywords||[]} onChange={v=>setPrefs({...prefs, mute_keywords:v})} />
        </div>

        <div className='grid md:grid-cols-4 gap-4'>
          <div>
            <label className='block font-semibold mb-1'>Urgency focus</label>
            <input type='range' min='0' max='1' step='0.05' value={prefs.urgency_bias||0.5} onChange={e=>setPrefs({...prefs, urgency_bias: +e.target.value})} />
          </div>
          <div>
            <label className='block font-semibold mb-1'>Importance threshold</label>
            <input type='range' min='0' max='1' step='0.05' value={prefs.importance_threshold||0.5} onChange={e=>setPrefs({...prefs, importance_threshold: +e.target.value})} />
          </div>
          <div>
            <label className='block font-semibold mb-1'>Email theme</label>
            <select className='border rounded-lg p-1' value={prefs.email_theme||'light'} onChange={e=>setPrefs({...prefs, email_theme:e.target.value})}>
              <option value='light'>Light</option>
              <option value='dark'>Dark</option>
            </select>
          </div>
          <div>
            <label className='block font-semibold mb-1'>Items in emailed digest</label>
            <input className='border rounded-lg p-1 w-24' type='number' min='5' max='50' value={prefs.top_n||20} onChange={e=>setPrefs({...prefs, top_n: Math.max(5, Math.min(50, +e.target.value||20))})} />
          </div>
        </div>

        <div className='flex justify-between'>
          <button className='px-4 py-2 rounded-xl border' onClick={save}>Save</button>
          <button className='px-4 py-2 rounded-xl border' onClick={preview}>Preview emailed digest</button>
        </div>
      </div>

      {previewHtml && (
        <div className='card mt-6'>
          <h2 className='font-bold mb-2'>Preview</h2>
          <div dangerouslySetInnerHTML={{__html: previewHtml}} />
        </div>
      )}
    </div>
  )
}
