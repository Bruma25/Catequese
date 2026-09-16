// src/hooks/useAuth.js
import { useEffect, useState } from 'react'
import { supabase } from '../services/supabaseClient'
import { getUserPapeis } from '../services/authService'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [papeis, setPapeis] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Verificar sessão atual
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser(session.user)
        carregarPapeis(session.user.id)
      } else {
        setLoading(false)
      }
    })

    // Ouvir mudanças na autenticação
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (session?.user) {
          setUser(session.user)
          await carregarPapeis(session.user.id)
        } else {
          setUser(null)
          setPapeis([])
        }
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  async function carregarPapeis(usuarioId) {
    try {
      const papeisData = await getUserPapeis(usuarioId)
      setPapeis(papeisData.map(p => p.tipo_papel_usuario))
    } catch (err) {
      console.error('Erro ao carregar papéis:', err)
    } finally {
      setLoading(false)
    }
  }

  async function logout() {
    await supabase.auth.signOut()
    localStorage.removeItem('user')
    setUser(null)
    setPapeis([])
  }

  return { user, papeis, loading, logout }
}