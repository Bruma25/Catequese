import { useNavigate } from 'react-router-dom'
import { User, LogIn } from 'lucide-react'
import './LoginPage.css'
import logo from "../assets/logo.png"
import email from "../assets/email.png"
import password from "../assets/password.png"
import perfil from "../assets/perfil.png"

function LoginPage() {
  const navigate = useNavigate()

  const handleEntrar = () => {
    // TODO: Implementar login real
    navigate('/home')
  }

  const handleCriarConta = () => {
    // TODO: Implementar criação de conta
    alert('Funcionalidade de criar conta será implementada em breve!')
  }

  return (
    <div className="login-container">
      <div className="login-content">
        {/* Cabeçalho com logo e texto */}
        <div className="login-header">
          <div className="login-logo">
            <img src={logo} alt="Catequese" />
          </div>
          <h1 className="login-text">Catequese Divino Espírito Santo</h1>
        </div>

        {/* Ícone de perfil */}
        <div className="profile-icon">
          <img src={perfil} alt="Perfil" className="profile-icon-img" style={{width: '120px', height: '120px',}} />
        </div>

        {/* Campos de formulário */}
        <div className="login-form">
          <div className="input-group">
            <img src={email} alt="Email" className="input-icon" />
            <input
              type="email"
              placeholder="Email"
              className="login-input"
            />
          </div>

          <div className="input-group">
            <img src={password} alt="Senha" className="input-icon" />
            <input
              type="password"
              placeholder="Senha"
              className="login-input"
            />
          </div>

          {/* Botões */}
          <div className="login-buttons">
            <button
              className="btn-entrar"
              onClick={handleEntrar}
            >
              <LogIn size={18} color="white" />
              Entrar
            </button>

            <button
              className="btn-criar-conta"
              onClick={handleCriarConta}
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