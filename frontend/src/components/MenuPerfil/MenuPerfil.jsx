import { useNavigate } from 'react-router-dom'
import './MenuPerfil.css'

function MenuPerfil({ onClose, position = 'right' }) {
  const navigate = useNavigate()

  // Mock de perfis (depois vem do backend/auth)
  const perfis = [
    { id: 1, nome: 'Coordenador Geral', papel: 'coordenador_geral' },
    { id: 2, nome: 'Responsável', papel: 'responsavel' }
  ]

  const handleSelecionarPerfil = (perfil) => {
    console.log('Perfil selecionado:', perfil)
    // TODO: Implementar troca de perfil
    onClose()
  }

  const handleSair = () => {
    console.log('Sair')
    // TODO: Implementar logout
    navigate('/login')
  }

  return (
    <div className={`menu-perfil ${position}`} onClick={onClose}>
      <div className="menu-perfil-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="menu-perfil-title">Meus Perfis</h3>

        <ul className="menu-perfil-list">
          {perfis.map(perfil => (
            <li key={perfil.id}>
              <button
                className="menu-perfil-item"
                onClick={() => handleSelecionarPerfil(perfil)}
              >
                {perfil.nome}
              </button>
            </li>
          ))}
        </ul>

        <button
          className="menu-perfil-sair"
          onClick={handleSair}
        >
          Sair
        </button>
      </div>
    </div>
  )
}

export default MenuPerfil