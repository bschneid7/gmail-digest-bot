import React, { useEffect, useState } from 'react'

export function Admin(){
  const [users, setUsers] = useState([])
  const [email, setEmail] = useState('')
  const [stats, setStats] = useState(null)

  const load = async () => {
    const r = await fetch('/api/admin/users')
    if(r.status===403){ alert('You are not an admin.'); return }
    setUsers(await r.json())
  }
  useEffect(()=>{ load() }, [])

  const addUser = async () => {
    if(!email) return
    await fetch('/api/admin/users', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email})})
    setEmail(''); load()
  }
  const removeUser = async (e) => {
    await fetch('/api/admin/users', {method:'DELETE', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email:e})})
    load()
  }

  const loadAnalytics = async () => { const r = await fetch('/api/admin/analytics'); if(r.status===403) return; setStats(await r.json()) }
  return (
    <div className='max-w-2xl mx-auto p-6 space-y-6'>
      <header className='flex items-center justify-between'>
        <h1 className='text-2xl font-bold'>Admin — Allowed Users</h1>
        <a className='text-blue-600 underline' href='/'>Back</a>
      </header>

      <div className='card'>
        <div className='flex gap-2'>
          <input className='border rounded-lg p-2 flex-1' placeholder='user@example.com' value={email} onChange={e=>setEmail(e.target.value)} />
          <button className='px-4 py-2 rounded-xl border' onClick={addUser}>Add</button>
        </div>
        <ul className='mt-4 divide-y'>
          {users.map(u => (
            <li key={u} className='flex items-center justify-between py-2'>
              <span>{u}</span>
              <button className='px-3 py-1 rounded border' onClick={()=>removeUser(u)}>Remove</button>
            </li>
          ))}
        </ul>
      </div>
    
      <div className='card mt-6'>
        <h2 className='font-semibold mb-2'>Analytics (last 14 days)</h2>
        <button className='px-3 py-1 rounded border' onClick={loadAnalytics}>Refresh</button>
        {stats && (
          <div className='mt-4 space-y-2'>
            <div>Total runs: {stats.runs}</div>
            <div>Total messages: {stats.total_messages}</div>
            <div>Avg messages per run: {stats.avg_per_run?.toFixed(1)}</div>
            <div className='mt-2'>
              <div className='font-semibold mb-1'>Top reasons</div>
              <ul className='list-disc ml-6'>
                {(stats.top_reasons||[]).map(([reason,count]) => (<li key={reason}>{reason}: {count}</li>))}
              </ul>
            </div>
          </div>
        )}
      </div>

    </div>
  )
}
