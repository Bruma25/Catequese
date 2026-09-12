import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import SplashScreen from './pages/SplashScreen'
import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'
import EtapaPage from './pages/EtapaPage'
import FichaInscricaoPage from './pages/FichaInscricaoPage'
import './App.css'

function App() {
  return (
    <Router basename="/Catequese">  {/* ← Adicione isso */}
      <Routes>
        <Route path="/" element={<SplashScreen />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/etapas" element={<EtapaPage />} />
        <Route path="/inscricao" element={<FichaInscricaoPage />} />
      </Routes>
    </Router>
  )
}

export default App