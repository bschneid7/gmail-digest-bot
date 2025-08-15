import React from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { App } from './modules/App'
import { Settings } from './modules/Settings'
import { Admin } from './modules/Admin'
import './styles.css'

const router = createBrowserRouter([
  { path: '/', element: <App/> },
  { path: '/settings', element: <Settings/> },
  { path: '/admin', element: <Admin/> },
])

createRoot(document.getElementById('root')).render(<RouterProvider router={router} />)
