// ../frontend/src/pages/GestaoEtapasPage.jsx
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { supabase } from '../services/supabaseClient'
import Header from '../components/Header/Header'
import {
  listarEtapas,
  criarEtapa,
  editarEtapa,
  excluirEtapa,
  listarSacramentos,
  buscarEtapa,
  listarCoordenadoresEtapa,
  atribuirCoordenadorEtapa
} from '../services/api'
import './GestaoEtapasPage.css'

function GestaoEtapasPage() {
  const navigate = useNavigate()
  const [etapas, setEtapas] = useState([])
  const [sacramentos, setSacramentos] = useState([])
  const [coordenadores, setCoordenadores] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editandoEtapa, setEditandoEtapa] = useState(null)
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    ano_nasc_minimo: '',
    ano_nasc_maximo: '',
    sacramentos_requeridos: [],
    sacramentos_proibidos: [],
    coordenador_etapa_id: ''
  })

  const anoAtual = new Date().getFullYear()

  useEffect(() => {
    window.scrollTo(0, 0)
    fetchData()
  }, [])

  async function fetchData() {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      const { data: { session } } = await supabase.auth.getSession()

      console.log('🔵 [fetchData] Usuário logado:', user)
      console.log('🔵 [fetchData] Session:', session)
      console.log('🔵 [fetchData] Token:', session?.access_token)

      // Buscar etapas
      const etapasData = await listarEtapas()

      // Buscar detalhes de cada etapa e coordenador
      const etapasComDetalhes = await Promise.all(
        etapasData.map(async (etapa) => {
          const detalhe = await buscarEtapa(etapa.id)

          // BUSCAR NOME DO COORDENADOR
          const { data: coordData } = await supabase
            .from('coordenador_etapa')
            .select(`
              id,
              nome,
              usuario_id
            `)
            .eq('etapa_id', etapa.id)
            .single()

          return {
            ...detalhe,
            coordenador_etapa_nome: coordData?.nome || null
          }
        })
      )

      setEtapas(etapasComDetalhes)

      // Buscar sacramentos
      const sacramentosData = await listarSacramentos()
      setSacramentos(sacramentosData)

      // Buscar coordenadores de etapa
      const coordenadoresData = await listarCoordenadoresEtapa()
      setCoordenadores(coordenadoresData)
    } catch (error) {
      console.error('Erro ao buscar dados:', error)
      alert('Erro ao carregar dados. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModal = async (etapa = null) => {
    if (etapa) {
      const etapaDetalhes = await buscarEtapa(etapa.id)

      // BUSCAR COORDENADOR ATUAL
      const { data: coordData } = await supabase
        .from('coordenador_etapa')
        .select('id')
        .eq('etapa_id', etapa.id)
        .single()

      setEditandoEtapa({
        ...etapaDetalhes,
        coordenador_etapa_nome: etapa.coordenador_etapa_nome
      })
      setFormData({
        nome: etapaDetalhes.nome || '',
        descricao: etapaDetalhes.descricao || '',
        ano_nasc_minimo: etapaDetalhes.ano_nasc_minimo || '',
        ano_nasc_maximo: etapaDetalhes.ano_nasc_maximo || '',
        sacramentos_requeridos: etapaDetalhes.sacramentos_requeridos || [],
        sacramentos_proibidos: etapaDetalhes.sacramentos_proibidos || [],
        coordenador_etapa_id: coordData?.id || ''
      })
    } else {
      setEditandoEtapa(null)
      setFormData({
        nome: '',
        descricao: '',
        ano_nasc_minimo: '',
        ano_nasc_maximo: '',
        sacramentos_requeridos: [],
        sacramentos_proibidos: [],
        coordenador_etapa_id: ''
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
      ano_nasc_maximo: '',
      sacramentos_requeridos: [],
      sacramentos_proibidos: [],
      coordenador_etapa_id: ''
    })
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSacramentoToggle = (sacramentoId, tipo) => {
    if (tipo === 'requeridos') {
      setFormData(prev => {
        const novosRequeridos = prev.sacramentos_requeridos.includes(sacramentoId)
          ? prev.sacramentos_requeridos.filter(id => id !== sacramentoId)
          : [...prev.sacramentos_requeridos, sacramentoId]

        const novosProibidos = prev.sacramentos_proibidos.filter(id => id !== sacramentoId)

        return {
          ...prev,
          sacramentos_requeridos: novosRequeridos,
          sacramentos_proibidos: novosProibidos
        }
      })
    } else if (tipo === 'proibidos') {
      setFormData(prev => {
        const novosProibidos = prev.sacramentos_proibidos.includes(sacramentoId)
          ? prev.sacramentos_proibidos.filter(id => id !== sacramentoId)
          : [...prev.sacramentos_proibidos, sacramentoId]

        const novosRequeridos = prev.sacramentos_requeridos.filter(id => id !== sacramentoId)

        return {
          ...prev,
          sacramentos_requeridos: novosRequeridos,
          sacramentos_proibidos: novosProibidos
        }
      })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.nome || !formData.ano_nasc_minimo || !formData.ano_nasc_maximo) {
      alert('Preencha todos os campos obrigatórios')
      return
    }

    if (parseInt(formData.ano_nasc_minimo) > parseInt(formData.ano_nasc_maximo)) {
      alert('O ano mínimo não pode ser maior que o ano máximo')
      return
    }

    try {
      const { data: { user } } = await supabase.auth.getUser()
      const { data: { session } } = await supabase.auth.getSession()

      console.log('🔵 [handleSubmit] Usuário logado:', user)
      console.log('🔵 [handleSubmit] Session:', session)
      console.log('🔵 [handleSubmit] Token:', session?.access_token)

      if (!user || !session) {
        alert('❌ Usuário não autenticado. Faça login novamente.')
        return
      }

      const dadosEtapa = {
        nome: formData.nome,
        descricao: formData.descricao,
        ano_nasc_minimo: parseInt(formData.ano_nasc_minimo),
        ano_nasc_maximo: parseInt(formData.ano_nasc_maximo),
        sacramentos_requeridos: formData.sacramentos_requeridos,
        sacramentos_proibidos: formData.sacramentos_proibidos
      }

      if (editandoEtapa) {
        await editarEtapa(editandoEtapa.id, dadosEtapa)

        const coordenadorId = formData.coordenador_etapa_id || null
        console.log('🔵 [handleSubmit] Atribuindo coordenador:', {
          etapaId: editandoEtapa.id,
          coordenadorId: coordenadorId
        })

        await atribuirCoordenadorEtapa(editandoEtapa.id, coordenadorId)

        alert('Etapa atualizada com sucesso!')
      } else {
        await criarEtapa(dadosEtapa)
        alert('Etapa criada com sucesso!')
      }

      handleCloseModal()
      fetchData()
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
      await excluirEtapa(etapaId)
      alert('Etapa excluída com sucesso!')
      fetchData()
    } catch (error) {
      console.error('Erro ao excluir etapa:', error)

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
          '⚠️ Não é possível excluir esta etapa.\n\n' +
          '📋 Motivo: Existem turmas vinculadas a ela.\n\n' +
          '✅ Solução: Exclua as turmas desta etapa primeiro.'
        )
      } else {
        alert('❌ Erro ao excluir etapa: ' + (error.message || 'Tente novamente.'))
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
          <h2 className="page-title">Gestão de Etapas</h2>
          <button className="nova-etapa-button" onClick={() => handleOpenModal()}>
            + NOVA ETAPA
          </button>
        </div>

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
                    {etapa.sacramentos_requeridos && etapa.sacramentos_requeridos.length > 0 && (
                      <p className="etapa-sacramentos">
                        <strong>Sacramentos requeridos:</strong>{' '}
                        {etapa.sacramentos_requeridos
                          .map(id => {
                            const sac = sacramentos.find(s => s.id === id)
                            return sac ? sac.nome_exibicao : id
                          })
                          .join(', ')}
                      </p>
                    )}
                    {etapa.sacramentos_proibidos && etapa.sacramentos_proibidos.length > 0 && (
                      <p className="etapa-sacramentos">
                        <strong>Sacramentos proibidos:</strong>{' '}
                        {etapa.sacramentos_proibidos
                          .map(id => {
                            const sac = sacramentos.find(s => s.id === id)
                            return sac ? sac.nome_exibicao : id
                          })
                          .join(', ')}
                      </p>
                    )}
                    {etapa.coordenador_etapa_nome && (
                      <p className="etapa-coordenador">
                        <strong>Coordenador:</strong> {etapa.coordenador_etapa_nome}
                      </p>
                    )}
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

              <div className="form-group">
                <label className="form-label">Coordenador de Etapa:</label>
                <select
                  name="coordenador_etapa_id"
                  value={formData.coordenador_etapa_id}
                  onChange={handleChange}
                  className="form-input"
                >
                  <option value="">Selecione um coordenador</option>
                  {coordenadores
                    .filter(coord => !coord.etapa_id || coord.etapa_id === editandoEtapa?.id)
                    .map(coord => (
                      <option key={coord.id} value={coord.id}>
                        {coord.nome} {coord.etapa_id && editandoEtapa?.id !== coord.etapa_id ? '(já vinculado)' : ''}
                      </option>
                    ))}
                </select>
                <p className="form-hint">
                  * Um coordenador só pode estar vinculado a uma etapa.
                </p>
              </div>

              <div className="form-group">
                <label className="form-label">Sacramentos Requeridos:</label>
                <div className="sacramentos-container">
                  {sacramentos.map(sacramento => (
                    <label key={sacramento.id} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={formData.sacramentos_requeridos.includes(sacramento.id)}
                        onChange={() => handleSacramentoToggle(sacramento.id, 'requeridos')}
                        disabled={formData.sacramentos_proibidos.includes(sacramento.id)}
                      />
                      <span>{sacramento.nome_exibicao}</span>
                      {formData.sacramentos_proibidos.includes(sacramento.id) && (
                        <small className="form-hint"> (proibido)</small>
                      )}
                    </label>
                  ))}
                </div>
                <p className="form-hint">
                  * Um sacramento não pode ser requerido e proibido ao mesmo tempo.
                </p>
              </div>

              <div className="form-group">
                <label className="form-label">Sacramentos Proibidos:</label>
                <div className="sacramentos-container">
                  {sacramentos.map(sacramento => (
                    <label key={sacramento.id} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={formData.sacramentos_proibidos.includes(sacramento.id)}
                        onChange={() => handleSacramentoToggle(sacramento.id, 'proibidos')}
                        disabled={formData.sacramentos_requeridos.includes(sacramento.id)}
                      />
                      <span>{sacramento.nome_exibicao}</span>
                      {formData.sacramentos_requeridos.includes(sacramento.id) && (
                        <small className="form-hint"> (requerido)</small>
                      )}
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