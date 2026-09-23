// ../frontend/components/MenuPerfil/MenuPerfil.jsx
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import './MenuPerfil.css'

function MenuPerfil({ onClose, position = 'right' }) {
  const navigate = useNavigate()
  const { papeis, logout } = useAuth()

  const nomePapel = {
    'RESPONSAVEL': 'Responsável',
    'CATEQUISTA': 'Catequista',
    'COORDENADOR_ETAPA': 'Coordenador de Etapa',
    'COORDENADOR_GERAL': 'Coordenador Geral'
  }

  const handleSelecionarPerfil = (papel) => {
    console.log('Perfil selecionado:', papel.codigo)
    localStorage.setItem('perfil_ativo', papel.codigo)
    window.dispatchEvent(new CustomEvent('perfil_mudou', { detail: papel.codigo }))
    onClose()
  }

  const handleSair = async () => {
    try {
      await logout()
      localStorage.removeItem('perfil_ativo')
      navigate('/')
    } catch (err) {
      console.error('Erro ao sair:', err)
    }
  }

  const papeisOrdenados = [...papeis].sort((a, b) => a.id - b.id)

  return (
    <div className={`menu-perfil ${position}`} onClick={onClose}>
      <div className="menu-perfil-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="menu-perfil-title">Meus Perfis</h3>

        <ul className="menu-perfil-list">
          {papeisOrdenados.map(papel => (
            <li key={papel.id}>
              <button
                className="menu-perfil-item"
                onClick={() => handleSelecionarPerfil(papel)}
              >
                {nomePapel[papel.codigo] || papel.descricao}
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