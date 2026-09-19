import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useAuth } from '../../hooks/useAuth'
import './MenuNavegacao.css'

function MenuNavegacao({ onClose, position = 'right' }) {
  const navigate = useNavigate()
  const { papeis } = useAuth()
  const [perfilAtivo, setPerfilAtivo] = useState('')

  // Itens de menu por perfil
  const itensMenu = [
    { id: 1, nome: 'Home', caminho: '/home', perfis: ['todos'] },
    { id: 2, nome: 'Inscrição', caminho: '/etapas', perfis: ['todos'] },
    { id: 3, nome: 'Gestão de Usuários', caminho: '/gestao-usuarios', perfis: ['coordenador_geral'] },
    { id: 4, nome: 'Gestão de Etapas', caminho: '/gestao-etapas', perfis: ['coordenador_geral'] },
    { id: 5, nome: 'Gestão de Turmas', caminho: '/gestao-turmas', perfis: ['coordenador_geral', 'coordenador_etapa'] },
    { id: 6, nome: 'Gestão de Inscrições', caminho: '/gestao-inscricoes', perfis: ['coordenador_geral', 'coordenador_etapa'] },
    { id: 7, nome: 'Minhas Turmas', caminho: '/minhas-turmas', perfis: ['catequista'] },
    { id: 8, nome: 'Meus Catequizandos', caminho: '/meus-catequizandos', perfis: ['responsavel'] },
    { id: 9, nome: 'Configuração da conta', caminho: '/configuracoes', perfis: ['todos'] }
  ]

  // Carregar perfil ativo do localStorage
  useEffect(() => {
    const perfilSalvo = localStorage.getItem('perfil_ativo')

    if (perfilSalvo && papeis.some(p => p.codigo === perfilSalvo)) {
      setPerfilAtivo(perfilSalvo)
    } else if (papeis.length > 0) {
      // Se não tem perfil salvo, usa o primeiro
      setPerfilAtivo(papeis[0].codigo)
      localStorage.setItem('perfil_ativo', papeis[0].codigo)
    }

    // Ouvir evento de troca de perfil
    const handlePerfilMudou = (event) => {
      setPerfilAtivo(event.detail)
    }

    window.addEventListener('perfil_mudou', handlePerfilMudou)

    return () => {
      window.removeEventListener('perfil_mudou', handlePerfilMudou)
    }
  }, [papeis])

  const handleNavegar = (caminho) => {
    navigate(caminho)
    onClose()
  }

  // Filtrar itens baseado no perfil ativo
  const itensFiltrados = itensMenu.filter(item =>
    item.perfis.includes('todos') || item.perfis.includes(perfilAtivo)
  )

  return (
    <div className={`menu-navegacao ${position}`} onClick={onClose}>
      <div className="menu-navegacao-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="menu-navegacao-title">
          Menu {perfilAtivo && `- ${perfilAtivo.replace('_', ' ')}`}
        </h3>

        <ul className="menu-navegacao-list">
          {itensFiltrados.map(item => (
            <li key={item.id}>
              <button
                className="menu-navegacao-item"
                onClick={() => handleNavegar(item.caminho)}
              >
                {item.nome}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default MenuNavegacao