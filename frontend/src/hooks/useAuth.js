// src/hooks/useAuth.js
import { useEffect, useState } from 'react'
import { supabase } from '../services/supabaseClient'
import { getUserPapeis } from '../services/authService'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [papeis, setPapeis] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        console.log('📋 SESSION USER ID:', session.user.id)
        console.log('📋 SESSION USER EMAIL:', session.user.email)
        setUser(session.user)
        carregarPapeis(session.user.id)
      } else {
        console.log('⚠️ Sem sessão')
        setLoading(false)
      }
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('📋 AUTH STATE CHANGE:', event)
        if (session?.user) {
          console.log('📋 AUTH CHANGE USER ID:', session.user.id)
          console.log('📋 AUTH CHANGE USER EMAIL:', session.user.email)
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
      console.log('📋 Carregando papéis para:', usuarioId)

      const papeisData = await getUserPapeis(usuarioId)

      console.log('✅ Papéis carregados:', papeisData)
      setPapeis(papeisData)
    } catch (err) {
      console.error('❌ Erro ao carregar papéis:', err)
      setPapeis([])
    } finally {
      setLoading(false)
    }
  }

  async function logout() {
    await supabase.auth.signOut()
    localStorage.removeItem('perfil_ativo')
    setUser(null)
    setPapeis([])
  }

  return { user, papeis, loading, logout }
}