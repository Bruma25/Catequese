import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Header from '../components/Header/Header'
import { criarInscricao, uploadDocumento } from '../services/api'
import './FichaInscricaoPage.css'

function FichaInscricaoPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [etapaSelecionada, setEtapaSelecionada] = useState(null)
  const [sacramentosCatequizando, setSacramentosCatequizando] = useState([])
  const [locaisEncontro, setLocaisEncontro] = useState([])
  const [inscricaoId, setInscricaoId] = useState(null)

  // Dados do catequizando
  const [formData, setFormData] = useState({
    nomeCompleto: '',
    dataNascimento: '',
    idade: '',
    endereco: '',
    telefone1: '',
    telefone2: '',
    email: '',
    batizado: '',
    dataBatismo: '',
    localBatismo: '',
    eucaristia: '',
    dataEucaristia: '',
    localEucaristia: '',
    crisma: '',
    dataCrisma: '',
    localCrisma: '',
    responsavelProprio: '',
    tipoResponsavel: '',
    nomePai: '',
    telefonePai: '',
    emailPai: '',
    nomeMae: '',
    telefoneMae: '',
    emailMae: '',
    outroResponsavel: '',
    telefoneOutro: '',
    emailOutro: '',
    necessidadeEspecial: '',
    descricaoNecessidade: '',
    termoCompromisso: false,
    autorizacaoCompromisso: false,
    local_encontro_id: '',
    temIrmao: 'nao',
    referenciaIrmao: '',
    querMesmaTurmaQueIrmao: 'nao'
  })

  // Documentos
  const [documentos, setDocumentos] = useState({
    identidade: null,
    batismo: null,
    eucaristia: null,
    crisma: null,
    identidade_responsavel: null,
    comprovante_residencia: null
  })

  // Carregar dados da página anterior e sacramentos
  useEffect(() => {
    window.scrollTo(0, 0)

    async function loadData() {
      const inscricaoData = localStorage.getItem('inscricao_data')
      if (inscricaoData) {
        const { dataNascimento, sacramentos, etapaSelecionada } = JSON.parse(inscricaoData)
        setEtapaSelecionada(etapaSelecionada)
        setSacramentosCatequizando(sacramentos || [])

        if (dataNascimento) {
          const hoje = new Date()
          const nasc = new Date(dataNascimento)
          const idade = hoje.getFullYear() - nasc.getFullYear()
          const maiorDeIdade = idade >= 18

          setFormData(prev => ({
            ...prev,
            dataNascimento: dataNascimento,
            idade: idade.toString(),
            batizado: sacramentos?.includes(1) ? 'sim' : 'nao',
            eucaristia: sacramentos?.includes(2) ? 'sim' : 'nao',
            crisma: sacramentos?.includes(3) ? 'sim' : 'nao',
            responsavelProprio: maiorDeIdade ? 'sim' : 'nao'  // ✅ Auto-preencher
          }))
        }
      } else {
        alert('Nenhuma etapa selecionada. Redirecionando...')
        navigate('/etapas')
      }

      // Buscar locais de encontro
      try {
        const locaisData = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/locais-encontro`)
          .then(res => res.json())
        setLocaisEncontro(locaisData)
      } catch (error) {
        console.error('Erro ao buscar locais de encontro:', error)
      }
    }

    loadData()
  }, [navigate])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    console.log('📝 Mudança:', { name, value, type, checked })
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleDocumentoChange = (tipo, file) => {
    setDocumentos(prev => ({
      ...prev,
      [tipo]: file
    }))
  }

  // Obter nome do responsável selecionado
  const getNomeResponsavel = () => {
    if (formData.responsavelProprio === 'sim') {
      return formData.nomeCompleto
    }

    switch (formData.tipoResponsavel) {
      case 'pai':
        return formData.nomePai
      case 'mae':
        return formData.nomeMae
      case 'outro':
        return formData.outroResponsavel
      default:
        return '_______________'
    }
  }

  // Upload de documentos
  const uploadDocumentos = async (inscricaoId) => {
    const documentosParaEnviar = []

    if (documentos.identidade) {
      documentosParaEnviar.push({
        file: documentos.identidade,
        tipo: 'identidade'
      })
    }

    if (documentos.batismo && formData.batizado === 'sim') {
      documentosParaEnviar.push({
        file: documentos.batismo,
        tipo: 'comprovante_batismo'
      })
    }

    if (documentos.eucaristia && formData.eucaristia === 'sim') {
      documentosParaEnviar.push({
        file: documentos.eucaristia,
        tipo: 'comprovante_eucaristia'
      })
    }

    if (documentos.crisma && formData.crisma === 'sim') {
      documentosParaEnviar.push({
        file: documentos.crisma,
        tipo: 'comprovante_crisma'
      })
    }

    if (documentos.identidade_responsavel && formData.responsavelProprio === 'nao') {
      documentosParaEnviar.push({
        file: documentos.identidade_responsavel,
        tipo: 'identidade'
      })
    }

    if (documentos.comprovante_residencia) {
      documentosParaEnviar.push({
        file: documentos.comprovante_residencia,
        tipo: 'comprovante_residencia'
      })
    }

    console.log('📎 Documentos para enviar:', documentosParaEnviar)

    // Envia cada documento
    for (const doc of documentosParaEnviar) {
      try {
        console.log(`📤 Enviando documento ${doc.tipo}...`)
        await uploadDocumento(inscricaoId, doc.file, doc.tipo)
        console.log(`✅ Documento ${doc.tipo} enviado com sucesso!`)
      } catch (error) {
        console.error(`❌ Erro ao enviar documento ${doc.tipo}:`, error)
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.termoCompromisso || formData.autorizacaoCompromisso !== 'concordo') {
      alert('Por favor, aceite o termo de compromisso e a autorização')
      return
    }

    setLoading(true)

    try {
      const mapeamentoVinculo = {
        'pai': 1,
        'mae': 2,
        'outro': 3
      }

      const dadosInscricao = {
        catequizando_nome: formData.nomeCompleto,
        catequizando_data_nascimento: formData.dataNascimento,
        catequizando_sacramentos: sacramentosCatequizando || [],
        etapa_id: etapaSelecionada.id,
        responsavel_nome: getNomeResponsavel(),
        responsavel_email: formData.emailMae || formData.emailPai || formData.emailOutro || formData.email || null,
        responsavel_telefone: formData.telefoneMae || formData.telefonePai || formData.telefoneOutro || formData.telefone1 || null,
        responsavel_vinculo: mapeamentoVinculo[formData.tipoResponsavel] || 3,
        local_encontro_id: formData.local_encontro_id ? parseInt(formData.local_encontro_id) : null,
        referencia_irmao: formData.temIrmao === 'sim' ? formData.referenciaIrmao : null,
        quer_mesma_turma_que_irmao: formData.temIrmao === 'sim' && formData.querMesmaTurmaQueIrmao === 'sim'
      }

      console.log('📤 Enviando inscrição:', dadosInscricao)

      const inscricaoCriada = await criarInscricao(dadosInscricao)

      console.log('✅ Inscrição criada:', inscricaoCriada)

      setInscricaoId(inscricaoCriada.id)

      // Upload de documentos (opcional)
      if (inscricaoCriada.id && Object.values(documentos).some(d => d !== null)) {
        console.log('📎 Enviando documentos...')
        await uploadDocumentos(inscricaoCriada.id)
      }

      // Verificar status
      if (inscricaoCriada.status_id === 2 || inscricaoCriada.status_id === 3) {
        alert('Inscrição confirmada com vaga!')
      } else if (inscricaoCriada.status_id === 5) {
        alert('Inscrição em lista de espera devido à falta de vagas.')
      } else {
        alert('Inscrição realizada com sucesso!')
      }

      // Limpar localStorage
      localStorage.removeItem('inscricao_data')

      navigate('/home')

    } catch (error) {
      console.error('Erro ao criar inscrição:', error)

      const mensagemErro = error.message || 'Erro ao realizar inscrição'
      alert(`Erro: ${mensagemErro}`)
    } finally {
      setLoading(false)
    }
  }

  if (!etapaSelecionada) {
    return <div className="loading-container">Carregando...</div>
  }

  const maiorDeIdade = parseInt(formData.idade) >= 18

  return (
    <div className="ficha-container">
      <Header titulo="Catequese Divino Espírito Santo" />

      <main className="ficha-content">
        <form onSubmit={handleSubmit}>
          {/* Dados do Catequizando */}
          <section className="ficha-section">
            <h2 className="section-title">Dados do Catequizando</h2>

            <div className="form-group">
              <label className="form-label">Nome Completo: *</label>
              <input
                type="text"
                name="nomeCompleto"
                value={formData.nomeCompleto}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Data de Nascimento: *</label>
                <input
                  type="date"
                  name="dataNascimento"
                  value={formData.dataNascimento}
                  onChange={handleChange}
                  className="form-input"
                  required
                  disabled
                />
              </div>

              <div className="form-group">
                <label className="form-label">Idade: *</label>
                <input
                  type="text"
                  name="idade"
                  value={formData.idade}
                  onChange={handleChange}
                  className="form-input"
                  required
                  disabled
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Endereço: *</label>
              <textarea
                name="endereco"
                value={formData.endereco}
                onChange={handleChange}
                className="form-textarea"
                rows="3"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Telefone(s): *</label>
              <input
                type="tel"
                name="telefone1"
                value={formData.telefone1}
                onChange={handleChange}
                className="form-input"
                placeholder="(00) 00000-0000"
                required
              />
              <input
                type="tel"
                name="telefone2"
                value={formData.telefone2}
                onChange={handleChange}
                className="form-input"
                placeholder="(00) 00000-0000 (opcional)"
                style={{ marginTop: '10px' }}
              />
            </div>

            <div className="form-group">
              <label className="form-label">E-mail:</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Batizado(a)? *</label>
              <div className="radio-group">
                <label className="radio-label">
                  <input
                    type="radio"
                    name="batizado"
                    value="sim"
                    checked={formData.batizado === 'sim'}
                    onChange={handleChange}
                    required
                  />
                  <span>Sim</span>
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    name="batizado"
                    value="nao"
                    checked={formData.batizado === 'nao'}
                    onChange={handleChange}
                    required
                  />
                  <span>Não</span>
                </label>
              </div>
              <p className="form-hint">
                * Caso não tenha, precisa fazer a preparação para o Batismo.
              </p>
            </div>

            {formData.batizado === 'sim' && (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Data do Batismo:</label>
                    <input
                      type="date"
                      name="dataBatismo"
                      value={formData.dataBatismo}
                      onChange={handleChange}
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Local do Batismo:</label>
                    <input
                      type="text"
                      name="localBatismo"
                      value={formData.localBatismo}
                      onChange={handleChange}
                      className="form-input"
                      placeholder="Paróquia – Diocese/Arquidiocese"
                    />
                    <p className="form-hint">
                      Normalmente o nome da diocese está no carimbo que consta na lembrança de batismo.
                    </p>
                  </div>
                </div>
              </>
            )}

            {/* Primeira Eucaristia */}
            <div className="form-group">
              <label className="form-label">Já recebeu a Primeira Eucaristia? *</label>
              <div className="radio-group">
                <label className="radio-label">
                  <input
                    type="radio"
                    name="eucaristia"
                    value="sim"
                    checked={formData.eucaristia === 'sim'}
                    onChange={handleChange}
                    required
                  />
                  <span>Sim</span>
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    name="eucaristia"
                    value="nao"
                    checked={formData.eucaristia === 'nao'}
                    onChange={handleChange}
                    required
                  />
                  <span>Não</span>
                </label>
              </div>
            </div>

            {formData.eucaristia === 'sim' && (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Data da Primeira Eucaristia:</label>
                    <input
                      type="date"
                      name="dataEucaristia"
                      value={formData.dataEucaristia}
                      onChange={handleChange}
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Local da Primeira Eucaristia:</label>
                    <input
                      type="text"
                      name="localEucaristia"
                      value={formData.localEucaristia}
                      onChange={handleChange}
                      className="form-input"
                      placeholder="Paróquia – Diocese/Arquidiocese"
                    />
                  </div>
                </div>
              </>
            )}

            {/* Crisma */}
            <div className="form-group">
              <label className="form-label">Já recebeu o Sacramento da Crisma? *</label>
              <div className="radio-group">
                <label className="radio-label">
                  <input
                    type="radio"
                    name="crisma"
                    value="sim"
                    checked={formData.crisma === 'sim'}
                    onChange={handleChange}
                    required
                  />
                  <span>Sim</span>
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    name="crisma"
                    value="nao"
                    checked={formData.crisma === 'nao'}
                    onChange={handleChange}
                    required
                  />
                  <span>Não</span>
                </label>
              </div>
            </div>

            {formData.crisma === 'sim' && (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Data da Crisma:</label>
                    <input
                      type="date"
                      name="dataCrisma"
                      value={formData.dataCrisma}
                      onChange={handleChange}
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Local da Crisma:</label>
                    <input
                      type="text"
                      name="localCrisma"
                      value={formData.localCrisma}
                      onChange={handleChange}
                      className="form-input"
                      placeholder="Paróquia – Diocese/Arquidiocese"
                    />
                  </div>
                </div>
              </>
            )}
          </section>

          {/* Irmãos na Catequese */}
          <section className="ficha-section">
            <h2 className="section-title">Irmãos na Catequese</h2>

            <div className="form-group">
              <label className="form-label">
                O catequizando tem irmão(s) que também fará(ão) catequese nesta etapa?
              </label>
              <div className="radio-group">
                <label className="radio-label">
                  <input
                    type="radio"
                    name="temIrmao"
                    value="sim"
                    checked={formData.temIrmao === 'sim'}
                    onChange={handleChange}
                  />
                  <span>Sim</span>
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    name="temIrmao"
                    value="nao"
                    checked={formData.temIrmao === 'nao'}
                    onChange={handleChange}
                  />
                  <span>Não</span>
                </label>
              </div>
            </div>

            {formData.temIrmao === 'sim' && (
              <>
                <div className="form-group">
                  <label className="form-label">Nome do(s) irmão(s):</label>
                  <input
                    type="text"
                    name="referenciaIrmao"
                    value={formData.referenciaIrmao}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Nome completo do irmão"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    Deseja que os irmãos fiquem na mesma turma?
                  </label>
                  <div className="radio-group">
                    <label className="radio-label">
                      <input
                        type="radio"
                        name="querMesmaTurmaQueIrmao"
                        value="sim"
                        checked={formData.querMesmaTurmaQueIrmao === 'sim'}
                        onChange={handleChange}
                      />
                      <span>Sim</span>
                    </label>
                    <label className="radio-label">
                      <input
                        type="radio"
                        name="querMesmaTurmaQueIrmao"
                        value="nao"
                        checked={formData.querMesmaTurmaQueIrmao === 'nao'}
                        onChange={handleChange}
                      />
                      <span>Não</span>
                    </label>
                  </div>
                </div>
              </>
            )}
          </section>

          {/* Dados dos Responsáveis */}
          <section className="ficha-section">
            <h2 className="section-title">Dados dos Responsáveis</h2>

            {/* Só mostrar se for maior de idade */}
            {maiorDeIdade && (
              <div className="form-group">
                <label className="form-label">O responsável é o próprio catequizando? *</label>
                <div className="radio-group">
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="responsavelProprio"
                      value="sim"
                      checked={formData.responsavelProprio === 'sim'}
                      onChange={handleChange}
                      required
                    />
                    <span>Sim</span>
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="responsavelProprio"
                      value="nao"
                      checked={formData.responsavelProprio === 'nao'}
                      onChange={handleChange}
                      required
                    />
                    <span>Não</span>
                  </label>
                </div>
              </div>
            )}

            {/* Se for menor, já assume que não é o próprio responsável */}
            {!maiorDeIdade && (
              <input
                type="hidden"
                name="responsavelProprio"
                value="nao"
                readOnly
              />
            )}

            {formData.responsavelProprio === 'nao' && (
              <>
                <div className="form-group">
                  <label className="form-label">Qual responsável está inscrevendo? *</label>
                  <div className="radio-group">
                    <label className="radio-label">
                      <input
                        type="radio"
                        name="tipoResponsavel"
                        value="pai"
                        checked={formData.tipoResponsavel === 'pai'}
                        onChange={handleChange}
                        required
                      />
                      <span>Pai</span>
                    </label>
                    <label className="radio-label">
                      <input
                        type="radio"
                        name="tipoResponsavel"
                        value="mae"
                        checked={formData.tipoResponsavel === 'mae'}
                        onChange={handleChange}
                        required
                      />
                      <span>Mãe</span>
                    </label>
                    <label className="radio-label">
                      <input
                        type="radio"
                        name="tipoResponsavel"
                        value="outro"
                        checked={formData.tipoResponsavel === 'outro'}
                        onChange={handleChange}
                        required
                      />
                      <span>Outro</span>
                    </label>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Nome do Pai:</label>
                  <input
                    type="text"
                    name="nomePai"
                    value={formData.nomePai}
                    onChange={handleChange}
                    className="form-input"
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Telefone do Pai:</label>
                    <input
                      type="tel"
                      name="telefonePai"
                      value={formData.telefonePai}
                      onChange={handleChange}
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">E-mail do Pai:</label>
                    <input
                      type="email"
                      name="emailPai"
                      value={formData.emailPai}
                      onChange={handleChange}
                      className="form-input"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Nome da Mãe:</label>
                  <input
                    type="text"
                    name="nomeMae"
                    value={formData.nomeMae}
                    onChange={handleChange}
                    className="form-input"
                    required={formData.tipoResponsavel === 'mae'}
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Telefone da Mãe:</label>
                    <input
                      type="tel"
                      name="telefoneMae"
                      value={formData.telefoneMae}
                      onChange={handleChange}
                      className="form-input"
                      required={formData.tipoResponsavel === 'mae'}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">E-mail da Mãe:</label>
                    <input
                      type="email"
                      name="emailMae"
                      value={formData.emailMae}
                      onChange={handleChange}
                      className="form-input"
                      required={formData.tipoResponsavel === 'mae'}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Outro Responsável (se aplicável):</label>
                  <input
                    type="text"
                    name="outroResponsavel"
                    value={formData.outroResponsavel}
                    onChange={handleChange}
                    className="form-input"
                    required={formData.tipoResponsavel === 'outro'}
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Telefone:</label>
                    <input
                      type="tel"
                      name="telefoneOutro"
                      value={formData.telefoneOutro}
                      onChange={handleChange}
                      className="form-input"
                      required={formData.tipoResponsavel === 'outro'}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">E-mail:</label>
                    <input
                      type="email"
                      name="emailOutro"
                      value={formData.emailOutro}
                      onChange={handleChange}
                      className="form-input"
                      required={formData.tipoResponsavel === 'outro'}
                    />
                  </div>
                </div>
              </>
            )}
          </section>

          {/* Preferência de Local */}
          <section className="ficha-section">
            <h2 className="section-title">Preferência de Local</h2>
            <p className="form-hint" style={{ marginBottom: '20px' }}>
              * Esta é uma consulta de preferência que está sujeita a vagas nas turmas oferecidas no local.
            </p>

            <div className="form-group">
              <label className="form-label">Onde prefere que seja a catequese?</label>
              <select
                name="local_encontro_id"
                value={formData.local_encontro_id}
                onChange={handleChange}
                className="form-input"
              >
                <option value="">Selecione um local (opcional)</option>
                {locaisEncontro.map(local => (
                  <option key={local.id} value={local.id}>
                    {local.nome_exibicao}
                  </option>
                ))}
              </select>
            </div>
          </section>

          {/* Documentos (OPCIONAL) */}
          <section className="ficha-section">
            <h2 className="section-title">Documentos (Opcional)</h2>
            <p className="form-hint" style={{ marginBottom: '20px' }}>
              * Você poderá enviar os documentos depois também.
            </p>
            <p className="form-hint" style={{ marginBottom: '20px', color: '#f39c12' }}>
              ⚠️ Se o sacramento foi recebido em nossa igreja, não é necessário enviar o documento agora.
              Caso necessário, a catequista solicitará posteriormente.
            </p>

            <div className="form-group">
              <label className="form-label">Identidade do Catequizando ou Certidão de Nascimento:</label>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => handleDocumentoChange('identidade', e.target.files[0])}
                className="form-input"
              />
            </div>

            {formData.batizado === 'sim' && (
              <div className="form-group">
                <label className="form-label">Certidão/Lembrança de Batismo:</label>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleDocumentoChange('batismo', e.target.files[0])}
                  className="form-input"
                />
                <p className="form-hint">
                  Se batizado nesta paróquia, não é necessário enviar.
                </p>
              </div>
            )}

            {formData.eucaristia === 'sim' && (
              <div className="form-group">
                <label className="form-label">Lembrança de Primeira Eucaristia:</label>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleDocumentoChange('eucaristia', e.target.files[0])}
                  className="form-input"
                />
                <p className="form-hint">
                  Se eucaristia nesta paróquia, não é necessário enviar.
                </p>
              </div>
            )}

            {formData.crisma === 'sim' && (
              <div className="form-group">
                <label className="form-label">Lembrança de Crisma:</label>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleDocumentoChange('crisma', e.target.files[0])}
                  className="form-input"
                />
                <p className="form-hint">
                  Se crisma nesta paróquia, não é necessário enviar.
                </p>
              </div>
            )}

            {formData.responsavelProprio === 'nao' && (
              <div className="form-group">
                <label className="form-label">Identidade do Responsável:</label>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleDocumentoChange('identidade_responsavel', e.target.files[0])}
                  className="form-input"
                />
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Comprovante de Residência:</label>
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => handleDocumentoChange('comprovante_residencia', e.target.files[0])}
                className="form-input"
              />
            </div>
          </section>

          {/* Informações Adicionais */}
          <section className="ficha-section">
            <h2 className="section-title">Informações Adicionais</h2>

            <div className="form-group">
              <label className="form-label">
                O catequizando possui alguma necessidade especial ou condição de saúde?
              </label>
              <div className="radio-group">
                <label className="radio-label">
                  <input
                    type="radio"
                    name="necessidadeEspecial"
                    value="sim"
                    checked={formData.necessidadeEspecial === 'sim'}
                    onChange={handleChange}
                  />
                  <span>Sim</span>
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    name="necessidadeEspecial"
                    value="nao"
                    checked={formData.necessidadeEspecial === 'nao'}
                    onChange={handleChange}
                  />
                  <span>Não</span>
                </label>
              </div>
            </div>

            {formData.necessidadeEspecial === 'sim' && (
              <div className="form-group">
                <label className="form-label">Especifique:</label>
                <textarea
                  name="descricaoNecessidade"
                  value={formData.descricaoNecessidade}
                  onChange={handleChange}
                  className="form-textarea"
                  rows="4"
                />
              </div>
            )}
          </section>

          {/* Autorização e Termo de Compromisso */}
          <section className="ficha-section termo-section">
            <h2 className="section-title">Autorização e Compromisso</h2>

            <div className="termo-texto autorizacao-texto">
              <p>
                Eu, <strong>{getNomeResponsavel()}</strong>, responsável pelo catequizando{' '}
                <strong>{formData.nomeCompleto || '_______________'}</strong>, autorizo a sua
                participação nas atividades da catequese e comprometo-me a acompanhar o seu
                desenvolvimento espiritual, garantindo a sua presença nos encontros e celebrações.
                Além disso, participar das reuniões e encontros de catequese em família.
              </p>

              <p>
                Também tenho ciência de que o catequizando que for catecúmeno, ou seja, que ainda
                não foi batizado, deverá receber o batismo este ano, visto que é imprescindível
                ter este sacramento da Iniciação Cristã, para que receba a Catequese adequada ao
                desenvolvimento na fé cristã católica, bem como para que possa receber o sacramento
                da Eucaristia. <em>(O sacramento do Batismo é obrigatório para se receber os demais sacramentos).</em>
              </p>

              <div className="termo-aceite">
                <p>Concordo e me comprometo com o acima descrito:</p>
                <div className="radio-group">
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="autorizacaoCompromisso"
                      value="concordo"
                      checked={formData.autorizacaoCompromisso === 'concordo'}
                      onChange={handleChange}
                      required
                    />
                    <span>Concordo</span>
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="autorizacaoCompromisso"
                      value="discordo"
                      checked={formData.autorizacaoCompromisso === 'discordo'}
                      onChange={handleChange}
                      required
                    />
                    <span>Discordo</span>
                  </label>
                </div>
              </div>
            </div>

            <div className="termo-texto termo-compromisso-texto">
              <h3 className="termo-subtitulo">TERMO DE COMPROMISSO DA FAMÍLIA</h3>

              <p>
                Eu, <strong>{getNomeResponsavel()}</strong>, ao inscrever{' '}
                <strong>{formData.nomeCompleto || '_______________'}</strong> para a catequese de{' '}
                <strong>{etapaSelecionada?.nome || '_______________'}</strong> na paróquia{' '}
                <strong>Divino Espírito Santo</strong>, recebi as informações importantes para o
                bom desenvolvimento do processo da Iniciação à Vida Cristã e comprometo-me a
                respeitar os seguintes requisitos da formação:
              </p>

              <ol className="termo-lista">
                <li>Os encontros da catequese são semanais e têm duração de uma hora e meia;</li>
                <li>Para os encontros é necessário que o catequizando tenha a Bíblia;</li>
                <li>Quando o catequizando faltar, deverá recuperar o encontro em horário combinado
                    com o catequista: observe-se um limite de até 3 faltas em um ano (na segunda a
                    família é notificada, na terceira é chamada para conversar e na quarta será
                    comunicada que a criança será convidada a parar o processo, podendo recomeçar
                    no ano seguinte);</li>
                <li>Em caso de doença e apresentação de atestado médico será proposta uma recuperação especial;</li>
                <li>Os familiares serão chamados para alguns encontros com o catequista, é fundamental
                    que algum responsável participe das reuniões;</li>
                <li>Algumas vezes o catequista ligará para sua casa, ou enviará e-mail para fazer
                    algum comunicado, ele fará em nome da Igreja, temos certeza que será bem acolhido;</li>
                <li>Ao longo do ano ocorrerão celebrações na Igreja em que o catequizando deverá
                    participar para passar às etapas seguintes de sua formação. A presença nessas
                    celebrações é imprescindível: duas faltas nestas celebrações interrompem o processo;</li>
                <li>Os catequizandos são convidados a participarem das celebrações da comunidade;</li>
                <li>Recebi, no ato da inscrição, as datas e horários dos compromissos deste Ano Catequético.</li>
              </ol>

              <p className="termo-observacao">
                *Haverá preparação para o Batismo especialmente para as crianças, adolescentes,
                jovens e adultos da catequese, num calendário que será confirmado pelos catequistas.
              </p>
            </div>

            <div className="form-group checkbox-termo">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="termoCompromisso"
                  checked={formData.termoCompromisso}
                  onChange={handleChange}
                  required
                />
                <span>Estou ciente e de acordo com o termo de compromisso *</span>
              </label>
            </div>
          </section>

          <button
            type="submit"
            className="enviar-button"
            disabled={loading}
          >
            {loading ? 'ENVIANDO...' : 'ENVIAR INSCRIÇÃO'}
          </button>
        </form>
      </main>
    </div>
  )
}

export default FichaInscricaoPage