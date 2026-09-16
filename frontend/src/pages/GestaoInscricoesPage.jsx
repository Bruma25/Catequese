import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Header from '../components/Header/Header'
import {
  listarInscricoes,
  listarEtapas,
  atribuirTurmaInscricao,
  removerTurmaInscricao,
  buscarInscricaoCompleta,
  listarTurmas,
  listarDocumentosInscricao,
  atualizarStatusDocumento
} from '../services/api'
import './GestaoInscricoesPage.css'

function GestaoInscricoesPage() {
  const navigate = useNavigate()
  const [inscricoes, setInscricoes] = useState([])
  const [etapas, setEtapas] = useState([])
  const [turmas, setTurmas] = useState([])
  const [loading, setLoading] = useState(true)
  const [filtroEtapa, setFiltroEtapa] = useState('')
  const [filtroStatus, setFiltroStatus] = useState('')
  const [inscricaoSelecionada, setInscricaoSelecionada] = useState(null)
  const [showModalDetalhes, setShowModalDetalhes] = useState(false)
  const [showModalTurma, setShowModalTurma] = useState(false)
  const [showModalDocumentos, setShowModalDocumentos] = useState(false)
  const [turmaParaAtribuir, setTurmaParaAtribuir] = useState('')
  const [documentos, setDocumentos] = useState([])

  // Status
  const statusMap = {
    1: { codigo: 'pendente_distribuicao', label: 'Pendente', class: 'status-pendente' },
    2: { codigo: 'confirmada', label: 'Confirmada', class: 'status-confirmada' },
    3: { codigo: 'lista_espera', label: 'Lista de Espera', class: 'status-espera' },
    4: { codigo: 'cancelada', label: 'Cancelada', class: 'status-cancelada' },
    5: { codigo: 'distribuida', label: 'Distribuída', class: 'status-distribuida' }
  }

  // Buscar dados
  useEffect(() => {
    window.scrollTo(0, 0)
    fetchData()
  }, [])

  async function fetchData() {
    try {
      const [inscricoesData, etapasData, turmasData] = await Promise.all([
        listarInscricoes(),
        listarEtapas(),
        listarTurmas()
      ])

      setInscricoes(inscricoesData)
      setEtapas(etapasData)
      setTurmas(turmasData)
    } catch (error) {
      console.error('Erro ao buscar dados:', error)
      alert('Erro ao carregar dados. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  // Filtrar inscrições
  const inscricoesFiltradas = inscricoes.filter(inscricao => {
    const matchEtapa = !filtroEtapa || inscricao.etapa_id === filtroEtapa
    const matchStatus = !filtroStatus || inscricao.status_id === parseInt(filtroStatus)
    return matchEtapa && matchStatus
  })

  // Abrir modal de detalhes
  const handleAbrirDetalhes = async (inscricaoId) => {
    try {
      const inscricaoCompleta = await buscarInscricaoCompleta(inscricaoId)
      setInscricaoSelecionada(inscricaoCompleta)
      setShowModalDetalhes(true)
    } catch (error) {
      console.error('Erro ao buscar detalhes:', error)
      alert('Erro ao carregar detalhes da inscrição.')
    }
  }

  // Abrir modal de atribuir turma
  const handleAbrirModalTurma = (inscricao) => {
    setInscricaoSelecionada(inscricao)
    setTurmaParaAtribuir(inscricao.turma_id || '')
    setShowModalTurma(true)
  }

  // Atribuir turma
  const handleAtribuirTurma = async () => {
    if (!turmaParaAtribuir) {
      alert('Selecione uma turma.')
      return
    }

    console.log('🔵 Tentando atribuir turma:', {
      inscricaoId: inscricaoSelecionada.id,
      turmaId: turmaParaAtribuir
    })

    try {
      const resultado = await atribuirTurmaInscricao(inscricaoSelecionada.id, turmaParaAtribuir)
      console.log('✅ Resultado:', resultado)
      alert('Turma atribuída com sucesso!')
      setShowModalTurma(false)
      setInscricaoSelecionada(null)
      setTurmaParaAtribuir('')
      fetchData()
    } catch (error) {
      console.error('❌ Erro ao atribuir turma:', error)
      console.error('Erro completo:', JSON.stringify(error, null, 2))

      let mensagemErro = 'Erro ao atribuir turma'
      if (error && typeof error === 'object') {
        if (error.detail) {
          mensagemErro = error.detail
        } else if (error.message) {
          mensagemErro = error.message
        } else {
          mensagemErro = JSON.stringify(error)
        }
      } else if (typeof error === 'string') {
        mensagemErro = error
      }

      alert(`Erro: ${mensagemErro}`)
    }
  }

  // Remover turma
  const handleRemoverTurma = async (inscricaoId) => {
    if (!confirm('Tem certeza que deseja remover a turma desta inscrição?')) {
      return
    }

    try {
      await removerTurmaInscricao(inscricaoId)
      alert('Turma removida com sucesso!')
      fetchData()
    } catch (error) {
      console.error('Erro ao remover turma:', error)
      let mensagemErro = 'Erro ao remover turma'
      if (error && typeof error === 'object') {
        if (error.detail) {
          mensagemErro = error.detail
        } else if (error.message) {
          mensagemErro = error.message
        } else {
          mensagemErro = JSON.stringify(error)
        }
      } else if (typeof error === 'string') {
        mensagemErro = error
      }
      alert(`Erro: ${mensagemErro}`)
    }
  }

  // Abrir modal de documentos
  const handleAbrirDocumentos = async (inscricaoId) => {
    try {
      const documentosData = await listarDocumentosInscricao(inscricaoId)
      setDocumentos(documentosData)
      setInscricaoSelecionada({ id: inscricaoId })
      setShowModalDocumentos(true)
    } catch (error) {
      console.error('Erro ao buscar documentos:', error)
      alert('Erro ao carregar documentos.')
    }
  }

  // Aprovar documento
  const handleAprovarDocumento = async (documentoId) => {
    console.log('🔵 Tentando aprovar documento:', documentoId)

    try {
      const resultado = await atualizarStatusDocumento(documentoId, 'aprovado')
      console.log('✅ Resultado:', resultado)
      alert('Documento aprovado!')
      if (inscricaoSelecionada?.id) {
        handleAbrirDocumentos(inscricaoSelecionada.id)
      }
    } catch (error) {
      console.error('Erro ao aprovar documento:', error)
      console.error('Erro completo:', JSON.stringify(error, null, 2))

      let mensagemErro = 'Erro ao aprovar documento'
      if (error && typeof error === 'object') {
        if (error.detail) {
          mensagemErro = error.detail
        } else if (error.message) {
          mensagemErro = error.message
        } else {
          mensagemErro = JSON.stringify(error)
        }
      } else if (typeof error === 'string') {
        mensagemErro = error
      }

      alert(`Erro: ${mensagemErro}`)
    }
  }

  // Rejeitar documento
  const handleRejeitarDocumento = async (documentoId) => {
    const observacao = prompt('Motivo da rejeição (opcional):')

    console.log('🔵 Tentando rejeitar documento:', documentoId, 'Obs:', observacao)

    try {
      const resultado = await atualizarStatusDocumento(documentoId, 'rejeitado', observacao || null)
      console.log('✅ Resultado:', resultado)
      alert('Documento rejeitado!')
      if (inscricaoSelecionada?.id) {
        handleAbrirDocumentos(inscricaoSelecionada.id)
      }
    } catch (error) {
      console.error('Erro ao rejeitar documento:', error)
      console.error('Erro completo:', JSON.stringify(error, null, 2))

      let mensagemErro = 'Erro ao rejeitar documento'
      if (error && typeof error === 'object') {
        if (error.detail) {
          mensagemErro = error.detail
        } else if (error.message) {
          mensagemErro = error.message
        } else {
          mensagemErro = JSON.stringify(error)
        }
      } else if (typeof error === 'string') {
        mensagemErro = error
      }

      alert(`Erro: ${mensagemErro}`)
    }
  }

  const handleCloseModalDetalhes = () => {
    setShowModalDetalhes(false)
    setInscricaoSelecionada(null)
  }

  const handleCloseModalTurma = () => {
    setShowModalTurma(false)
    setInscricaoSelecionada(null)
    setTurmaParaAtribuir('')
  }

  const handleCloseModalDocumentos = () => {
    setShowModalDocumentos(false)
    setDocumentos([])
    setInscricaoSelecionada(null)
  }

  if (loading) {
    return <div className="loading-container">Carregando...</div>
  }

  return (
    <div className="gestao-container">
      <Header titulo="Catequese Divino Espírito Santo" />

      <main className="gestao-content">
        <div className="gestao-header-content">
          <h2 className="page-title">Gestão de Inscrições</h2>
        </div>

        {/* Filtros */}
        <div className="filtros-container">
          <div className="filtro-group">
            <label className="filtro-label">Etapa:</label>
            <select
              value={filtroEtapa}
              onChange={(e) => setFiltroEtapa(e.target.value)}
              className="filtro-select"
            >
              <option value="">Todas</option>
              {etapas.map(etapa => (
                <option key={etapa.id} value={etapa.id}>
                  {etapa.nome}
                </option>
              ))}
            </select>
          </div>

          <div className="filtro-group">
            <label className="filtro-label">Status:</label>
            <select
              value={filtroStatus}
              onChange={(e) => setFiltroStatus(e.target.value)}
              className="filtro-select"
            >
              <option value="">Todos</option>
              <option value="1">Pendente</option>
              <option value="2">Confirmada</option>
              <option value="3">Lista de Espera</option>
              <option value="4">Cancelada</option>
              <option value="5">Distribuída</option>
            </select>
          </div>
        </div>

        {/* Lista de Inscrições */}
        <div className="inscricoes-list">
          {inscricoesFiltradas.length === 0 ? (
            <p className="sem-inscricoes">Nenhuma inscrição encontrada</p>
          ) : (
            inscricoesFiltradas.map(inscricao => (
              <div key={inscricao.id} className="inscricao-card">
                <div className="inscricao-info">
                  <h3 className="inscricao-nome">{inscricao.catequizando_nome}</h3>
                  <p className="inscricao-responsavel">
                    Responsável: {inscricao.responsavel_nome}
                  </p>
                  <p className="inscricao-etapa">
                    Etapa: {etapas.find(e => e.id === inscricao.etapa_id)?.nome || 'N/A'}
                  </p>
                  <p className={`inscricao-status ${statusMap[inscricao.status_id]?.class || ''}`}>
                    Status: {statusMap[inscricao.status_id]?.label || 'Desconhecido'}
                  </p>
                </div>

                <div className="inscricao-actions">
                  <button
                    className="detalhes-button"
                    onClick={() => handleAbrirDetalhes(inscricao.id)}
                  >
                    Detalhes
                  </button>

                  {/* ✅ Botão aparece para TODOS os status (não só status 1) */}
                  {!inscricao.turma_id && (
                    <button
                      className="atribuir-turma-button"
                      onClick={() => handleAbrirModalTurma(inscricao)}
                    >
                      Atribuir Turma
                    </button>
                  )}

                  {inscricao.turma_id && (
                    <button
                      className="remover-turma-button"
                      onClick={() => handleRemoverTurma(inscricao.id)}
                    >
                      Remover Turma
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </main>

      {/* Modal de Detalhes */}
      {showModalDetalhes && inscricaoSelecionada && (
        <div className="modal-overlay" onClick={handleCloseModalDetalhes}>
          <div className="modal-content modal-grande" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">Detalhes da Inscrição</h3>

            <div className="detalhes-grid">
              <div className="detalhes-section">
                <h4 className="detalhes-subtitulo">Catequizando</h4>
                <p><strong>Nome:</strong> {inscricaoSelecionada.catequizando?.nome}</p>
                <p><strong>Data Nascimento:</strong> {inscricaoSelecionada.catequizando?.data_nascimento}</p>
                <p><strong>Telefone:</strong> {inscricaoSelecionada.catequizando?.telefone || 'N/A'}</p>
                <p><strong>Email:</strong> {inscricaoSelecionada.catequizando?.email || 'N/A'}</p>
              </div>

              <div className="detalhes-section">
                <h4 className="detalhes-subtitulo">Responsável</h4>
                <p><strong>Nome:</strong> {inscricaoSelecionada.responsavel?.nome}</p>
                <p><strong>Telefone:</strong> {inscricaoSelecionada.responsavel?.telefone || 'N/A'}</p>
                <p><strong>Email:</strong> {inscricaoSelecionada.responsavel?.email || 'N/A'}</p>
              </div>

              <div className="detalhes-section">
                <h4 className="detalhes-subtitulo">Inscrição</h4>
                <p><strong>Etapa:</strong> {inscricaoSelecionada.etapa?.nome}</p>
                <p><strong>Status:</strong> {statusMap[inscricaoSelecionada.status?.id]?.label || 'N/A'}</p>
                <p><strong>Data:</strong> {inscricaoSelecionada.data_inscricao ? new Date(inscricaoSelecionada.data_inscricao).toLocaleDateString('pt-BR') : 'N/A'}</p>
                <p><strong>Turma:</strong> {inscricaoSelecionada.turma?.nome_exibicao || 'Não atribuída'}</p>
                {/* ✅ Termo assinado */}
                <p><strong>Termo:</strong> {inscricaoSelecionada.termo_assinado ? '✅ Assinado' : '❌ Não assinado'}</p>
              </div>

              {/* ✅ Irmãos na Catequese */}
              {inscricaoSelecionada.referencia_irmao && (
                <div className="detalhes-section">
                  <h4 className="detalhes-subtitulo">Irmãos na Catequese</h4>
                  <p><strong>Irmão(s):</strong> {inscricaoSelecionada.referencia_irmao}</p>
                  {inscricaoSelecionada.quer_mesma_turma_que_irmao && (
                    <p><strong>Preferência:</strong> <span className="badge-info">Mesma turma</span></p>
                  )}
                </div>
              )}

              {/* ✅ Local de Preferência */}
              {inscricaoSelecionada.local_encontro_id && (
                <div className="detalhes-section">
                  <h4 className="detalhes-subtitulo">Local de Preferência</h4>
                  <p><strong>Local:</strong> {inscricaoSelecionada.local_encontro_nome}</p>
                </div>
              )}

              {/* ✅ Observações do Responsável */}
              {inscricaoSelecionada.observacao_responsavel && (
                <div className="detalhes-section full-width">
                  <h4 className="detalhes-subtitulo">Observações do Responsável</h4>
                  <p className="observacao-texto">{inscricaoSelecionada.observacao_responsavel}</p>
                </div>
              )}

              {inscricaoSelecionada.documentos && inscricaoSelecionada.documentos.length > 0 && (
                <div className="detalhes-section full-width">
                  <h4 className="detalhes-subtitulo">Documentos ({inscricaoSelecionada.documentos.length})</h4>
                  <div className="documentos-mini-list">
                    {inscricaoSelecionada.documentos.map(doc => (
                      <div key={doc.id} className="documento-mini-item">
                        <span>{doc.tipo_documento}</span>
                        <span className={`status-badge ${doc.status_validacao}`}>
                          {doc.status_validacao}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button
                className="cancelar-button"
                onClick={handleCloseModalDetalhes}
              >
                Fechar
              </button>
              {inscricaoSelecionada.documentos && inscricaoSelecionada.documentos.length > 0 && (
                <button
                  className="ver-documentos-button"
                  onClick={() => {
                    handleCloseModalDetalhes()
                    handleAbrirDocumentos(inscricaoSelecionada.id)
                  }}
                >
                  Ver Documentos
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal de Atribuir Turma */}
      {showModalTurma && inscricaoSelecionada && (
        <div className="modal-overlay" onClick={handleCloseModalTurma}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">Atribuir Turma</h3>

            <div className="form-group">
              <label className="form-label">Selecione a turma:</label>
              <select
                value={turmaParaAtribuir}
                onChange={(e) => setTurmaParaAtribuir(e.target.value)}
                className="form-input"
              >
                <option value="">Selecione uma turma...</option>
                {turmas
                  .filter(t => t.etapa_id === inscricaoSelecionada.etapa_id && t.ativa)
                  .map(turma => (
                    <option key={turma.id} value={turma.id}>
                      {turma.nome_exibicao || turma.nome_sistema} ({turma.vagas_totais} vagas)
                    </option>
                  ))
                }
              </select>
            </div>

            <div className="modal-actions">
              <button
                className="cancelar-button"
                onClick={handleCloseModalTurma}
              >
                Cancelar
              </button>
              <button
                className="salvar-button"
                onClick={handleAtribuirTurma}
                disabled={!turmaParaAtribuir}
              >
                ATRIBUIR
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Documentos */}
      {showModalDocumentos && (
        <div className="modal-overlay" onClick={handleCloseModalDocumentos}>
          <div className="modal-content modal-grande" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">Documentos da Inscrição</h3>

            <div className="documentos-list">
              {documentos.length === 0 ? (
                <p className="sem-documentos">Nenhum documento enviado</p>
              ) : (
                documentos.map(doc => {

                  console.log('📄 Documento:', doc)
                  console.log('Status:', doc.status_validacao)
                  console.log('Observação:', doc.observacao_validacao)
                  console.log('Tipo observação:', typeof doc.observacao_validacao)

                  // ✅ Normaliza o status para comparação
                  const statusNormalizado = (doc.status_validacao || '').toLowerCase().trim()
                  // ✅ Só mostra botões se estiver pendente
                  const mostrarBotoes = statusNormalizado === 'pendente'

                  return (
                    <div key={doc.id} className="documento-item">
                      <div className="documento-info">
                        <p className="documento-tipo">{doc.tipo_documento}</p>
                        <p className="documento-nome">{doc.file_name || doc.nome_original || 'Sem nome'}</p>
                        <p className="documento-data">
                          Enviado em: {doc.uploaded_at || doc.created_at ? new Date(doc.uploaded_at || doc.created_at).toLocaleDateString('pt-BR') : 'N/A'}
                        </p>
                        {/* ✅ Motivo da rejeição (só aparece se rejeitado) */}
                        {doc.status_validacao === 'rejeitado' && doc.observacao_validacao && (
                          <p className="documento-observacao-rejeicao">
                            <strong>Motivo da rejeição:</strong> {doc.observacao_validacao}
                          </p>
                        )}
                      </div>
                      <div className="documento-status">
                        <span className={`status-badge ${doc.status_validacao}`}>
                          {doc.status_validacao}
                        </span>
                      </div>
                      <div className="documento-actions">
                        {/* ✅ Botões só aparecem se estiver pendente */}
                        {mostrarBotoes && (
                          <>
                            <button
                              className="aprovar-button"
                              onClick={() => handleAprovarDocumento(doc.id)}
                            >
                              Aprovar
                            </button>
                            <button
                              className="rejeitar-button"
                              onClick={() => handleRejeitarDocumento(doc.id)}
                            >
                              Rejeitar
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  )
                })
              )}
            </div>

            <div className="modal-actions">
              <button
                className="cancelar-button"
                onClick={handleCloseModalDocumentos}
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default GestaoInscricoesPage