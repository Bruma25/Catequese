import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Header from '../components/Header/Header'
import {
  listarTurmas,
  criarTurma,
  editarTurma,
  excluirTurma,
  listarEtapas,
  listarLocaisEncontro,
  listarCatequistas
} from '../services/api'
import './GestaoTurmasPage.css'

function GestaoTurmasPage() {
  const navigate = useNavigate()
  const [turmas, setTurmas] = useState([])
  const [etapas, setEtapas] = useState([])
  const [locaisEncontro, setLocaisEncontro] = useState([])
  const [catequistas, setCatequistas] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editandoTurma, setEditandoTurma] = useState(null)
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

  // Buscar dados da API
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

      setTurmas(turmasData)
      setEtapas(etapasData)
      setLocaisEncontro(locaisData)
      setCatequistas(catequistasData)
    } catch (error) {
      console.error('Erro ao buscar dados:', error)
      alert('Erro ao carregar dados. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = (turma = null) => {
    if (turma) {
      setEditandoTurma(turma)
      setFormData({
        etapa_id: turma.etapa_id || '',
        nome_sistema: turma.nome_sistema || '',
        nome_exibicao: turma.nome_exibicao || '',
        vagas_totais: turma.vagas_totais || '',
        ativa: turma.ativa ?? true,
        local_encontro_id: turma.local_encontro_id || '',
        ano_nasc_minimo: turma.ano_nasc_minimo || '',
        ano_nasc_maximo: turma.ano_nasc_maximo || '',
        catequistas_ids: []
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
      alert(`Erro: ${error.message}`)
    }
  }

  if (loading) {
    return <div className="loading-container">Carregando...</div>
  }

  return (
    <div className="gestao-container">
      {/* Cabeçalho Reutilizável */}
      <Header titulo="Catequese Divino Espírito Santo" />

      {/* Conteúdo Principal */}
      <main className="gestao-content">
        <div className="gestao-header-content">
          <h2 className="page-title">Gestão de Turmas</h2>
          <button className="nova-turma-button" onClick={() => handleOpenModal()}>
            + NOVA TURMA
          </button>
        </div>

        {/* Lista de Turmas */}
        <div className="turmas-list">
          {turmas.length === 0 ? (
            <p className="sem-turmas">Nenhuma turma cadastrada</p>
          ) : (
            turmas.map(turma => (
              <div key={turma.id} className="turma-card">
                <div className="turma-info">
                  <h3 className="turma-nome">{turma.nome_exibicao || turma.nome_sistema}</h3>
                  <p className="turma-etapa">
                    Etapa: {etapas.find(e => e.id === turma.etapa_id)?.nome || 'N/A'}
                  </p>
                  <p className="turma-vagas">Vagas: {turma.vagas_totais}</p>
                  <p className={`turma-status ${turma.ativa ? 'ativa' : 'inativa'}`}>
                    Status: {turma.ativa ? 'Ativa' : 'Inativa'}
                  </p>
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
            ))
          )}
        </div>
      </main>

      {/* Modal de Cadastro/Edição */}
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

              {/* Catequistas */}
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