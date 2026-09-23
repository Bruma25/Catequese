// frontend/src/pages/ConfiguracaoPeriodosPage.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/Header/Header'
import './ConfiguracaoPeriodosPage.css'

function ConfiguracaoPeriodosPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  const [dataInicioCatequese, setDataInicioCatequese] = useState('')
  const [dataFimCatequese, setDataFimCatequese] = useState('')

  const [dataInicioJovens, setDataInicioJovens] = useState('')
  const [dataFimJovens, setDataFimJovens] = useState('')

  useEffect(() => {
    carregarPeriodos()
  }, [])

  async function carregarPeriodos() {
    try {
      const periodos = localStorage.getItem('periodos_inscricao')

      if (periodos) {
        const dados = JSON.parse(periodos)
        setDataInicioCatequese(dados.catequese?.inicio || '')
        setDataFimCatequese(dados.catequese?.fim || '')
        setDataInicioJovens(dados.jovens?.inicio || '')
        setDataFimJovens(dados.jovens?.fim || '')
      }
    } catch (error) {
      console.error('Erro ao carregar períodos:', error)
    }
  }

  async function handleSalvar() {
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      if (!dataInicioCatequese || !dataFimCatequese) {
        throw new Error('Preencha as datas de inscrição para catequese')
      }

      if (!dataInicioJovens || !dataFimJovens) {
        throw new Error('Preencha as datas de inscrição para jovens e adultos')
      }

      const periodos = {
        catequese: {
          inicio: dataInicioCatequese,
          fim: dataFimCatequese
        },
        jovens: {
          inicio: dataInicioJovens,
          fim: dataFimJovens
        }
      }

      localStorage.setItem('periodos_inscricao', JSON.stringify(periodos))

      window.dispatchEvent(new Event('storage'))

      setSuccess('Períodos de inscrição atualizados com sucesso!')
    } catch (err) {
      setError(err.message || 'Erro ao salvar períodos')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="config-periodos-container">
      <Header titulo="Catequese Divino Espírito Santo" />

      <main className="config-periodos-content">
        <h1 className="config-periodos-title">Configurar Períodos de Inscrição</h1>

        {error && (
          <div className="error-message">{error}</div>
        )}

        {success && (
          <div className="success-message">{success}</div>
        )}

        <div className="periodo-section">
          <h2 className="section-title">Catequese</h2>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Data de Início:</label>
              <input
                type="date"
                value={dataInicioCatequese}
                onChange={(e) => setDataInicioCatequese(e.target.value)}
                className="form-input"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Data de Fim:</label>
              <input
                type="date"
                value={dataFimCatequese}
                onChange={(e) => setDataFimCatequese(e.target.value)}
                className="form-input"
                disabled={loading}
              />
            </div>
          </div>
        </div>

        <div className="periodo-section">
          <h2 className="section-title">Catequese de Jovens e Adultos</h2>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Data de Início:</label>
              <input
                type="date"
                value={dataInicioJovens}
                onChange={(e) => setDataInicioJovens(e.target.value)}
                className="form-input"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Data de Fim:</label>
              <input
                type="date"
                value={dataFimJovens}
                onChange={(e) => setDataFimJovens(e.target.value)}
                className="form-input"
                disabled={loading}
              />
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button
            className="btn-salvar"
            onClick={handleSalvar}
            disabled={loading}
          >
            💾 Salvar Períodos
          </button>
        </div>
      </main>
    </div>
  )
}

export default ConfiguracaoPeriodosPage