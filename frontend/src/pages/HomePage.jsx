import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import logo from '../assets/logo.png'
import papel from '../assets/role.png'
import menu from '../assets/menu.png'
import './HomePage.css'

function HomePage() {
  const navigate = useNavigate()
  const [periodoInscricao] = useState('01/01/2025 - 31/12/2025')

  const handleInscricaoClick = () => {
    navigate('/etapas')
  }

  const handlePerfilClick = () => {
    alert('Menu de perfis (será implementado depois)')
  }

  const handleMenuClick = () => {
    alert('Menu de navegação (será implementado depois)')
  }

  return (
    <div className="home-container">
      {/* Cabeçalho */}
      <header className="home-header">
        <div className="header-left">
          <img src={logo} alt="Logo" className="header-logo" />
          <h1 className="header-title">Catequese Divino Espírito Santo</h1>
        </div>
        <div className="header-right">
          <button onClick={handlePerfilClick} className="icon-button">
            <img src={papel} alt="Perfil" className="header-icon" />
          </button>
          <button onClick={handleMenuClick} className="icon-button">
            <img src={menu} alt="Menu" className="header-icon" />  {/* ← Use o menu.png */}
          </button>
        </div>
      </header>

      {/* Conteúdo Principal */}
      <main className="home-content">
        <button className="inscricao-button" onClick={handleInscricaoClick}>
          INSCRIÇÃO PARA CATEQUESE
        </button>

        <div className="periodo-container">
          <label className="periodo-label">Período de inscrição:</label>
          <p className="periodo-texto">{periodoInscricao}</p>
        </div>
      </main>
    </div>
  )
}

export default HomePage