// src/pages/ResetSenhaPage.jsx
import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Eye, EyeOff, Lock } from 'lucide-react'
import { supabase } from '../services/supabaseClient'
import logo from "../assets/logo.png"
import './ResetSenhaPage.css'

function ResetSenhaPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [senha, setSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [mostrarSenha, setMostrarSenha] = useState(false)
  const [mostrarConfirmarSenha, setMostrarConfirmarSenha] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [token, setToken] = useState('')
  const [email, setEmail] = useState('')

  useEffect(() => {
    // Extrair token e email do hash da URL
    const hash = window.location.hash.substring(1) // Remove #
    const params = new URLSearchParams(hash)

    const accessToken = params.get('access_token')
    const refreshToken = params.get('refresh_token')
    const userEmail = params.get('email')

    console.log('📋 Token:', accessToken ? 'Presente' : 'Ausente')
    console.log('📋 Email:', userEmail)

    if (accessToken) {
      setToken(accessToken)
      setEmail(userEmail || '')

      // Configurar sessão manualmente
      supabase.auth.setSession({
        access_token: accessToken,
        refresh_token: refreshToken || '',
      }).then(({ error }) => {
        if (error) {
          console.error('❌ Erro ao setar sessão:', error)
        } else {
          console.log('✅ Sessão configurada com sucesso')
        }
      })
    } else {
      console.log('⚠️ Nenhum token encontrado na URL')
    }

    // Ouvir mudanças de auth
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        console.log('📋 Auth event:', event)

        if (event === 'PASSWORD_RECOVERY') {
          console.log('✅ PASSWORD_RECOVERY detectado')
        }

        if (event === 'SIGNED_IN' && session) {
          console.log('✅ Usuário logado')
        }
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const handleResetSenha = async () => {
    setError('')
    setSuccess('')

    if (!senha || !confirmarSenha) {
      setError('Preencha todos os campos')
      return
    }

    if (senha !== confirmarSenha) {
      setError('As senhas não conferem')
      return
    }

    if (senha.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres')
      return
    }

    setLoading(true)

    try {
      // Primeiro, garantir que a sessão está configurada
      const { data: { session } } = await supabase.auth.getSession()

      if (!session) {
        throw new Error('Sessão não encontrada. Por favor, clique no link do email novamente.')
      }

      console.log('📋 Sessão atual:', session)

      const { error } = await supabase.auth.updateUser({
        password: senha
      })

      if (error) throw error

      setSuccess('Senha atualizada com sucesso! Redirecionando...')

      // Logout após sucesso
      await supabase.auth.signOut()

      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } catch (err) {
      console.error('❌ Erro detalhado:', err)
      setError(err.message || 'Erro ao redefinir senha')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="reset-container">
      <div className="reset-content">
        {/* Logo */}
        <div className="reset-logo">
          <img src={logo} alt="Catequese" style={{ width: '120px', height: '120px' }} />
          <h1 className="reset-title">Redefinir Senha</h1>
        </div>

        {/* Mensagens */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {success && (
          <div className="success-message">
            {success}
          </div>
        )}

        {/* Formulário */}
        <div className="reset-form">
          <div className="form-group">
            <label className="form-label">Nova Senha:</label>
            <div className="password-input-group">
              <input
                type={mostrarSenha ? 'text' : 'password'}
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="form-input"
                placeholder="Digite sua nova senha"
                disabled={loading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setMostrarSenha(!mostrarSenha)}
                disabled={loading}
              >
                {mostrarSenha ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Confirmar Nova Senha:</label>
            <div className="password-input-group">
              <input
                type={mostrarConfirmarSenha ? 'text' : 'password'}
                value={confirmarSenha}
                onChange={(e) => setConfirmarSenha(e.target.value)}
                className="form-input"
                placeholder="Confirme sua nova senha"
                disabled={loading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setMostrarConfirmarSenha(!mostrarConfirmarSenha)}
                disabled={loading}
              >
                {mostrarConfirmarSenha ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <button
            className="btn-reset"
            onClick={handleResetSenha}
            disabled={loading}
          >
            <Lock size={18} color="white" />
            {loading ? 'Redefinindo...' : 'Redefinir Senha'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ResetSenhaPage