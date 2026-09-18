// src/pages/ResetSenhaPage.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Lock } from 'lucide-react'
import { supabase } from '../services/supabaseClient'
import logo from "../assets/logo.png"
import './ResetSenhaPage.css'

function ResetSenhaPage() {
  const navigate = useNavigate()
  const [senha, setSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [mostrarSenha, setMostrarSenha] = useState(false)
  const [mostrarConfirmarSenha, setMostrarConfirmarSenha] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [validando, setValidando] = useState(true)

  useEffect(() => {
    // Verificar se é uma sessão de recovery
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        // Verificar se é recovery pelo recovery_sent_at
        if (session.user.recovery_sent_at) {
          console.log('✅ Sessão de recovery válida')
          setValidando(false)
        } else {
          console.log('⚠️ Sessão existe mas não é recovery')
          // Não redireciona, permite usar a página
          setValidando(false)
        }
      } else {
        console.log('❌ Sem sessão')
        // Permite usar a página mesmo sem sessão
        setValidando(false)
      }
    })

    // Ouvir mudanças de auth
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        console.log('📋 Auth event:', event)
        if (event === 'PASSWORD_RECOVERY') {
          console.log('✅ PASSWORD_RECOVERY detectado')
          setValidando(false)
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
      const { error } = await supabase.auth.updateUser({
        password: senha
      })

      if (error) throw error

      setSuccess('Senha atualizada com sucesso! Redirecionando...')

      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } catch (err) {
      setError(err.message || 'Erro ao redefinir senha')
    } finally {
      setLoading(false)
    }
  }

  if (validando) {
    return (
      <div className="reset-container">
        <div className="reset-content">
          <div className="loading-message">
            Carregando...
          </div>
        </div>
      </div>
    )
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