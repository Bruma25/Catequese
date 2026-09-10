const API_URL = import.meta.env.VITE_API_URL;

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorMessage = "Ocorreu um erro na comunicação com o servidor.";

    try {
      const errorData = await response.json();

      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      // Mantém a mensagem padrão caso a resposta não seja JSON.
    }

    throw new Error(errorMessage);
  }

  return response.json();
}

export async function listarEtapas() {
  return request("/api/v1/etapas");
}

export async function criarInscricao(dados) {
  return request("/api/v1/inscricoes", {
    method: "POST",
    body: JSON.stringify(dados),
  });
}

export async function listarInscricoes() {
  return request("/api/v1/inscricoes");
}

export async function buscarInscricao(id) {
  return request(`/api/v1/inscricoes/${id}`);
}