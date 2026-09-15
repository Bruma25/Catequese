import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import Header from '../components/Header/Header'
import './HomePage.css'

function HomePage() {
  const navigate = useNavigate()
  const [periodoInscricao] = useState('01/01/2025 - 31/12/2025')

  const handleInscricaoClick = () => {
    navigate('/etapas')
  }

  return (
    <div className="home-container">
      {/* Cabeçalho Reutilizável */}
      <Header titulo="Catequese Divino Espírito Santo" />

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