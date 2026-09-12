import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import logo from '../assets/logo.png'
import papel from '../assets/role.png'
import menu from '../assets/menu.png'
import { supabase } from '../services/supabaseClient'
import './EtapaPage.css'

function EtapaPage() {
  const navigate = useNavigate()
  const [dataNascimento, setDataNascimento] = useState('')
  const [sacramentosSelecionados, setSacramentosSelecionados] = useState([])
  const [etapasFiltradas, setEtapasFiltradas] = useState([])
  const [etapas, setEtapas] = useState([])
  const [sacramentos, setSacramentos] = useState([])
  const [loading, setLoading] = useState(true)

  // Ano atual dinâmico
  const anoAtual = new Date().getFullYear()

  // Buscar sacramentos e etapas do Supabase
  useEffect(() => {
    async function fetchData() {
      try {
        // Buscar sacramentos
        const { data: sacramentosData, error: errorSacramentos } = await supabase
          .from('sacramento')
          .select('*')
          .order('ordem')

        console.log('Sacramentos - Data:', sacramentosData)
        console.log('Sacramentos - Erro:', errorSacramentos)

        if (errorSacramentos) {
          console.error('Erro ao buscar sacramentos:', errorSacramentos)
          alert(`Erro ao carregar sacramentos: ${errorSacramentos.message}`)
        } else {
          setSacramentos(sacramentosData || [])
        }

        // Buscar etapas
        const { data: etapasData, error: errorEtapas } = await supabase
          .from('etapa')
          .select('*')
          .order('nome')

        console.log('Etapas - Data:', etapasData)
        console.log('Etapas - Erro:', errorEtapas)

        if (errorEtapas) {
          console.error('Erro ao buscar etapas:', errorEtapas)
          alert('Erro ao carregar etapas')
        } else {
          setEtapas(etapasData || [])
        }
      } catch (err) {
        console.error('Erro:', err)
        alert('Erro ao conectar com banco de dados')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const calcularAnoNascimento = (dataNasc) => {
    if (!dataNasc) return null
    const ano = parseInt(dataNasc.split('-')[0])
    return ano
  }

  const verificarElegibilidade = () => {
    const anoNasc = calcularAnoNascimento(dataNascimento)
    if (!anoNasc) {
      alert('Por favor, informe a data de nascimento')
      return
    }

    const etapasElegiveis = etapas.filter(etapa => {
      // Verifica idade
      const idadeOk = anoNasc >= etapa.ano_nasc_minimo && anoNasc <= etapa.ano_nasc_maximo

      // TODO: Adicionar lógica de sacramentos quando tiver a tabela de relação etapa-sacramento

      return idadeOk
    })

    setEtapasFiltradas(etapasElegiveis)

    if (etapasElegiveis.length === 0) {
      alert('Nenhuma etapa encontrada para os critérios informados')
    }
  }

  const handleSacramentoToggle = (sacramentoId) => {
    setSacramentosSelecionados(prev =>
      prev.includes(sacramentoId)
        ? prev.filter(s => s !== sacramentoId)
        : [...prev, sacramentoId]
    )
  }

  const handleSelecionarEtapa = (etapa) => {
    // Salva dados em localStorage para usar na ficha
    localStorage.setItem('inscricao_data', JSON.stringify({
      dataNascimento,
      sacramentos: sacramentosSelecionados,
      etapaSelecionada: etapa
    }))
    navigate('/inscricao')
  }

  const handlePerfilClick = () => {
    alert('Menu de perfis (será implementado depois)')
  }

  const handleMenuClick = () => {
    alert('Menu de navegação (será implementado depois)')
  }

  if (loading) {
    return (
      <div className="loading-container">
        <p>Carregando...</p>
      </div>
    )
  }

  return (
    <div className="etapa-container">
      {/* Cabeçalho */}
      <header className="etapa-header">
        <div className="header-left">
          <img src={logo} alt="Logo" className="header-logo" />
          <h1 className="header-title">Catequese Divino Espírito Santo</h1>
        </div>
        <div className="header-right">
          <button onClick={handlePerfilClick} className="icon-button">
            <img src={papel} alt="Perfil" className="header-icon" />
          </button>
          <button onClick={handleMenuClick} className="icon-button">
            <img src={menu} alt="Menu" className="header-icon" />
          </button>
        </div>
      </header>

      {/* Conteúdo Principal */}
      <main className="etapa-content">
        {/* Dados do Catequizando */}
        <section className="dados-section">
          <h2 className="section-title">Dados do Catequizando</h2>

          <div className="form-group">
            <label className="form-label">Data de Nascimento:</label>
            <input
              type="date"
              value={dataNascimento}
              onChange={(e) => setDataNascimento(e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Sacramentos já recebidos:</label>
            <div className="sacramentos-container">
              {sacramentos.map(sacramento => (
                <label key={sacramento.id} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={sacramentosSelecionados.includes(sacramento.id)}
                    onChange={() => handleSacramentoToggle(sacramento.id)}
                  />
                  <span>{sacramento.nome_exibicao}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            className="buscar-button"
            onClick={verificarElegibilidade}
          >
            VER ETAPAS DISPONÍVEIS
          </button>
        </section>

        {/* Etapas Disponíveis */}
        {etapasFiltradas.length > 0 && (
          <section className="etapas-section">
            <h2 className="section-title">Etapas Disponíveis</h2>
            <div className="etapas-list">
              {etapasFiltradas.map(etapa => {
                // Calcular idade para o ano atual
                const idadeMin = anoAtual - etapa.ano_nasc_maximo
                const idadeMax = anoAtual - etapa.ano_nasc_minimo

                return (
                  <div key={etapa.id} className="etapa-card">
                    <h3 className="etapa-nome">{etapa.nome}</h3>
                    <p className="etapa-desc">{etapa.descricao || ''}</p>
                    <p className="etapa-idade">
                      Idade (neste ano): {idadeMin} a {idadeMax} anos
                    </p>
                    <button
                      className="selecionar-button"
                      onClick={() => handleSelecionarEtapa(etapa)}
                    >
                      SELECIONAR
                    </button>
                  </div>
                )
              })}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default EtapaPage