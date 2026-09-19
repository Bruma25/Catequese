// src/pages/GestaoUsuariosPage.jsx
import { useState, useEffect } from 'react'
import Header from '../components/Header/Header'
import {
  listarUsuarios,
  criarUsuario,
  editarUsuario,
  excluirUsuario,
  listarPapeis,
  atualizarPapeisUsuario
} from '../services/api'
import { User, Edit, Trash2, Save, X, Plus } from 'lucide-react'
import './GestaoUsuariosPage.css'

function GestaoUsuariosPage() {
  const [usuarios, setUsuarios] = useState([])
  const [papeis, setPapeis] = useState([])
  const [loading, setLoading] = useState(true)
  const [filtroPapel, setFiltroPapel] = useState('')

  // Modal
  const [showModal, setShowModal] = useState(false)
  const [editandoUsuario, setEditandoUsuario] = useState(null)
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    papeis_ids: []
  })

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      const [usuariosData, papeisData] = await Promise.all([
        listarUsuarios(),
        listarPapeis()
      ])

      console.log('📋 Usuários:', usuariosData)
      console.log('📋 Papéis:', papeisData)

      setUsuarios(usuariosData)
      setPapeis(papeisData)
    } catch (error) {
      console.error('Erro ao buscar dados:', error)
      alert('Erro ao carregar dados.')
    } finally {
      setLoading(false)
    }
  }

  // ✅ Filtro corrigido
  const usuariosFiltrados = usuarios.filter(usuario => {
    if (!filtroPapel) return true

    return usuario.papeis?.some(papel => {
      return String(papel.id) === String(filtroPapel)
    })
  })

  const handleOpenModal = (usuario = null) => {
    if (usuario) {
      setEditandoUsuario(usuario)
      setFormData({
        nome: usuario.nome || '',
        email: usuario.email || '',
        papeis_ids: usuario.papeis?.map(p => p.id) || []
      })
    } else {
      setEditandoUsuario(null)
      setFormData({
        nome: '',
        email: '',
        papeis_ids: []
      })
    }
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditandoUsuario(null)
    setFormData({
      nome: '',
      email: '',
      papeis_ids: []
    })
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handlePapelToggle = (papelId) => {
    setFormData(prev => ({
      ...prev,
      papeis_ids: prev.papeis_ids.includes(papelId)
        ? prev.papeis_ids.filter(id => id !== papelId)
        : [...prev.papeis_ids, papelId]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.nome || !formData.email) {
      alert('Preencha nome e email')
      return
    }

    try {
      const dadosUsuario = {
        nome: formData.nome,
        email: formData.email,
        papeis_ids: formData.papeis_ids
      }

      if (editandoUsuario) {
        await editarUsuario(editandoUsuario.id, dadosUsuario)
        alert('Usuário atualizado com sucesso!')
      } else {
        await criarUsuario(dadosUsuario)
        alert('Usuário criado com sucesso!')
      }

      handleCloseModal()
      fetchData()
    } catch (error) {
      console.error('Erro ao salvar usuário:', error)
      alert(`Erro: ${error.message}`)
    }
  }

  const handleExcluir = async (usuarioId, usuarioNome) => {
    if (!confirm(`Tem certeza que deseja excluir o usuário "${usuarioNome}"?`)) {
      return
    }

    try {
      await excluirUsuario(usuarioId)
      alert('Usuário excluído com sucesso!')
      fetchData()
    } catch (error) {
      console.error('Erro ao excluir usuário:', error)
      alert(`Erro: ${error.message}`)
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
          <h2 className="page-title">Gestão de Usuários</h2>
          <button className="novo-usuario-button" onClick={() => handleOpenModal()}>
            <Plus size={18} />
            NOVO USUÁRIO
          </button>
        </div>

        {/* Filtro por Papel */}
        <div className="filtros-container">
          <div className="filtro-group">
            <label className="filtro-label">Filtrar por Papel:</label>
            <select
              value={filtroPapel}
              onChange={(e) => setFiltroPapel(e.target.value)}
              className="filtro-select"
            >
              <option value="">Todos os papéis</option>
              {papeis.map(papel => (
                <option key={papel.id} value={papel.id}>
                  {papel.descricao}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Lista de Usuários */}
        <div className="usuarios-list">
          {usuariosFiltrados.length === 0 ? (
            <p className="sem-usuarios">
              {filtroPapel
                ? 'Nenhum usuário encontrado para este papel'
                : 'Nenhum usuário cadastrado'}
            </p>
          ) : (
            usuariosFiltrados.map(usuario => (
              <div key={usuario.id} className="usuario-card">
                <div className="usuario-info">
                  <div className="usuario-header">
                    <User size={24} className="usuario-icon" />
                    <h3 className="usuario-nome">{usuario.nome || 'Sem nome'}</h3>
                  </div>
                  <p className="usuario-email">{usuario.email || 'Sem email'}</p>
                  <div className="usuario-papeis">
                    <strong>Papéis:</strong>{' '}
                    {usuario.papeis && usuario.papeis.length > 0
                      ? usuario.papeis.map(p => p.descricao).join(', ')
                      : 'Nenhum papel'}
                  </div>
                </div>
                <div className="usuario-actions">
                  <button
                    className="editar-button"
                    onClick={() => handleOpenModal(usuario)}
                  >
                    <Edit size={16} />
                    Editar
                  </button>
                  <button
                    className="excluir-button"
                    onClick={() => handleExcluir(usuario.id, usuario.nome || usuario.email)}
                  >
                    <Trash2 size={16} />
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
              {editandoUsuario ? 'Editar Usuário' : 'Novo Usuário'}
            </h3>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Nome: *</label>
                <input
                  type="text"
                  name="nome"
                  value={formData.nome}
                  onChange={handleChange}
                  className="form-input"
                  required
                  placeholder="Nome completo"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email: *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="form-input"
                  required
                  placeholder="email@exemplo.com"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Papéis:</label>
                <div className="papeis-container">
                  {papeis.map(papel => (
                    <label key={papel.id} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={formData.papeis_ids.includes(papel.id)}
                        onChange={() => handlePapelToggle(papel.id)}
                      />
                      <span>{papel.descricao}</span>
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
                  <X size={18} />
                  Cancelar
                </button>
                <button type="submit" className="salvar-button">
                  <Save size={18} />
                  {editandoUsuario ? 'SALVAR' : 'CRIAR'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default GestaoUsuariosPage