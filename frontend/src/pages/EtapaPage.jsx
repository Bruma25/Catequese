import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Header from '../components/Header/Header'
import { listarEtapas, listarSacramentos } from '../services/api'
import './EtapaPage.css'

function EtapaPage() {
  const navigate = useNavigate()
  const [dataNascimento, setDataNascimento] = useState('')
  const [sacramentosSelecionados, setSacramentosSelecionados] = useState([])
  const [etapasFiltradas, setEtapasFiltradas] = useState([])
  const [etapas, setEtapas] = useState([])
  const [sacramentos, setSacramentos] = useState([])
  const [loading, setLoading] = useState(true)

  const anoAtual = new Date().getFullYear()

  // Buscar sacramentos e etapas da API
  useEffect(() => {
    async function fetchData() {
      try {
        // Buscar sacramentos
        const sacramentosData = await listarSacramentos()
        setSacramentos(sacramentosData)

        // Buscar etapas
        const etapasData = await listarEtapas()
        setEtapas(etapasData)
      } catch (err) {
        console.error('Erro ao buscar dados:', err)
        alert('Erro ao carregar dados. Tente novamente.')
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
      const idadeOk = anoNasc >= etapa.ano_nascimento_min && anoNasc <= etapa.ano_nascimento_max

      // TODO: Adicionar lógica de sacramentos quando a API retornar sacramentos_requeridos

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

  if (loading) {
    return <div className="loading-container">Carregando...</div>
  }

  return (
    <div className="etapa-container">
      {/* Cabeçalho Reutilizável */}
      <Header titulo="Catequese Divino Espírito Santo" />

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
                const idadeMin = anoAtual - etapa.ano_nascimento_max
                const idadeMax = anoAtual - etapa.ano_nascimento_min

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