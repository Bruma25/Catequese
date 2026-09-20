// src/pages/MeusCatequizandosPage.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../services/supabaseClient'
import {
  buscarInscricaoCompleta,
  listarDocumentosInscricao,
  uploadDocumento,
  atualizarStatusDocumento,
  buscarResponsavelPorUsuario
} from '../services/api'
import Header from '../components/Header/Header'
import { FileText, Upload, CheckCircle, XCircle, Clock, Edit, Eye } from 'lucide-react'
import './MeusCatequizandosPage.css'

function MeusCatequizandosPage() {
  const navigate = useNavigate()
  const [catequizandos, setCatequizandos] = useState([])
  const [loading, setLoading] = useState(true)
  const [usuarioLogado, setUsuarioLogado] = useState(null)

  // Modal de detalhes
  const [showModalDetalhes, setShowModalDetalhes] = useState(false)
  const [inscricaoSelecionada, setInscricaoSelecionada] = useState(null)

  // Modal de documentos
  const [showModalDoc, setShowModalDoc] = useState(false)
  const [documentos, setDocumentos] = useState([])
  const [fileUpload, setFileUpload] = useState(null)
  const [tipoDocumento, setTipoDocumento] = useState('')

  useEffect(() => {
    carregarDados()
  }, [])

  async function carregarDados() {
    try {
      // 1. Buscar usuário logado
      console.log('🔍 [1] Buscando usuário logado...')
      const { data: { user }, error: erroUser } = await supabase.auth.getUser()

      console.log('👤 Usuário logado:', user?.id)
      console.log('❌ Erro user:', erroUser)

      if (!user) {
        console.log('⚠️ Usuário não logado, redirecionando para /login')
        navigate('/login')
        return
      }

      setUsuarioLogado(user)
      console.log('✅ Usuário definido:', usuarioLogado?.id)

      // 2. Buscar responsáveis do usuário
      console.log('🔍 [2] Buscando responsáveis para usuario_id:', user.id)
      const { data: responsaveis, error: erroResponsaveis } = await supabase
        .from('responsavel')
        .select('*')
        .eq('usuario_id', user.id)

      console.log('📋 Responsáveis encontrados:', responsaveis)
      console.log('❌ Erro responsáveis:', erroResponsaveis)

      if (!responsaveis || responsaveis.length === 0) {
        console.log('⚠️ Nenhum responsável encontrado para este usuário!')
        alert('Nenhuma inscrição encontrada. Faça sua primeira inscrição!')
        navigate('/home')
        return
      }

      // Suportar múltiplos responsáveis
      const responsavelIds = responsaveis.map(r => r.id)
      console.log('🆔 IDs dos responsáveis:', responsavelIds)

      // 3. Buscar vínculos de todos os responsáveis
      console.log('🔍 [3] Buscando vínculos catequizando_responsavel para responsavel_ids:', responsavelIds)
      const { data: vinculos, error: erroVinculos } = await supabase
        .from('catequizando_responsavel')
        .select('catequizando_id')
        .in('responsavel_id', responsavelIds)

      console.log('🔗 Vínculos encontrados:', vinculos)
      console.log('❌ Erro vínculos:', erroVinculos)

      if (!vinculos || vinculos.length === 0) {
        console.log('⚠️ Nenhum vínculo catequizando_responsavel encontrado!')
        setCatequizandos([])
        setLoading(false)
        return
      }

      const catequizandoIds = vinculos.map(v => v.catequizando_id)
      console.log('👶 IDs dos catequizandos:', catequizandoIds)

      // 4. Buscar inscrições dos catequizandos
      const { data: inscricoes, error: erroInscricoes } = await supabase
        .from('inscricao')
        .select(`
          id,
          catequizando_id,
          etapa_id,
          turma_id,
          status_id,
          data_inscricao,
          termo_assinado,
          referencia_irmao,
          quer_mesma_turma_que_irmao,
          observacao_responsavel,
          local_encontro_id,
          catequizando:catequizando_id (
            id,
            nome,
            data_nascimento,
            necessidade_especial,
            descricao_necessidade_especial
          ),
          etapa:etapa_id (
            id,
            nome
          ),
          turma:turma_id (
            id,
            nome_exibicao,
            nome_sistema
          ),
          status:status_id (
            id,
            codigo,
            descricao
          ),
          local:local_encontro_id (
            id,
            nome_exibicao
          )
        `)
        .in('catequizando_id', catequizandoIds)
        .order('data_inscricao', { ascending: false })

      console.log('📝 Inscrições encontradas:', inscricoes)
      console.log('❌ Erro inscrições:', erroInscricoes)

      setCatequizandos(inscricoes || [])
      console.log('✅ Catequizandos definidos:', catequizandos)
    } catch (error) {
      console.error('💥 Erro ao carregar dados:', error)
      alert('Erro ao carregar dados.')
    } finally {
      setLoading(false)
      console.log('⏹️ Loading definido como false')
    }
  }

  // Abrir modal de detalhes
  const handleAbrirDetalhes = async (inscricaoId) => {
    console.log('🔍 Abrindo detalhes da inscrição:', inscricaoId)
    try {
      const inscricaoCompleta = await buscarInscricaoCompleta(inscricaoId)
      console.log('✅ Inscrição completa:', inscricaoCompleta)
      setInscricaoSelecionada(inscricaoCompleta)
      setShowModalDetalhes(true)
    } catch (error) {
      console.error('❌ Erro ao buscar detalhes:', error)
      alert('Erro ao carregar detalhes da inscrição.')
    }
  }

  const handleCloseModalDetalhes = () => {
    console.log('🚫 Fechando modal de detalhes')
    setShowModalDetalhes(false)
    setInscricaoSelecionada(null)
  }

  const handleOpenModalDoc = async (inscricao) => {
    console.log('📂 Abrindo modal de documentos para inscrição:', inscricao.id)
    setInscricaoSelecionada(inscricao)

    // Buscar documentos da inscrição
    try {
      console.log('🔍 Buscando documentos para inscrição:', inscricao.id)
      const docs = await listarDocumentosInscricao(inscricao.id)
      console.log('📄 Documentos encontrados:', docs)
      setDocumentos(docs)
    } catch (error) {
      console.error('❌ Erro ao buscar documentos:', error)
      setDocumentos([])
    }

    setShowModalDoc(true)
    console.log('✅ Modal de documentos aberto')
  }

  const handleCloseModalDoc = () => {
    console.log('🚫 Fechando modal de documentos')
    setShowModalDoc(false)
    setInscricaoSelecionada(null)
    setDocumentos([])
    setFileUpload(null)
    setTipoDocumento('')
  }

  const handleUpload = async () => {
    if (!fileUpload || !tipoDocumento) {
      console.log('⚠️ Upload tentado sem arquivo ou tipo')
      alert('Selecione o tipo de documento e o arquivo')
      return
    }

    console.log('📤 Enviando documento:', {
      inscricaoId: inscricaoSelecionada.id,
      tipo: tipoDocumento,
      arquivo: fileUpload.name
    })

    try {
      await uploadDocumento(inscricaoSelecionada.id, fileUpload, tipoDocumento)
      alert('Documento enviado com sucesso!')

      // Recarregar documentos
      console.log('🔍 Recarregando documentos após upload...')
      const docs = await listarDocumentosInscricao(inscricaoSelecionada.id)
      console.log('📄 Documentos após upload:', docs)
      setDocumentos(docs)

      setFileUpload(null)
      setTipoDocumento('')
    } catch (error) {
      console.error('❌ Erro ao fazer upload:', error)
      alert(`Erro: ${error.message}`)
    }
  }

  const getStatusIcon = (statusCodigo) => {
    switch (statusCodigo) {
      case 'confirmada':
        return <CheckCircle size={20} className="status-icon confirmada" />
      case 'lista_espera':
        return <Clock size={20} className="status-icon lista_espera" />
      case 'pendente_distribuicao':
        return <Clock size={20} className="status-icon pendente" />
      case 'cancelada':
        return <XCircle size={20} className="status-icon cancelada" />
      default:
        return <FileText size={20} />
    }
  }

  const getStatusClass = (statusCodigo) => {
    return `status-badge ${statusCodigo}`
  }

  if (loading) {
    console.log('⏳ Loading = true, exibindo "Carregando..."')
    return <div className="loading-container">Carregando...</div>
  }

  console.log('✅ Renderizando página com catequizandos:', catequizandos)

  return (
    <div className="meus-catequizandos-container">
      <Header titulo="Catequese Divino Espírito Santo" />

      <main className="meus-catequizandos-content">
        <h2 className="page-title">Meus Catequizandos</h2>

        {catequizandos.length === 0 ? (
          <div className="sem-catequizandos">
            <FileText size={48} />
            <p>Você não tem catequizandos cadastrados</p>
            <button
              className="nova-inscricao-button"
              onClick={() => navigate('/inscricao')}
            >
              Fazer Nova Inscrição
            </button>
          </div>
        ) : (
          <div className="catequizandos-list">
            {catequizandos.map(inscricao => {
              console.log('🔍 Renderizando inscrição:', inscricao)

              // Verificar se os dados existem
              if (!inscricao.catequizando) {
                console.error('❌ inscricao.catequizando é undefined!', inscricao)
                return null
              }
              if (!inscricao.status) {
                console.error('❌ inscricao.status é undefined!', inscricao)
                return null
              }

              return (
                <div key={inscricao.id} className="catequizando-card">
                  <div className="catequizando-header">
                    <div className="catequizando-info">
                      <h3 className="catequizando-nome">{inscricao.catequizando.nome}</h3>
                      <p className="catequizando-nascimento">
                        Nascimento: {new Date(inscricao.catequizando.data_nascimento).toLocaleDateString('pt-BR')}
                      </p>
                      {inscricao.catequizando.necessidade_especial && (
                        <p className="catequizando-necessidade">
                          Necessidade especial: {inscricao.catequizando.descricao_necessidade_especial}
                        </p>
                      )}
                    </div>
                    <div className="status-container">
                      {getStatusIcon(inscricao.status.codigo)}
                      <span className={getStatusClass(inscricao.status.codigo)}>
                        {inscricao.status.descricao}
                      </span>
                    </div>
                  </div>

                  <div className="catequizando-detalhes">
                    <div className="detalhe-item">
                      <strong>Etapa:</strong> {inscricao.etapa?.nome || 'Não definida'}
                    </div>
                    {inscricao.turma && (
                      <div className="detalhe-item">
                        <strong>Turma:</strong> {inscricao.turma.nome_exibicao || inscricao.turma.nome_sistema}
                      </div>
                    )}
                    <div className="detalhe-item">
                      <strong>Data da Inscrição:</strong> {new Date(inscricao.data_inscricao).toLocaleDateString('pt-BR')}
                    </div>
                    <div className="detalhe-item">
                      <strong>Termo Assinado:</strong> {inscricao.termo_assinado ? 'Sim' : 'Não'}
                    </div>
                  </div>

                  <div className="catequizando-actions">
                    <button
                      className="btn-documentos"
                      onClick={() => handleOpenModalDoc(inscricao)}
                    >
                      <FileText size={16} />
                      Ver Documentos
                    </button>
                    <button
                      className="btn-ver"
                      onClick={() => handleAbrirDetalhes(inscricao.id)}
                    >
                      <Eye size={16} />
                      Ver Detalhes
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
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
                <p><strong>Data Nascimento:</strong> {inscricaoSelecionada.catequizando?.data_nascimento ? new Date(inscricaoSelecionada.catequizando.data_nascimento).toLocaleDateString('pt-BR') : 'N/A'}</p>
                {inscricaoSelecionada.catequizando?.necessidade_especial && (
                  <>
                    <p><strong>Necessidade Especial:</strong> Sim</p>
                    <p><strong>Descrição:</strong> {inscricaoSelecionada.catequizando.descricao_necessidade_especial}</p>
                  </>
                )}
              </div>

              <div className="detalhes-section">
                <h4 className="detalhes-subtitulo">Inscrição</h4>
                <p><strong>Etapa:</strong> {inscricaoSelecionada.etapa?.nome || 'N/A'}</p>
                <p><strong>Status:</strong> {inscricaoSelecionada.status?.descricao || 'N/A'}</p>
                <p><strong>Data:</strong> {inscricaoSelecionada.data_inscricao ? new Date(inscricaoSelecionada.data_inscricao).toLocaleDateString('pt-BR') : 'N/A'}</p>
                <p><strong>Turma:</strong> {inscricaoSelecionada.turma?.nome_exibicao || inscricaoSelecionada.turma?.nome_sistema || 'Não atribuída'}</p>
                <p><strong>Termo:</strong> {inscricaoSelecionada.termo_assinado ? '✅ Assinado' : '❌ Não assinado'}</p>
              </div>

              {/* Irmãos na Catequese */}
              {inscricaoSelecionada.referencia_irmao && (
                <div className="detalhes-section">
                  <h4 className="detalhes-subtitulo">Irmãos na Catequese</h4>
                  <p><strong>Irmão(s):</strong> {inscricaoSelecionada.referencia_irmao}</p>
                  {inscricaoSelecionada.quer_mesma_turma_que_irmao && (
                    <p><strong>Preferência:</strong> <span className="badge-info">Mesma turma</span></p>
                  )}
                </div>
              )}

              {/* Local de Preferência */}
              {inscricaoSelecionada.local_encontro_id && (
                <div className="detalhes-section">
                  <h4 className="detalhes-subtitulo">Local de Preferência</h4>
                  <p><strong>Local:</strong> {inscricaoSelecionada.local?.nome_exibicao || `ID: ${inscricaoSelecionada.local_encontro_id}`}</p>
                </div>
              )}

              {/* Observações do Responsável */}
              {inscricaoSelecionada.observacao_responsavel && (
                <div className="detalhes-section full-width">
                  <h4 className="detalhes-subtitulo">Observações do Responsável</h4>
                  <p className="observacao-texto">{inscricaoSelecionada.observacao_responsavel}</p>
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
            </div>
          </div>
        </div>
      )}

      {/* Modal de Documentos */}
      {showModalDoc && inscricaoSelecionada && (
        <div className="modal-overlay" onClick={handleCloseModalDoc}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">
              Documentos - {inscricaoSelecionada.catequizando?.nome || 'Carregando...'}
            </h3>

            {/* Upload */}
            <div className="upload-section">
              <h4 className="upload-title">Enviar Novo Documento</h4>

              <div className="upload-form">
                {/* LISTA CORRIGIDA DE DOCUMENTOS */}
                <select
                  value={tipoDocumento}
                  onChange={(e) => setTipoDocumento(e.target.value)}
                  className="form-select"
                >
                  <option value="">Selecione o tipo...</option>
                  <option value="identidade">Identidade ou Certidão de Nascimento</option>
                  <option value="comprovante_batismo">Certidão/Lembrança de Batismo</option>
                  <option value="comprovante_eucaristia">Lembrança de Primeira Eucaristia</option>
                  <option value="comprovante_crisma">Lembrança de Crisma</option>
                  <option value="comprovante_outro_sacramento">Comprovante de Outro Sacramento</option>
                  <option value="comprovante_residencia">Comprovante de Residência</option>
                  <option value="outro">Outro Documento</option>
                </select>

                <input
                  type="file"
                  onChange={(e) => setFileUpload(e.target.files[0])}
                  className="file-input"
                  accept=".pdf,.jpg,.jpeg,.png"
                />

                <button
                  className="btn-upload"
                  onClick={handleUpload}
                  disabled={!fileUpload || !tipoDocumento}
                >
                  <Upload size={16} />
                  Enviar
                </button>
              </div>
            </div>

            {/* Lista de Documentos */}
            <div className="documentos-section">
              <h4 className="documentos-title">Documentos Enviados</h4>

              {documentos.length === 0 ? (
                <p className="sem-documentos">Nenhum documento enviado</p>
              ) : (
                <div className="documentos-list">
                  {documentos.map(doc => {
                    const statusNormalizado = (doc.status_validacao || '').toLowerCase().trim()
                    const mostrarBotoes = statusNormalizado === 'pendente'

                    return (
                      <div key={doc.id} className="documento-item">
                        <div className="documento-info">
                          <FileText size={20} />
                          <div>
                            <p className="documento-nome">{doc.nome_original}</p>
                            <p className="documento-tipo">
                              Tipo: {doc.tipo_documento}
                            </p>
                            <p className="documento-data">
                              Enviado em: {new Date(doc.uploaded_at).toLocaleDateString('pt-BR')}
                            </p>
                            {doc.status_validacao === 'rejeitado' && doc.observacao_validacao && (
                              <p className="documento-observacao-rejeicao">
                                <strong>Motivo da rejeição:</strong> {doc.observacao_validacao}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="documento-status">
                          {doc.status_validacao === 'aprovado' && (
                            <span className="status-aprovado">
                              <CheckCircle size={16} /> Aprovado
                            </span>
                          )}
                          {doc.status_validacao === 'rejeitado' && (
                            <span className="status-rejeitado">
                              <XCircle size={16} /> Rejeitado
                            </span>
                          )}
                          {!doc.status_validacao || doc.status_validacao === 'pendente' && (
                            <span className="status-pendente">
                              <Clock size={16} /> Pendente
                            </span>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>

            <button
              className="btn-fechar"
              onClick={handleCloseModalDoc}
            >
              Fechar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default MeusCatequizandosPage