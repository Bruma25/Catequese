import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import './MenuPerfil.css'

function MenuPerfil({ onClose, position = 'right' }) {
  const navigate = useNavigate()
  const { papeis, logout } = useAuth()

  // Mapear códigos para nomes amigáveis
  const nomePapel = {
    'responsavel': 'Responsável',
    'catequista': 'Catequista',
    'coordenador_etapa': 'Coordenador de Etapa',
    'coordenador_geral': 'Coordenador Geral'
  }

  const handleSelecionarPerfil = (papel) => {
    console.log('Perfil selecionado:', papel.codigo)
    // Salvar perfil ativo no localStorage
    localStorage.setItem('perfil_ativo', papel.codigo)
    // Disparar evento para atualizar MenuNavegacao
    window.dispatchEvent(new CustomEvent('perfil_mudou', { detail: papel.codigo }))
    onClose()
  }

  const handleSair = async () => {
    try {
      await logout()
      localStorage.removeItem('perfil_ativo')
      navigate('/')  // Volta para SplashScreen
    } catch (err) {
      console.error('Erro ao sair:', err)
    }
  }

  return (
    <div className={`menu-perfil ${position}`} onClick={onClose}>
      <div className="menu-perfil-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="menu-perfil-title">Meus Perfis</h3>

        <ul className="menu-perfil-list">
          {papeis.map(papel => (
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