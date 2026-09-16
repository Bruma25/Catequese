// src/services/authService.js
import { supabase } from './supabaseClient'

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

export async function getCurrentUser() {
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

export async function getUserPapeis(usuarioId) {
  const { data, error } = await supabase
    .from('usuario_papel')
    .select(`
      papel_id,
      tipo_papel_usuario (
        id,
        codigo,
        descricao
      )
    `)
    .eq('usuario_id', usuarioId)

  if (error) throw error
  return data
}