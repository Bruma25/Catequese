// frontend/src/pages/HomePage.jsx
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { supabase } from '../services/supabaseClient'
import Header from '../components/Header/Header'
import './HomePage.css'

function HomePage() {
  const navigate = useNavigate()

  const [periodoCatequese, setPeriodoCatequese] = useState('01/01/2025 - 31/12/2025')
  const [periodoJovensAdultos, setPeriodoJovensAdultos] = useState('01/02/2025 - 28/02/2025')

  const [nomeUsuario, setNomeUsuario] = useState('')

  useEffect(() => {
    buscarNomeUsuario()
    carregarPeriodos()

    const handleStorageChange = () => {
      carregarPeriodos()
    }

    window.addEventListener('storage', handleStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
    }
  }, [])

  async function buscarNomeUsuario() {
    try {
      const { data: { user } } = await supabase.auth.getUser()

      if (!user) {
        return
      }

      const { data: userData, error } = await supabase
        .from('usuario')
        .select('*')
        .eq('id', user.id)
        .single()

      if (error) {
        console.error('Erro ao buscar usuário:', error)
        return
      }

      if (userData?.nome) {
        const primeiroNome = userData.nome.split(' ')[0]
        setNomeUsuario(primeiroNome)
      }
    } catch (error) {
      console.error('Erro ao buscar nome do usuário:', error)
    }
  }

  function carregarPeriodos() {
    try {
      const periodos = localStorage.getItem('periodos_inscricao')

      if (periodos) {
        const dados = JSON.parse(periodos)

        if (dados.catequese?.inicio && dados.catequese?.fim) {
          const inicio = formatarDataBR(dados.catequese.inicio)
          const fim = formatarDataBR(dados.catequese.fim)
          setPeriodoCatequese(`${inicio} - ${fim}`)
        }

        if (dados.jovens?.inicio && dados.jovens?.fim) {
          const inicio = formatarDataBR(dados.jovens.inicio)
          const fim = formatarDataBR(dados.jovens.fim)
          setPeriodoJovensAdultos(`${inicio} - ${fim}`)
        }
      }
    } catch (error) {
      console.error('Erro ao carregar períodos:', error)
    }
  }

  function formatarDataBR(dataISO) {
    if (!dataISO) return ''
    const [ano, mes, dia] = dataISO.split('-')
    return `${dia}/${mes}/${ano}`
  }

  const handleInscricaoClick = () => {
    navigate('/etapas')
  }

  return (
    <div className="home-container">
      <Header titulo="Catequese Divino Espírito Santo" />

      <main className="home-content">
        {nomeUsuario && (
          <div className="boas-vindas-container">
            <p className="boas-vindas-texto">Olá, {nomeUsuario}!</p>
          </div>
        )}

        <button className="inscricao-button" onClick={handleInscricaoClick}>
          INSCRIÇÃO PARA CATEQUESE
        </button>

        <div className="periodo-container">
          <label className="periodo-label">Período de inscrição para catequese:</label>
          <p className="periodo-texto">{periodoCatequese}</p>
        </div>

        <div className="periodo-container">
          <label className="periodo-label">Período de inscrição para catequese de jovens e adultos:</label>
          <p className="periodo-texto">{periodoJovensAdultos}</p>
        </div>
      </main>
    </div>
  )
}

export default HomePage