// ../frontend/src/pages/EtapaPage.jsx
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Header from '../components/Header/Header'
import { listarEtapas, listarSacramentos, verificarVagasEtapa } from '../services/api'
import './EtapaPage.css'

function EtapaPage() {
  const navigate = useNavigate()
  const [dataNascimento, setDataNascimento] = useState('')
  const [sacramentosSelecionados, setSacramentosSelecionados] = useState([])
  const [etapasFiltradas, setEtapasFiltradas] = useState([])
  const [etapas, setEtapas] = useState([])
  const [sacramentos, setSacramentos] = useState([])
  const [loading, setLoading] = useState(true)

  // Estado para popup de confirmação
  const [showConfirmModal, setShowConfirmModal] = useState(false)
  const [etapaParaInscricao, setEtapaParaInscricao] = useState(null)
  const [vagasInfo, setVagasInfo] = useState(null)

  const anoAtual = new Date().getFullYear()

  // Buscar sacramentos e etapas da API
  useEffect(() => {
    async function fetchData() {
      try {
        const sacramentosData = await listarSacramentos()
        setSacramentos(sacramentosData)

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
      const idadeOk = (
        (!etapa.ano_nascimento_min || anoNasc >= etapa.ano_nascimento_min) &&
        (!etapa.ano_nascimento_max || anoNasc <= etapa.ano_nascimento_max)
      )

      const temSacramentosRequeridos = !etapa.sacramentos_requeridos || etapa.sacramentos_requeridos.length === 0 ||
        etapa.sacramentos_requeridos.every(
          sacramentoRequerido => sacramentosSelecionados.includes(sacramentoRequerido)
        )

      const naoTemSacramentosProibidos = !etapa.sacramentos_proibidos || etapa.sacramentos_proibidos.length === 0 ||
        !etapa.sacramentos_proibidos.some(
          sacramentoProibido => sacramentosSelecionados.includes(sacramentoProibido)
        )

      return idadeOk && temSacramentosRequeridos && naoTemSacramentosProibidos
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

  //Verificar vagas e mostrar popup
  const handleSelecionarEtapa = async (etapa) => {
    try {
      const vagasData = await verificarVagasEtapa(etapa.id)
      setVagasInfo(vagasData)

      if (vagasData.sem_vagas) {
        // Mostrar popup de confirmação
        setEtapaParaInscricao(etapa)
        setShowConfirmModal(true)
      } else {
        // Vagas disponíveis, ir direto para ficha
        localStorage.setItem('inscricao_data', JSON.stringify({
          dataNascimento,
          sacramentos: sacramentosSelecionados,
          etapaSelecionada: etapa,
          sem_vagas: false
        }))
        navigate('/inscricao')
      }
    } catch (error) {
      console.error('Erro ao verificar vagas:', error)
      // Em caso de erro, permitir inscrição normalmente
      localStorage.setItem('inscricao_data', JSON.stringify({
        dataNascimento,
        sacramentos: sacramentosSelecionados,
        etapaSelecionada: etapa,
        sem_vagas: false
      }))
      navigate('/inscricao')
    }
  }

  // CONFIRMAR: Usuário quer continuar para fila de espera
  const handleConfirmarInscricao = () => {
    if (etapaParaInscricao) {
      localStorage.setItem('inscricao_data', JSON.stringify({
        dataNascimento,
        sacramentos: sacramentosSelecionados,
        etapaSelecionada: etapaParaInscricao,
        sem_vagas: true
      }))
      navigate('/inscricao')
    }
    setShowConfirmModal(false)
    setEtapaParaInscricao(null)
  }

  // CANCELAR: Usuário não quer continuar
  const handleCancelarInscricao = () => {
    setShowConfirmModal(false)
    setEtapaParaInscricao(null)
  }

  if (loading) {
    return <div className="loading-container">Carregando...</div>
  }

  return (
    <div className="etapa-container">
      <Header titulo="Catequese Divino Espírito Santo" />

      <main className="etapa-content">
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

      {/* MODAL DE CONFIRMAÇÃO */}
      {showConfirmModal && (
        <div className="modal-overlay" onClick={handleCancelarInscricao}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-icon">⚠️</div>
            <h3 className="modal-title">Atenção: Vagas Preenchidas</h3>
            <p className="modal-text">
              As vagas para <strong>{etapaParaInscricao?.nome}</strong> já foram preenchidas.
            </p>
            <p className="modal-text">
              Você pode continuar e sua inscrição será incluída na <strong>fila de espera</strong>.
              Assim que houver vaga disponível, entraremos em contato.
            </p>
            <div className="modal-actions">
              <button
                className="modal-button cancelar"
                onClick={handleCancelarInscricao}
              >
                Cancelar
              </button>
              <button
                className="modal-button confirmar"
                onClick={handleConfirmarInscricao}
              >
                Continuar para Fila de Espera
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default EtapaPage