import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import logo from '../assets/logo.png'
import papel from '../assets/role.png'
import menu from '../assets/menu.png'
import { supabase } from '../services/supabaseClient'
import './FichaInscricaoPage.css'

function FichaInscricaoPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [etapaSelecionada, setEtapaSelecionada] = useState(null)
  const [sacramentosCatequizando, setSacramentosCatequizando] = useState([])

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
    autorizacaoCompromisso: false
  })

  // Carregar dados da página anterior e rolar para o topo
  useEffect(() => {
    // Rolar para o topo da página
    window.scrollTo(0, 0)

    const inscricaoData = localStorage.getItem('inscricao_data')
    if (inscricaoData) {
      const { dataNascimento, sacramentos, etapaSelecionada } = JSON.parse(inscricaoData)
      setEtapaSelecionada(etapaSelecionada)

      // Calcular idade
      if (dataNascimento) {
        const hoje = new Date()
        const nasc = new Date(dataNascimento)
        const idade = hoje.getFullYear() - nasc.getFullYear()
        setFormData(prev => ({
          ...prev,
          dataNascimento: dataNascimento,
          idade: idade.toString(),
          batizado: sacramentos?.includes(1) ? 'sim' : 'nao'
        }))
      }
    } else {
      alert('Nenhuma etapa selecionada. Redirecionando...')
      navigate('/etapas')
    }
  }, [navigate])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
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

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.termoCompromisso || formData.autorizacaoCompromisso !== 'concordo') {
      alert('Por favor, aceite o termo de compromisso e a autorização')
      return
    }

    setLoading(true)

    try {
      // 1. Criar Responsável
      const responsavelData = {
        nome: getNomeResponsavel(),
        email: formData.emailMae || formData.emailPai || formData.emailOutro || formData.email || null,
        telefone: formData.telefoneMae || formData.telefonePai || formData.telefoneOutro || formData.telefone1 || null
      }

      const { data: responsavel, error: errorResponsavel } = await supabase
        .from('responsavel')
        .insert([responsavelData])
        .select()
        .single()

      if (errorResponsavel) {
        console.error('Erro ao criar responsável:', errorResponsavel)
        throw errorResponsavel
      }

      // 2. Criar Catequizando
      const catequizandoData = {
        nome: formData.nomeCompleto,
        data_nascimento: formData.dataNascimento,
        endereco: formData.endereco || null,
        telefone: formData.telefone1 || null,
        email: formData.email || null,
        necessidade_especial: formData.necessidadeEspecial === 'sim',
        descricao_necessidade_especial: formData.necessidadeEspecial === 'sim' ? (formData.descricaoNecessidade || null) : null,
        observacoes: null
      }

      const { data: catequizando, error: errorCatequizando } = await supabase
        .from('catequizando')
        .insert([catequizandoData])
        .select()
        .single()

      if (errorCatequizando) {
        console.error('Erro ao criar catequizando:', errorCatequizando)
        throw errorCatequizando
      }

      // 3. Criar Histórico Sacramental
      const inscricaoDataRaw = localStorage.getItem('inscricao_data')
      if (inscricaoDataRaw) {
        const { sacramentos } = JSON.parse(inscricaoDataRaw)
        if (sacramentos && sacramentos.length > 0) {
          const historicoData = sacramentos.map(sacramentoId => ({
            catequizando_id: catequizando.id,
            sacramento_id: sacramentoId
          }))

          const { error: errorHistorico } = await supabase
            .from('historico_sacramental')
            .insert(historicoData)

          if (errorHistorico) {
            console.error('Erro ao criar histórico sacramental:', errorHistorico)
          }
        }
      }

      // 4. Criar Inscrição
      const inscricaoData = {
        catequizando_id: catequizando.id,
        responsavel_id: responsavel.id,
        etapa_id: etapaSelecionada.id,
        status_id: 1,
        termo_assinado: true,
        quer_mesma_turma_que_irmao: false,
        override_idade: false,
        observacao_responsavel: formData.necessidadeEspecial === 'sim' ? formData.descricaoNecessidade : null,
        data_inscricao: new Date().toISOString()
      }

      const { data: inscricao, error: errorInscricao } = await supabase
        .from('inscricao')
        .insert([inscricaoData])
        .select()
        .single()

      if (errorInscricao) {
        console.error('Erro ao criar inscrição:', errorInscricao)
        throw errorInscricao
      }

      console.log('Inscrição criada com sucesso!', inscricao)
      alert('Inscrição realizada com sucesso!')

      // Limpar localStorage
      localStorage.removeItem('inscricao_data')

      navigate('/home')

    } catch (error) {
      console.error('Erro ao salvar inscrição:', error)
      alert(`Erro ao realizar inscrição: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handlePerfilClick = () => {
    alert('Menu de perfis (será implementado depois)')
  }

  const handleMenuClick = () => {
    alert('Menu de navegação (será implementado depois)')
  }

  if (!etapaSelecionada) {
    return <div className="loading-container">Carregando...</div>
  }

  return (
    <div className="ficha-container">
      {/* Cabeçalho */}
      <header className="ficha-header">
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
          </section>

          {/* Dados dos Responsáveis */}
          <section className="ficha-section">
            <h2 className="section-title">Dados dos Responsáveis</h2>

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

            {/* Autorização */}
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

            {/* Termo de Compromisso */}
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

            {/* Checkbox de Aceite */}
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

          {/* Botão Enviar */}
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