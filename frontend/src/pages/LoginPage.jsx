import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { LogIn, Mail, Lock } from 'lucide-react'
import { login, signup, resetPassword } from '../services/authService'
import ModalCriarConta from '../components/ModalCriarConta/ModalCriarConta'
import './LoginPage.css'
import logo from "../assets/logo.png"
import perfil from "../assets/perfil.png"

function LoginPage() {
  const navigate = useNavigate()
  const [emailInput, setEmailInput] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [modalAberto, setModalAberto] = useState(false)

  const handleEntrar = async () => {
    if (!emailInput || !password) {
      setError('Preencha email e senha')
      return
    }

    setLoading(true)
    setError('')

    try {
      const { user, session } = await login(emailInput, password)

      localStorage.setItem('user', JSON.stringify({
        id: user.id,
        email: user.email,
      }))

      navigate('/home')
    } catch (err) {
      setError(err.message || 'Erro ao fazer login')
    } finally {
      setLoading(false)
    }
  }

  const handleCriarConta = async (email, senha, nome) => {
    await signup(email, senha, nome)
    setSuccess('Conta criada! Verifique seu email para confirmar.')
    setError('')
  }

  const handleEsqueciSenha = async () => {
    const email = prompt('Digite seu email para recuperar a senha:')

    if (!email) {
      alert('Email é obrigatório')
      return
    }

    try {
      await resetPassword(email)
      alert('Email de recuperação enviado! Verifique sua caixa de entrada.')
      setSuccess('Email de recuperação enviado!')
    } catch (err) {
      setError(err.message || 'Erro ao enviar email de recuperação')
    }
  }

  return (
    <div className="login-container">
      <div className="login-content">
        {/* Logo Maior no Topo */}
        <div className="login-logo-large">
          <img src={logo} alt="Catequese" style={{ width: '150px', height: '150px' }} />
          <h1 className="login-text">Catequese Divino Espírito Santo</h1>
        </div>

        {/* Ícone de perfil */}
        <div className="profile-icon">
          <img src={perfil} alt="Perfil" className="profile-icon-img" style={{width: '120px', height: '120px'}} />
        </div>

        {/* Campos de formulário */}
        <div className="login-form">
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

          <div className="input-group">
            <Mail size={20} color="#667eea" />
            <input
              type="email"
              placeholder="Email"
              className="login-input"
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="input-group">
            <Lock size={20} color="#667eea" />
            <input
              type="password"
              placeholder="Senha"
              className="login-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleEntrar()}
              disabled={loading}
            />
          </div>

          {/* Botões */}
          <div className="login-buttons">
            <button
              className="btn-entrar"
              onClick={handleEntrar}
              disabled={loading}
            >
              <LogIn size={18} color="white" />
              {loading ? 'Entrando...' : 'Entrar'}
            </button>

            <button
              className="btn-criar-conta"
              onClick={() => setModalAberto(true)}
              disabled={loading}
            >
              Criar conta
            </button>

            {/* Link Esqueci Minha Senha */}
            <button
              className="btn-esqueci-senha"
              onClick={handleEsqueciSenha}
              disabled={loading}
            >
              Esqueci minha senha
            </button>
          </div>
        </div>
      </div>

      {/* Modal Criar Conta */}
      <ModalCriarConta
        isOpen={modalAberto}
        onClose={() => setModalAberto(false)}
        onCriarConta={handleCriarConta}
      />
    </div>
  )
}

export default LoginPage