import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { LogIn } from 'lucide-react'
import { login } from '../services/authService'
import './LoginPage.css'
import logo from "../assets/logo.png"
import email from "../assets/email.png"
import password from "../assets/password.png"
import perfil from "../assets/perfil.png"

function LoginPage() {
  const navigate = useNavigate()
  const [emailInput, setEmailInput] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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

  const handleCriarConta = () => {
    alert('Funcionalidade de criar conta será implementada em breve!')
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

          <div className="input-group">
            <img src={email} alt="Email" className="input-icon" />
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
            <img src={password} alt="Senha" className="input-icon" />
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
              onClick={handleCriarConta}
              disabled={loading}
            >
              Criar conta
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage