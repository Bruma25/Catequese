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
import ResetSenhaPage from './pages/ResetSenhaPage'
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
      <Route
          path="/reset-senha"  // ✅ NOVA ROTA
          element={
            <RotaPublica>
              <ResetSenhaPage />
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

      {/* Rota padrão */}
      <Route path="*" element={<Navigate to={user ? "/home" : "/login"} replace />} />
    </Routes>
  )
}

export default App