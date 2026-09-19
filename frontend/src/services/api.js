const API_URL = import.meta.env.VITE_API_URL

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  })

  if (!response.ok) {
    let errorMessage = 'Ocorreu um erro na comunicação com o servidor.'

    try {
      const errorData = await response.json()

      if (errorData.detail) {
        errorMessage = errorData.detail
      }
    } catch {
      // Mantém a mensagem padrão caso a resposta não seja JSON.
    }

    throw new Error(errorMessage)
  }

  return response.json()
}

// ✅ CORRETO - Adiciona a barra entre API_URL e o caminho
export async function contarInscricoesPorTurma(turmaId) {
  try {
    const response = await fetch(`${API_URL}/api/v1/inscricoes/contar-por-turma/${turmaId}`)

    if (!response.ok) {
      console.warn(`⚠️ Erro ao contar inscrições para turma ${turmaId}: ${response.status}`)
      return 0
    }

    const data = await response.json()
    return data.count || 0
  } catch (error) {
    console.error('❌ Erro ao contar inscrições:', error)
    return 0  // Fallback para não quebrar a página
  }
}

// Etapas
export async function listarEtapas() {
  return request('/api/v1/etapas')
}

// Sacramentos
export async function listarSacramentos() {
  return request('/api/v1/sacramentos')
}

// Tipos de vínculo
export async function listarTiposVinculo() {
  return request('/api/v1/tipos-vinculo')
}

// Etapas - CRUD completo
export async function buscarEtapa(id) {
  return request(`/api/v1/etapas/${id}`)
}

export async function criarEtapa(dados) {
  return request('/api/v1/etapas', {
    method: 'POST',
    body: JSON.stringify(dados)
  })
}

export async function editarEtapa(id, dados) {
  return request(`/api/v1/etapas/${id}`, {
    method: 'PUT',
    body: JSON.stringify(dados)
  })
}

export async function excluirEtapa(id) {
  return request(`/api/v1/etapas/${id}`, {
    method: 'DELETE'
  })
}

// Inscrições
export async function criarInscricao(dados) {
  return request('/api/v1/inscricoes', {
    method: 'POST',
    body: JSON.stringify(dados)
  })
}

export async function listarInscricoes() {
  return request('/api/v1/inscricoes')
}

export async function buscarInscricao(id) {
  return request(`/api/v1/inscricoes/${id}`)
}

export async function listarTurmas() {
  return request('/api/v1/turmas')
}

export async function buscarTurma(id) {
  return request(`/api/v1/turmas/${id}`)
}

export async function criarTurma(dados) {
  return request('/api/v1/turmas', {
    method: 'POST',
    body: JSON.stringify(dados)
  })
}

export async function editarTurma(id, dados) {
  return request(`/api/v1/turmas/${id}`, {
    method: 'PUT',
    body: JSON.stringify(dados)
  })
}

export async function excluirTurma(id) {
  return request(`/api/v1/turmas/${id}`, {
    method: 'DELETE'
  })
}

export async function listarLocaisEncontro() {
  return request('/api/v1/locais-encontro')
}

export async function listarCatequistas() {
  return request('/api/v1/catequistas')
}

// Inscrições - Gestão
export async function buscarInscricaoCompleta(id) {
  return request(`/api/v1/inscricoes/${id}/completa`)
}

export async function listarInscricoesPorEtapa(etapaId) {
  return request(`/api/v1/inscricoes/etapa/${etapaId}`)
}

export async function listarInscricoesPorStatus(statusCodigo) {
  return request(`/api/v1/inscricoes/status/${statusCodigo}`)
}

export async function listarPendentesDistribuicao() {
  return request('/api/v1/inscricoes/pendentes-distribuicao')
}

export async function atualizarStatusInscricao(inscricaoId, statusId) {
  return request(`/api/v1/inscricoes/${inscricaoId}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status_id: statusId })
  })
}

export async function atribuirTurmaInscricao(inscricaoId, turmaId) {
  return request(`/api/v1/inscricoes/${inscricaoId}/turma?turma_id=${turmaId}`, {
    method: 'PUT'
  })
}

export async function removerTurmaInscricao(inscricaoId) {
  return request(`/api/v1/inscricoes/${inscricaoId}/turma`, {
    method: 'DELETE'
  })
}

export async function listarDocumentosInscricao(inscricaoId) {
  return request(`/api/v1/inscricoes/${inscricaoId}/documentos`)
}

export async function atualizarStatusDocumento(documentoId, statusValidacao, observacaoValidacao = null) {
  const url = observacaoValidacao
      ? `/api/v1/documentos/${documentoId}/status?status_validacao=${statusValidacao}&observacao_validacao=${encodeURIComponent(observacaoValidacao)}`
      : `/api/v1/documentos/${documentoId}/status?status_validacao=${statusValidacao}`

  return request(url, {
    method: 'PUT'
  })
}

export async function excluirDocumento(documentoId) {
  return request(`/api/v1/documentos/${documentoId}`, {
    method: 'DELETE'
  })
}

export async function contarVagasOcupadas(turmaId) {
  return request(`/api/v1/turmas/${turmaId}/vagas-ocupadas`)
}

export async function uploadDocumento(inscricaoId, file, tipoDocumento) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('tipo_documento', tipoDocumento)

  const url = `${import.meta.env.VITE_API_URL}/api/v1/inscricoes/${inscricaoId}/documentos`

  console.log('📤 Upload documento:', {
    url,
    tipoDocumento,
    fileName: file.name,
    fileSize: file.size
  })

  const response = await fetch(url, {
    method: 'POST',
    body: formData
    // NÃO passar headers - o navegador define automaticamente
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    console.error('❌ Erro no upload:', errorData)
    throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`)
  }

  const result = await response.json()
  console.log('✅ Upload sucesso:', result)

  return result
}

// Usuários
export async function listarUsuarios() {
  return request('/api/v1/usuarios')
}

export async function buscarUsuario(id) {
  return request(`/api/v1/usuarios/${id}`)
}

export async function criarUsuario(dados) {
  return request('/api/v1/usuarios', {
    method: 'POST',
    body: JSON.stringify(dados)
  })
}

export async function editarUsuario(id, dados) {
  return request(`/api/v1/usuarios/${id}`, {
    method: 'PUT',
    body: JSON.stringify(dados)
  })
}

export async function excluirUsuario(id) {
  return request(`/api/v1/usuarios/${id}`, {
    method: 'DELETE'
  })
}

export async function listarPapeis() {
  return request('/api/v1/tipos-papel')
}

export async function atualizarPapeisUsuario(usuarioId, papeisIds) {
  return request(`/api/v1/usuarios/${usuarioId}/papeis`, {
    method: 'PUT',
    body: JSON.stringify({ papeis_ids: papeisIds })
  })
}

// Meus Catequizandos
export async function atualizarDadosCatequizando(catequizandoId, dados) {
  return request(`/api/v1/catequizandos/${catequizandoId}`, {
    method: 'PUT',
    body: JSON.stringify(dados)
  })
}

export async function buscarCatequizandoPorId(id) {
  return request(`/api/v1/catequizandos/${id}`)
}