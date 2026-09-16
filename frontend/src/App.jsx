import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import SplashScreen from './pages/SplashScreen'
import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'
import EtapaPage from './pages/EtapaPage'
import FichaInscricaoPage from './pages/FichaInscricaoPage'
import GestaoEtapasPage from './pages/GestaoEtapasPage'
import GestaoTurmasPage from './pages/GestaoTurmasPage'
import GestaoInscricoesPage from './pages/GestaoInscricoesPage'
import './App.css'

function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return <div>Carregando...</div>
  }

  if (!user) {
    return <LoginPage />
  }

  return (
    <Router basename="/Catequese">  {/* ← Adicione isso */}
      <Routes>
        <Route path="/" element={<SplashScreen />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/etapas" element={<EtapaPage />} />
        <Route path="/inscricao" element={<FichaInscricaoPage />} />
        <Route path="/gestao-etapas" element={<GestaoEtapasPage />} />
        <Route path="/gestao-turmas" element={<GestaoTurmasPage />} />
        <Route path="/gestao-inscricoes" element={<GestaoInscricoesPage />} />
      </Routes>
    </Router>
  )
}

export default App