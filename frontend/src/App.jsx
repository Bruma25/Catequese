// src/App.jsx
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import SplashScreen from './pages/SplashScreen'
import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'
import EtapaPage from './pages/EtapaPage'
import FichaInscricaoPage from './pages/FichaInscricaoPage'
import GestaoEtapasPage from './pages/GestaoEtapasPage'
import GestaoTurmasPage from './pages/GestaoTurmasPage'
import GestaoInscricoesPage from './pages/GestaoInscricoesPage'
import ConfiguracoesPage from './pages/ConfiguracoesPage'
import MinhasTurmasPage from './pages/MinhasTurmasPage'
import MinhasTurmasCoordenadorPage from './pages/MinhasTurmasCoordenadorPage'
import MinhasTurmasCatequistaPage from './pages/MinhasTurmasCatequistaPage'
import GestaoUsuariosPage from './pages/GestaoUsuariosPage'
import MeusCatequizandosPage from './pages/MeusCatequizandosPage'
import ConfiguracaoPeriodosPage from './pages/ConfiguracaoPeriodosPage'
import './App.css'

// Componente para rotas protegidas
function RotaProtegida({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Carregando...</div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}

// Componente para rotas públicas
function RotaPublica({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Carregando...</div>
      </div>
    )
  }

  if (user) {
    return <Navigate to="/home" replace />
  }

  return children
}

function App() {
  const { user } = useAuth()

  return (
    <Routes>
      {/* Rotas públicas */}
      <Route path="/" element={<SplashScreen />} />
      <Route
        path="/login"
        element={
          <RotaPublica>
            <LoginPage />
          </RotaPublica>
        }
      />

      {/* Rotas protegidas */}
      <Route
        path="/home"
        element={
          <RotaProtegida>
            <HomePage />
          </RotaProtegida>
        }
      />
      <Route
        path="/configuracao-periodos"
        element={
          <RotaProtegida>
            <ConfiguracaoPeriodosPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/etapas"
        element={
          <RotaProtegida>
            <EtapaPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/inscricao"
        element={
          <RotaProtegida>
            <FichaInscricaoPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/gestao-etapas"
        element={
          <RotaProtegida>
            <GestaoEtapasPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/gestao-turmas"
        element={
          <RotaProtegida>
            <GestaoTurmasPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/gestao-inscricoes"
        element={
          <RotaProtegida>
            <GestaoInscricoesPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/configuracoes"
        element={
          <RotaProtegida>
            <ConfiguracoesPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/gestao-usuarios"
        element={
          <RotaProtegida>
            <GestaoUsuariosPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/meus-catequizandos"
        element={
          <RotaProtegida>
            <MeusCatequizandosPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/minhas-turmas"
        element={
          <RotaProtegida>
            <MinhasTurmasPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/minhas-turmas-coordenador"
        element={
          <RotaProtegida>
            <MinhasTurmasCoordenadorPage />
          </RotaProtegida>
        }
      />
      <Route
        path="/minhas-turmas-catequista"
        element={
          <RotaProtegida>
            <MinhasTurmasCatequistaPage />
          </RotaProtegida>
        }
      />

      {/* Rota padrão */}
      <Route path="*" element={<Navigate to={user ? "/home" : "/login"} replace />} />
    </Routes>
  )
}

export default App