import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import logo from '../assets/logo.png'
import papel from '../assets/role.png'
import menu from '../assets/menu.png'
import { supabase } from '../services/supabaseClient'
import './GestaoEtapasPage.css'

function GestaoEtapasPage() {
  const navigate = useNavigate()
  const [etapas, setEtapas] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editandoEtapa, setEditandoEtapa] = useState(null)
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    ano_nasc_minimo: '',
    ano_nasc_maximo: ''
  })

  const anoAtual = new Date().getFullYear()

  // Buscar etapas do Supabase
  useEffect(() => {
    window.scrollTo(0, 0)
    fetchEtapas()
  }, [])

  async function fetchEtapas() {
    try {
      const { data, error } = await supabase
        .from('etapa')
        .select('*')
        .order('nome')

      if (error) throw error
      setEtapas(data || [])
    } catch (error) {
      console.error('Erro ao buscar etapas:', error)
      alert('Erro ao carregar etapas')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = (etapa = null) => {
    if (etapa) {
      setEditandoEtapa(etapa)
      setFormData({
        nome: etapa.nome || '',
        descricao: etapa.descricao || '',
        ano_nasc_minimo: etapa.ano_nasc_minimo || '',
        ano_nasc_maximo: etapa.ano_nasc_maximo || ''
      })
    } else {
      setEditandoEtapa(null)
      setFormData({
        nome: '',
        descricao: '',
        ano_nasc_minimo: '',
        ano_nasc_maximo: ''
      })
    }
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditandoEtapa(null)
    setFormData({
      nome: '',
      descricao: '',
      ano_nasc_minimo: '',
      ano_nasc_maximo: ''
    })
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.nome || !formData.ano_nasc_minimo || !formData.ano_nasc_maximo) {
      alert('Preencha todos os campos obrigatórios')
      return
    }

    try {
      if (editandoEtapa) {
        // Editar etapa existente
        const { error } = await supabase
          .from('etapa')
          .update({
            nome: formData.nome,
            descricao: formData.descricao,
            ano_nasc_minimo: parseInt(formData.ano_nasc_minimo),
            ano_nasc_maximo: parseInt(formData.ano_nasc_maximo)
          })
          .eq('id', editandoEtapa.id)

        if (error) throw error
        alert('Etapa atualizada com sucesso!')
      } else {
        // Criar nova etapa
        const { error } = await supabase
          .from('etapa')
          .insert([{
            nome: formData.nome,
            descricao: formData.descricao,
            ano_nasc_minimo: parseInt(formData.ano_nasc_minimo),
            ano_nasc_maximo: parseInt(formData.ano_nasc_maximo)
          }])

        if (error) throw error
        alert('Etapa criada com sucesso!')
      }

      handleCloseModal()
      fetchEtapas()
    } catch (error) {
      console.error('Erro ao salvar etapa:', error)
      alert(`Erro: ${error.message}`)
    }
  }

  const handleExcluir = async (etapaId, etapaNome) => {
    if (!confirm(`Tem certeza que deseja excluir a etapa "${etapaNome}"?`)) {
      return
    }

    try {
      const { error } = await supabase
        .from('etapa')
        .delete()
        .eq('id', etapaId)

      if (error) throw error
      alert('Etapa excluída com sucesso!')
      fetchEtapas()
    } catch (error) {
      console.error('Erro ao excluir etapa:', error)
      alert(`Erro: ${error.message}`)
    }
  }

  const handlePerfilClick = () => {
    alert('Menu de perfis (será implementado depois)')
  }

  const handleMenuClick = () => {
    alert('Menu de navegação (será implementado depois)')
  }

  if (loading) {
    return <div className="loading-container">Carregando...</div>
  }

  return (
    <div className="gestao-container">
      {/* Cabeçalho */}
      <header className="gestao-header">
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
      <main className="gestao-content">
        <div className="gestao-header-content">
          <h2 className="page-title">Gestão de Etapas</h2>
          <button className="nova-etapa-button" onClick={() => handleOpenModal()}>
            + NOVA ETAPA
          </button>
        </div>

        {/* Lista de Etapas */}
        <div className="etapas-list">
          {etapas.length === 0 ? (
            <p className="sem-etapas">Nenhuma etapa cadastrada</p>
          ) : (
            etapas.map(etapa => {
              const idadeMin = anoAtual - etapa.ano_nasc_maximo
              const idadeMax = anoAtual - etapa.ano_nasc_minimo

              return (
                <div key={etapa.id} className="etapa-card">
                  <div className="etapa-info">
                    <h3 className="etapa-nome">{etapa.nome}</h3>
                    {etapa.descricao && (
                      <p className="etapa-desc">{etapa.descricao}</p>
                    )}
                    <p className="etapa-idade">
                      Idade (neste ano): {idadeMin} a {idadeMax} anos
                    </p>
                    <p className="etapa-anos">
                      Nascimentos: {etapa.ano_nasc_minimo} - {etapa.ano_nasc_maximo}
                    </p>
                  </div>
                  <div className="etapa-actions">
                    <button
                      className="editar-button"
                      onClick={() => handleOpenModal(etapa)}
                    >
                      Editar
                    </button>
                    <button
                      className="excluir-button"
                      onClick={() => handleExcluir(etapa.id, etapa.nome)}
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

      {/* Modal de Cadastro/Edição */}
      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">
              {editandoEtapa ? 'Editar Etapa' : 'Nova Etapa'}
            </h3>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Nome da Etapa: *</label>
                <input
                  type="text"
                  name="nome"
                  value={formData.nome}
                  onChange={handleChange}
                  className="form-input"
                  required
                  placeholder="Ex: 1ª Etapa - Batismo"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Descrição:</label>
                <textarea
                  name="descricao"
                  value={formData.descricao}
                  onChange={handleChange}
                  className="form-textarea"
                  rows="3"
                  placeholder="Ex: Preparação para o Batismo"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Ano Nascimento Mínimo: *</label>
                  <input
                    type="number"
                    name="ano_nasc_minimo"
                    value={formData.ano_nasc_minimo}
                    onChange={handleChange}
                    className="form-input"
                    required
                    placeholder="Ex: 2017"
                    min="1900"
                    max={anoAtual}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Ano Nascimento Máximo: *</label>
                  <input
                    type="number"
                    name="ano_nasc_maximo"
                    value={formData.ano_nasc_maximo}
                    onChange={handleChange}
                    className="form-input"
                    required
                    placeholder="Ex: 2018"
                    min="1900"
                    max={anoAtual}
                  />
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
                  {editandoEtapa ? 'SALVAR' : 'CRIAR'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default GestaoEtapasPage