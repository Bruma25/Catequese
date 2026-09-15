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