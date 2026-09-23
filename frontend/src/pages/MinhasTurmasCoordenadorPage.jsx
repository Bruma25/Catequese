// ../frontend/src/pages/MinhasTurmasCoordenadorPage.jsx
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { supabase } from '../services/supabaseClient'
import Header from '../components/Header/Header'
import {
  listarMinhasTurmas,
  listarCatequizandosPorTurma,
  exportarCatequizandosTurma,
  listarCatequistas
} from '../services/api'
import './MinhasTurmasPage.css'

function MinhasTurmasCoordenadorPage() {
  const navigate = useNavigate()
  const [turmas, setTurmas] = useState([])
  const [catequistas, setCatequistas] = useState([])
  const [loading, setLoading] = useState(true)
  const [filtroCatequista, setFiltroCatequista] = useState('')
  const [turmaExpandida, setTurmaExpandida] = useState(null)
  const [catequizandosPorTurma, setCatequizandosPorTurma] = useState({})
  const [showModalExportar, setShowModalExportar] = useState(false)
  const [turmaParaExportar, setTurmaParaExportar] = useState(null)
  const [camposExportacao, setCamposExportacao] = useState([
    'nome',
    'data_nascimento',
    'idade',
    'responsaveis',
    'sacramentos'
  ])

  // CATEQUISTAS FILTRADOS (APENAS DA ETAPA)
  const [catequistasFiltrados, setCatequistasFiltrados] = useState([])

  // MAP: turma_id → [catequista_ids]
  const [turmasCatequistasMap, setTurmasCatequistasMap] = useState({})

  const camposDisponiveis = [
    { id: 'nome', label: 'Nome' },
    { id: 'data_nascimento', label: 'Data Nascimento' },
    { id: 'idade', label: 'Idade' },
    { id: 'telefone', label: 'Telefone' },
    { id: 'email', label: 'Email' },
    { id: 'responsaveis', label: 'Responsáveis' },
    { id: 'sacramentos', label: 'Sacramentos' },
    { id: 'documentos', label: 'Documentos' },
    { id: 'observacoes', label: 'Observações' },
    { id: 'necessidade_especial', label: 'Necessidade Especial' }
  ]

  useEffect(() => {
    window.scrollTo(0, 0)
    fetchData()
  }, [])

  async function fetchData() {
    try {
      const { data: { user } } = await supabase.auth.getUser()

      // BUSCAR ETAPA DO COORDENADOR
      const { data: coordenador } = await supabase
        .from('coordenador_etapa')
        .select('etapa_id')
        .eq('usuario_id', user.id)
        .single()

      if (!coordenador) {
        alert('Você não é coordenador de nenhuma etapa.')
        setLoading(false)
        return
      }

      // Buscar todas as turmas e filtrar por etapa
      const turmasData = await listarMinhasTurmas()
      const turmasFiltradasPorEtapa = turmasData.filter(t => t.etapa_id === coordenador.etapa_id)

      const catequistasData = await listarCatequistas()

      // BUSCAR TURMA_CATEQUISTA PARA TODAS AS TURMAS DA ETAPA
      const turmaIds = turmasFiltradasPorEtapa.map(t => t.id)

      const { data: turmaCatequistasData } = await supabase
        .from('turma_catequista')
        .select('turma_id, catequista_id')
        .in('turma_id', turmaIds)

      // CRIAR MAP: turma_id → [catequista_ids]
      const map = {}
      turmaCatequistasData?.forEach(tc => {
        if (!map[tc.turma_id]) {
          map[tc.turma_id] = []
        }
        map[tc.turma_id].push(tc.catequista_id)
      })

      // BUSCAR CATEQUISTAS DAS TURMAS DA ETAPA (via mapa)
      const catequistaIds = new Set()
      turmaIds.forEach(turmaId => {
        const catequistasDestaTurma = map[turmaId] || []
        catequistasDestaTurma.forEach(cId => {
          catequistaIds.add(cId)
        })
      })

      const catequistasDaEtapa = catequistasData.filter(c => catequistaIds.has(c.id))

      setTurmas(turmasFiltradasPorEtapa)
      setCatequistas(catequistasData)
      setCatequistasFiltrados(catequistasDaEtapa)
      setTurmasCatequistasMap(map)
    } catch (error) {
      console.error('Erro ao buscar dados:', error)
      alert('Erro ao carregar dados. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  // FILTRAR TURMAS POR CATEQUISTA (via mapa turma_catequista)
  const turmasFiltradas = turmas.filter(turma => {
    if (!filtroCatequista) return true

    // USAR MAPA PARA FILTRAR
    const catequistasDestaTurma = turmasCatequistasMap[turma.id] || []
    return catequistasDestaTurma.includes(filtroCatequista)
  })

  const handleExpandirTurma = async (turma) => {
    if (turmaExpandida === turma.id) {
      setTurmaExpandida(null)
      return
    }

    setTurmaExpandida(turma.id)

    try {
      const dados = await listarCatequizandosPorTurma(turma.id)
      setCatequizandosPorTurma(prev => ({
        ...prev,
        [turma.id]: dados.catequizandos
      }))
    } catch (error) {
      console.error('Erro ao buscar catequizandos:', error)
      alert('Erro ao carregar catequizandos da turma.')
    }
  }

  const handleAbrirExportar = (turma) => {
    setTurmaParaExportar(turma)
    setShowModalExportar(true)
  }

  const handleExportar = async () => {
    if (!turmaParaExportar) return

    try {
      const camposString = camposExportacao.join(',')
      await exportarCatequizandosTurma(turmaParaExportar.id, camposString)

      alert('Exportação realizada com sucesso!')
      setShowModalExportar(false)
      setTurmaParaExportar(null)
    } catch (error) {
      console.error('Erro ao exportar:', error)
      alert(`Erro: ${error.message}`)
    }
  }

  const handleToggleCampoExportacao = (campoId) => {
    setCamposExportacao(prev =>
      prev.includes(campoId)
        ? prev.filter(c => c !== campoId)
        : [...prev, campoId]
    )
  }

  const calcularIdade = (dataNascimento) => {
    if (!dataNascimento) return ''

    const hoje = new Date()
    const nasc = new Date(dataNascimento)
    let idade = hoje.getFullYear() - nasc.getFullYear()
    const mes = hoje.getMonth() - nasc.getMonth()

    if (mes < 0 || (mes === 0 && hoje.getDate() < nasc.getDate())) {
      idade--
    }

    return idade
  }

  if (loading) {
    return <div className="loading-container">Carregando...</div>
  }

  return (
    <div className="gestao-container">
      <Header titulo="Catequese Divino Espírito Santo" />

      <main className="gestao-content">
        <div className="gestao-header-content">
          <h2 className="page-title">Minhas Turmas</h2>
          <p className="perfil-ativo-info">Perfil: Coordenador de Etapa</p>
        </div>

        {/* Filtro por Catequista */}
        <div className="filtros-container">
          <div className="filtro-group">
            <label className="filtro-label">Catequista:</label>
            <select
              value={filtroCatequista}
              onChange={(e) => setFiltroCatequista(e.target.value)}
              className="filtro-select"
            >
              <option value="">Todos</option>
              {catequistasFiltrados.map(catequista => (
                <option key={catequista.id} value={catequista.id}>
                  {catequista.nome}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Lista de Turmas */}
        <div className="turmas-list">
          {turmasFiltradas.length === 0 ? (
            <p className="sem-turmas">Nenhuma turma encontrada</p>
          ) : (
            turmasFiltradas.map(turma => {
              const catequizandos = catequizandosPorTurma[turma.id] || []
              const isExpandida = turmaExpandida === turma.id

              return (
                <div key={turma.id} className={`turma-card ${isExpandida ? 'expandida' : ''}`}>
                  {/* HEADER OCUPA LARGURA TOTAL */}
                  <div className="turma-header" onClick={() => handleExpandirTurma(turma)}>
                    <div className="turma-info">
                      <h3 className="turma-nome">{turma.nome_exibicao || turma.nome_sistema}</h3>
                      <p className="turma-catequistas">
                        Catequizandos: {catequizandos.length}
                      </p>
                    </div>
                    <button className="expandir-button">
                      {isExpandida ? '▲ Recolher' : '▼ Expandir'}
                    </button>
                  </div>

                  {/* DETALHES EXPANDEM ABAIXO */}
                  {isExpandida && (
                    <div className="turma-detalhes">
                      <div className="turma-actions">
                        <button
                          className="exportar-button"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleAbrirExportar(turma)
                          }}
                        >
                          📥 Exportar Lista
                        </button>
                      </div>

                      {catequizandos.length === 0 ? (
                        <p className="sem-catequizandos">Nenhum catequizando nesta turma</p>
                      ) : (
                        <div className="catequizandos-table-container">
                          <table className="catequizandos-table">
                            <thead>
                              <tr>
                                <th>Nome</th>
                                <th>Data Nasc.</th>
                                <th>Idade</th>
                                <th>Responsáveis</th>
                                <th>Telefone</th>
                                <th>Sacramentos</th>
                                <th>Documentos</th>
                                <th>Obs.</th>
                              </tr>
                            </thead>
                            <tbody>
                              {catequizandos.map((cat, index) => {
                                const idade = calcularIdade(cat.data_nascimento)
                                const responsaveisNomes = cat.responsaveis.map(r => r.nome).join(', ')
                                const sacramentosNomes = cat.sacramentos.map(s => s.nome_exibicao).join(', ')

                                const docsAprovados = cat.documentos.filter(d => d.status_validacao === 'aprovado').length
                                const docsPendentes = cat.documentos.filter(d => d.status_validacao === 'pendente').length
                                const docsStatus = `${docsAprovados}✅ / ${docsPendentes}⏳`

                                return (
                                  <tr key={cat.id || index} className={cat.necessidade_especial ? 'necessidade-especial' : ''}>
                                    <td className="nome-col">{cat.nome}</td>
                                    <td>{cat.data_nascimento ? new Date(cat.data_nascimento).toLocaleDateString('pt-BR') : 'N/A'}</td>
                                    <td>{idade} anos</td>
                                    <td>{responsaveisNomes || 'N/A'}</td>
                                    <td>{cat.telefone || 'N/A'}</td>
                                    <td>{sacramentosNomes || 'Nenhum'}</td>
                                    <td>{docsStatus}</td>
                                    <td>{cat.observacoes ? '📝' : ''}</td>
                                  </tr>
                                )
                              })}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>
      </main>

      {/* Modal de Exportação */}
      {showModalExportar && turmaParaExportar && (
        <div className="modal-overlay" onClick={() => setShowModalExportar(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">Exportar Lista - {turmaParaExportar.nome_exibicao || turmaParaExportar.nome_sistema}</h3>

            <div className="form-group">
              <label className="form-label">Selecione os campos:</label>
              <div className="campos-checkboxes">
                {camposDisponiveis.map(campo => (
                  <label key={campo.id} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={camposExportacao.includes(campo.id)}
                      onChange={() => handleToggleCampoExportacao(campo.id)}
                    />
                    <span>{campo.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="modal-actions">
              <button
                className="cancelar-button"
                onClick={() => setShowModalExportar(false)}
              >
                Cancelar
              </button>
              <button
                className="salvar-button"
                onClick={handleExportar}
                disabled={camposExportacao.length === 0}
              >
                📥 EXPORTAR CSV
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MinhasTurmasCoordenadorPage