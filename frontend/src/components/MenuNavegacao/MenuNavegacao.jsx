import { useNavigate } from 'react-router-dom'
import './MenuNavegacao.css'

function MenuNavegacao({ onClose, position = 'right' }) {
  const navigate = useNavigate()

  // Mock de itens de menu (depois vem do backend, baseado no perfil)
  const itensMenu = [
    { id: 1, nome: 'Home', caminho: '/home', perfis: ['todos'] },
    { id: 2, nome: 'Inscrição', caminho: '/etapas', perfis: ['todos'] },
    { id: 3, nome: 'Gestão de Etapas', caminho: '/gestao-etapas', perfis: ['coordenador_geral'] },
    { id: 4, nome: 'Gestão de Turmas', caminho: '/gestao-turmas', perfis: ['coordenador_geral'] },
    { id: 5, nome: 'Inscrições', caminho: '/inscricoes', perfis: ['coordenador_geral'] }
  ]

  // Mock do perfil atual (depois vem do auth)
  const perfilAtual = 'coordenador_geral'

  const handleNavegar = (caminho) => {
    navigate(caminho)
    onClose()
  }

  const itensFiltrados = itensMenu.filter(item =>
    item.perfis.includes('todos') || item.perfis.includes(perfilAtual)
  )

  return (
    <div className={`menu-navegacao ${position}`} onClick={onClose}>
      <div className="menu-navegacao-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="menu-navegacao-title">Menu</h3>

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