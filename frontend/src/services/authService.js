// src/services/authService.js
import { supabase } from './supabaseClient'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const USAR_BACKEND = import.meta.env.VITE_USAR_BACKEND === 'true'

export async function login(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })

  if (error) throw error
  return data
}

export async function logout() {
  const { error } = await supabase.auth.signOut()
  if (error) throw error
}

export async function signup(email, password, nome) {
  const { data: authData, error: authError } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        nome: nome,
      },
    },
  })

  if (authError) throw authError

  if (authData.user) {
    const { error: userError } = await supabase
      .from('usuario')
      .insert({
        id: authData.user.id,
        email: email,
        nome: nome,
      })

    if (userError) throw userError
  }

  return authData
}

// export async function resetPassword(email) {
//   const { error } = await supabase.auth.resetPasswordForEmail(email, {
//     redirectTo: `${window.location.origin}/Catequese/reset-senha`,
//   })
//
//   if (error) throw error
// }

export async function resetPassword(email) {
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    // ✅ Não especificar redirectTo, usar hash URL
  })

  if (error) throw error
}

export async function getCurrentUser() {
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

export async function getUserPapeis(usuarioId) {
  console.log('🔍 Buscando papéis para:', usuarioId)

  if (USAR_BACKEND) {
    try {
      const response = await fetch(`${API_URL}/usuarios/${usuarioId}/papeis`)

      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('✅ Papéis do backend:', data)
      return data
    } catch (error) {
      console.warn('⚠️ Backend falhou, usando Supabase direto:', error)
    }
  }

  const { data: testData, error: testError } = await supabase
    .from('usuario_papel')
    .select('*')
    .eq('usuario_id', usuarioId)

  console.log('📋 Teste simples:', testData, 'Erro:', testError)

  const { data, error } = await supabase
    .from('usuario_papel')
    .select(`
      *,
      tipo_papel_usuario:tipo_papel_usuario(
        id,
        codigo,
        descricao
      )
    `)
    .eq('usuario_id', usuarioId)

  if (error) {
    console.error('❌ Erro na query:', error)
    throw error
  }

  console.log('📋 Dados brutos:', data)

  const papeis = data
    .filter(item => item.tipo_papel_usuario !== null)
    .map(item => item.tipo_papel_usuario)

  console.log('✅ Papéis extraídos:', papeis)
  return papeis
}

export async function getUsuario(usuarioId) {
  try {
    const response = await fetch(`${API_URL}/usuarios/${usuarioId}`)

    if (!response.ok) {
      throw new Error(`Erro ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('❌ Erro ao buscar usuário:', error)
    throw error
  }
}

export async function listarUsuarios() {
  try {
    const response = await fetch(`${API_URL}/usuarios`)

    if (!response.ok) {
      throw new Error(`Erro ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('❌ Erro ao listar usuários:', error)
    throw error
  }
}

export async function atualizarPapeisUsuario(usuarioId, papeisIds) {
  try {
    const response = await fetch(`${API_URL}/usuarios/${usuarioId}/papeis`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        papeis_ids: papeisIds
      })
    })

    if (!response.ok) {
      throw new Error(`Erro ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('❌ Erro ao atualizar papéis:', error)
    throw error
  }
}
