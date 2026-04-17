"use client"

import { useState, useEffect } from "react"

export default function Demo() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true)
        const response = await fetch("http://localhost:8000/api/auth/users/")
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`)
        }
        
        const result = await response.json()
        setData(result)
        setError(null)
      } catch (err) {
        setError(err.message)
        setData(null)
      } finally {
        setLoading(false)
      }
    }

    fetchUsers()
  }, [])

  const refetch = async () => {
    try {
      setLoading(true)
      const response = await fetch("http://localhost:8000/api/auth/users/")
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }
      
      const result = await response.json()
      setData(result)
      setError(null)
    } catch (err) {
      setError(err.message)
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ padding: "2rem" }}>
      <h1>Demo - Users from Django Backend</h1>

      {loading && <p>Loading...</p>}

      {error && (
        <div style={{ color: "red", padding: "1rem", backgroundColor: "#ffe0e0", marginBottom: "1rem" }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {data && (
        <div>
          <p>Total Users: {Array.isArray(data) ? data.length : 0}</p>
          <pre style={{ backgroundColor: "#f5f5f5", padding: "1rem", overflowX: "auto", marginBottom: "1rem" }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}

      <button onClick={refetch} style={{ padding: "0.5rem 1rem", cursor: "pointer" }}>
        Refresh Data
      </button>
    </main>
  )
}