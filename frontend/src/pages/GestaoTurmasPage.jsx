// ../frontend/src/pages/GestaoTurmasPage.jsx
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { supabase } from '../services/supabaseClient'
import Header from '../components/Header/Header'
import {
  listarTurmas,
  criarTurma,
  editarTurma,
  excluirTurma,
  listarEtapas,
  listarLocaisEncontro,
  listarCatequistas,
  contarInscricoesPorTurma,
  buscarTurmaPorId
} from '../services/api'
import './GestaoTurmasPage.css'

function GestaoTurmasPage() {
  const navigate = useNavigate()
  const [turmas, setTurmas] = useState([])
  const [etapas, setEtapas] = useState([])
  const [locaisEncontro, setLocaisEncontro] = useState([])
  const [catequistas, setCatequistas] = useState([])
  const [inscricoesPorTurma, setInscricoesPorTurma] = useState({})
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editandoTurma, setEditandoTurma] = useState(null)
  const [filtroEtapa, setFiltroEtapa] = useState('')
  const [formData, setFormData] = useState({
    etapa_id: '',
    nome_sistema: '',
    nome_exibicao: '',
    vagas_totais: '',
    ativa: true,
    local_encontro_id: '',
    ano_nasc_minimo: '',
    ano_nasc_maximo: '',
    catequistas_ids: []
  })

  useEffect(() => {
    window.scrollTo(0, 0)
    fetchData()
  }, [])

  async function fetchData() {
    try {
      const [turmasData, etapasData, locaisData, catequistasData] = await Promise.all([
        listarTurmas(),
        listarEtapas(),
        listarLocaisEncontro(),
        listarCatequistas()
      ])

      // BUSCAR CATEQUISTAS DE CADA TURMA
      const turmasComCatequistas = await Promise.all(
        turmasData.map(async (turma) => {
          const { data: turmaCatequistas } = await supabase
            .from('turma_catequista')
            .select(`
              catequista_id,
              catequista:catequista_id (
                id,
                nome
              )
            `)
            .eq('turma_id', turma.id)

          const catequistasDaTurma = turmaCatequistas && turmaCatequistas.length > 0
            ? turmaCatequistas.map(tc => tc.catequista).filter(c => c !== null)
            : []

          return {
            ...turma,
            catequistas: catequistasDaTurma
          }
        })
      )

      setTurmas(turmasComCatequistas)
      setEtapas(etapasData)
      setLocaisEncontro(locaisData)
      setCatequistas(catequistasData)

      // Buscar quantidade de inscrições por turma
      const inscricoes = await Promise.all(
        turmasData.map(async (turma) => {
          const count = await contarInscricoesPorTurma(turma.id)
          return { turmaId: turma.id, count }
        })
      )

      const inscricoesMap = {}
      inscricoes.forEach(({ turmaId, count }) => {
        inscricoesMap[turmaId] = count
      })
      setInscricoesPorTurma(inscricoesMap)
    } catch (error) {
      console.error('Erro ao buscar dados:', error)
      alert('Erro ao carregar dados. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const turmasFiltradas = turmas.filter(turma => {
    if (!filtroEtapa) return true
    return turma.etapa_id === filtroEtapa
  })

  const handleOpenModal = async (turma = null) => {
    if (turma) {
      const turmaDetalhes = await buscarTurmaPorId(turma.id)

      setEditandoTurma(turmaDetalhes)
      setFormData({
        etapa_id: turmaDetalhes.etapa_id || '',
        nome_sistema: turmaDetalhes.nome_sistema || '',
        nome_exibicao: turmaDetalhes.nome_exibicao || '',
        vagas_totais: turmaDetalhes.vagas_totais || '',
        ativa: turmaDetalhes.ativa ?? true,
        local_encontro_id: turmaDetalhes.local_encontro_id || '',
        ano_nasc_minimo: turmaDetalhes.ano_nasc_minimo || '',
        ano_nasc_maximo: turmaDetalhes.ano_nasc_maximo || '',
        catequistas_ids: turmaDetalhes.catequistas?.map(c => c.id) || []
      })
    } else {
      setEditandoTurma(null)
      setFormData({
        etapa_id: '',
        nome_sistema: '',
        nome_exibicao: '',
        vagas_totais: '',
        ativa: true,
        local_encontro_id: '',
        ano_nasc_minimo: '',
        ano_nasc_maximo: '',
        catequistas_ids: []
      })
    }
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditandoTurma(null)
    setFormData({
      etapa_id: '',
      nome_sistema: '',
      nome_exibicao: '',
      vagas_totais: '',
      ativa: true,
      local_encontro_id: '',
      ano_nasc_minimo: '',
      ano_nasc_maximo: '',
      catequistas_ids: []
    })
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleCatequistaToggle = (catequistaId) => {
    setFormData(prev => ({
      ...prev,
      catequistas_ids: prev.catequistas_ids.includes(catequistaId)
        ? prev.catequistas_ids.filter(id => id !== catequistaId)
        : [...prev.catequistas_ids, catequistaId]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.etapa_id || !formData.nome_sistema || !formData.vagas_totais) {
      alert('Preencha todos os campos obrigatórios')
      return
    }

    try {
      const dadosTurma = {
        etapa_id: formData.etapa_id,
        nome_sistema: formData.nome_sistema,
        nome_exibicao: formData.nome_exibicao || null,
        vagas_totais: parseInt(formData.vagas_totais),
        ativa: formData.ativa,
        local_encontro_id: formData.local_encontro_id || null,
        ano_nasc_minimo: formData.ano_nasc_minimo ? parseInt(formData.ano_nasc_minimo) : null,
        ano_nasc_maximo: formData.ano_nasc_maximo ? parseInt(formData.ano_nasc_maximo) : null,
        catequistas_ids: formData.catequistas_ids
      }

      if (editandoTurma) {
        await editarTurma(editandoTurma.id, dadosTurma)
        alert('Turma atualizada com sucesso!')
      } else {
        await criarTurma(dadosTurma)
        alert('Turma criada com sucesso!')
      }

      handleCloseModal()
      fetchData()
    } catch (error) {
      console.error('Erro ao salvar turma:', error)
      alert(`Erro: ${error.message}`)
    }
  }

  const handleExcluir = async (turmaId, turmaNome) => {
    if (!confirm(`Tem certeza que deseja excluir a turma "${turmaNome}"?`)) {
      return
    }

    try {
      await excluirTurma(turmaId)
      alert('Turma excluída com sucesso!')
      fetchData()
    } catch (error) {
      console.error('Erro ao excluir turma:', error)

      const errorMsg = error.message || ''
      const errorCode = error.code || ''
      const errorDetail = error.detail || ''

      if (
        errorCode === '23503' ||
        errorMsg.includes('foreign key') ||
        errorMsg.includes('violates foreign key') ||
        errorDetail.includes('still referenced from table')
      ) {
        alert(
          '⚠️ Não é possível excluir esta turma.\n\n' +
          '📋 Motivo: Existem catequizandos inscritos nela.\n\n' +
          '✅ Solução: Exclua as inscrições dos catequizandos desta turma primeiro.'
        )
      } else {
        alert('❌ Erro ao excluir turma: ' + (error.message || 'Tente novamente.'))
      }
    }
  }

  if (loading) {
    return <div className="loading-container">Carregando...</div>
  }

  return (
    <div className="gestao-container">
      <Header titulo="Catequese Divino Espírito Santo" />

      <main className="gestao-content">
        <div className="gestao-header-content">
          <h2 className="page-title">Gestão de Turmas</h2>
          <button className="nova-turma-button" onClick={() => handleOpenModal()}>
            + NOVA TURMA
          </button>
        </div>

        <div className="filtros-container">
          <div className="filtro-group">
            <label className="filtro-label">Filtrar por Etapa:</label>
            <select
              value={filtroEtapa}
              onChange={(e) => setFiltroEtapa(e.target.value)}
              className="filtro-select"
            >
              <option value="">Todas as etapas</option>
              {etapas.map(etapa => (
                <option key={etapa.id} value={etapa.id}>
                  {etapa.nome}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="turmas-list">
          {turmasFiltradas.length === 0 ? (
            <p className="sem-turmas">
              {filtroEtapa
                ? 'Nenhuma turma encontrada para esta etapa'
                : 'Nenhuma turma cadastrada'}
            </p>
          ) : (
            turmasFiltradas.map(turma => {
              const vagasOcupadas = inscricoesPorTurma[turma.id] || 0
              const vagasTotais = turma.vagas_totais

              return (
                <div key={turma.id} className="turma-card">
                  <div className="turma-info">
                    <h3 className="turma-nome">
                      {turma.nome_exibicao || turma.nome_sistema}
                    </h3>
                    <p className="turma-etapa">
                      Etapa: {etapas.find(e => e.id === turma.etapa_id)?.nome || 'N/A'}
                    </p>
                    <p className="turma-vagas">
                      Vagas: {vagasOcupadas}/{vagasTotais}
                    </p>
                    <p className={`turma-status ${turma.ativa ? 'ativa' : 'inativa'}`}>
                      Status: {turma.ativa ? 'Ativa' : 'Inativa'}
                    </p>
                    {turma.catequistas && turma.catequistas.length > 0 ? (
                      <p className="turma-catequistas">
                        <strong>Catequistas:</strong> {turma.catequistas.map(c => c.nome).join(', ')}
                      </p>
                    ) : (
                      <p className="sem-catequistas">
                        Sem catequistas
                      </p>
                    )}
                  </div>
                  <div className="turma-actions">
                    <button
                      className="editar-button"
                      onClick={() => handleOpenModal(turma)}
                    >
                      Editar
                    </button>
                    <button
                      className="excluir-button"
                      onClick={() => handleExcluir(turma.id, turma.nome_exibicao || turma.nome_sistema)}
                    >
                      Excluir
                    </button>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </main>

      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">
              {editandoTurma ? 'Editar Turma' : 'Nova Turma'}
            </h3>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Etapa: *</label>
                <select
                  name="etapa_id"
                  value={formData.etapa_id}
                  onChange={handleChange}
                  className="form-input"
                  required
                >
                  <option value="">Selecione uma etapa</option>
                  {etapas.map(etapa => (
                    <option key={etapa.id} value={etapa.id}>
                      {etapa.nome}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Nome do Sistema: *</label>
                <input
                  type="text"
                  name="nome_sistema"
                  value={formData.nome_sistema}
                  onChange={handleChange}
                  className="form-input"
                  required
                  placeholder="Ex: TURMA_EUC_2026_A"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Nome de Exibição:</label>
                <input
                  type="text"
                  name="nome_exibicao"
                  value={formData.nome_exibicao}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="Ex: Primeira Eucaristia 2026 - Turma A"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Vagas Totais: *</label>
                  <input
                    type="number"
                    name="vagas_totais"
                    value={formData.vagas_totais}
                    onChange={handleChange}
                    className="form-input"
                    required
                    min="1"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Ativa:</label>
                  <select
                    name="ativa"
                    value={formData.ativa ? 'true' : 'false'}
                    onChange={handleChange}
                    className="form-input"
                  >
                    <option value="true">Sim</option>
                    <option value="false">Não</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Local de Encontro:</label>
                <select
                  name="local_encontro_id"
                  value={formData.local_encontro_id}
                  onChange={handleChange}
                  className="form-input"
                >
                  <option value="">Selecione um local</option>
                  {locaisEncontro.map(local => (
                    <option key={local.id} value={local.id}>
                      {local.nome_exibicao}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Ano Nascimento Mínimo:</label>
                  <input
                    type="number"
                    name="ano_nasc_minimo"
                    value={formData.ano_nasc_minimo}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Ex: 2015"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Ano Nascimento Máximo:</label>
                  <input
                    type="number"
                    name="ano_nasc_maximo"
                    value={formData.ano_nasc_maximo}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Ex: 2016"
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Catequistas:</label>
                <div className="catequistas-container">
                  {catequistas.map(catequista => (
                    <label key={catequista.id} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={formData.catequistas_ids.includes(catequista.id)}
                        onChange={() => handleCatequistaToggle(catequista.id)}
                      />
                      <span>{catequista.nome}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="cancelar-button"
                  onClick={handleCloseModal}
                >
                  Cancelar
                </button>
                <button type="submit" className="salvar-button">
                  {editandoTurma ? 'SALVAR' : 'CRIAR'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default GestaoTurmasPage