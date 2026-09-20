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

  // Modal de documentos
  const [showModalDoc, setShowModalDoc] = useState(false)
  const [inscricaoSelecionada, setInscricaoSelecionada] = useState(null)
  const [documentos, setDocumentos] = useState([])
  const [fileUpload, setFileUpload] = useState(null)
  const [tipoDocumento, setTipoDocumento] = useState('')

  useEffect(() => {
    carregarDados()
  }, [])

  async function carregarDados() {
    try {
      // 1. Buscar usuário logado
      const { data: { user }, error: erroUser } = await supabase.auth.getUser()

      console.log('👤 Usuário logado:', user?.id)
      console.log('❌ Erro user:', erroUser)

      if (!user) {
        console.log('⚠️ Usuário não logado, redirecionando...')
        navigate('/login')
        return
      }

      setUsuarioLogado(user)

      // 2. Buscar responsáveis do usuário
      const { data: responsaveis, error: erroResponsaveis } = await supabase
        .from('responsavel')
        .select('id, nome, usuario_id')
        .eq('usuario_id', user.id)

      console.log('📋 Responsáveis encontrados:', responsaveis)
      console.log('❌ Erro responsáveis:', erroResponsaveis)

      if (!responsaveis || responsaveis.length === 0) {
        console.log('⚠️ Nenhum responsável encontrado para este usuário!')
        alert('Nenhuma inscrição encontrada. Faça sua primeira inscrição!')
        navigate('/home')
        return
      }

      const responsavelIds = responsaveis.map(r => r.id)
      console.log('🆔 IDs dos responsáveis:', responsavelIds)

      // 3. Buscar vínculos catequizando_responsavel
      const { data: vinculos, error: erroVinculos } = await supabase
        .from('catequizando_responsavel')
        .select('catequizando_id, responsavel_id, tipo_vinculo_id, descricao_outro')
        .in('responsavel_id', responsavelIds)

      console.log('🔗 Vínculos catequizando_responsavel encontrados:', vinculos)
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
          )
        `)
        .in('catequizando_id', catequizandoIds)
        .order('data_inscricao', { ascending: false })

      console.log('📝 Inscrições encontradas:', inscricoes)
      console.log('❌ Erro inscrições:', erroInscricoes)

      setCatequizandos(inscricoes || [])
    } catch (error) {
      console.error('💥 Erro ao carregar dados:', error)
      alert('Erro ao carregar dados.')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenModalDoc = async (inscricao) => {
    console.log('📂 Abrindo modal de documentos para inscrição:', inscricao.id)
    setInscricaoSelecionada(inscricao)

    // Buscar documentos da inscrição
    try {
      const docs = await listarDocumentosInscricao(inscricao.id)
      console.log('📄 Documentos encontrados:', docs)
      setDocumentos(docs)
    } catch (error) {
      console.error('❌ Erro ao buscar documentos:', error)
      setDocumentos([])
    }

    setShowModalDoc(true)
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
    console.log('⏳ Carregando dados...')
    return <div className="loading-container">Carregando...</div>
  }

  console.log('✅ Dados carregados com sucesso:', catequizandos)

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
            {catequizandos.map(inscricao => (
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
                    <strong>Etapa:</strong> {inscricao.etapa.nome}
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
                    className="btn-editar"
                    onClick={() => navigate(`/inscricao/${inscricao.id}/editar`)}
                  >
                    <Edit size={16} />
                    Editar Dados
                  </button>
                  <button
                    className="btn-ver"
                    onClick={() => navigate(`/inscricao/${inscricao.id}`)}
                  >
                    <Eye size={16} />
                    Ver Detalhes
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Modal de Documentos */}
      {showModalDoc && inscricaoSelecionada && (
        <div className="modal-overlay" onClick={handleCloseModalDoc}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">
              Documentos - {inscricaoSelecionada.catequizando.nome}
            </h3>

            {/* Upload */}
            <div className="upload-section">
              <h4 className="upload-title">Enviar Novo Documento</h4>

              <div className="upload-form">
                <select
                  value={tipoDocumento}
                  onChange={(e) => setTipoDocumento(e.target.value)}
                  className="form-select"
                >
                  <option value="">Selecione o tipo...</option>
                  <option value="certidao_nascimento">Certidão de Nascimento</option>
                  <option value="rg">RG</option>
                  <option value="cpf">CPF</option>
                  <option value="comprovante_residencia">Comprovante de Residência</option>
                  <option value="foto">Foto 3x4</option>
                  <option value="outro">Outro</option>
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
                  {documentos.map(doc => (
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
                        {doc.observacao_validacao && (
                          <p className="documento-observacao">{doc.observacao_validacao}</p>
                        )}
                      </div>
                    </div>
                  ))}
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