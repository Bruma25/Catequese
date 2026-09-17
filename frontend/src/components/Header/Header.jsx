import { useState } from 'react'
import logo from '../../assets/logo.png'
import papel from '../../assets/role.png'
import menu from '../../assets/menu.png'
import MenuPerfil from '../MenuPerfil/MenuPerfil'
import MenuNavegacao from '../MenuNavegacao/MenuNavegacao'
import { useAuth } from '../../hooks/useAuth'
import './Header.css'

function Header({ titulo = 'Catequese Divino Espírito Santo' }) {
  const [showMenuPerfil, setShowMenuPerfil] = useState(false)
  const [showMenuNavegacao, setShowMenuNavegacao] = useState(false)
  const { user, papeis } = useAuth()

  const perfilAtivo = localStorage.getItem('perfil_ativo')

  const handleToggleMenuPerfil = () => {
    setShowMenuPerfil(!showMenuPerfil)
    setShowMenuNavegacao(false)
  }

  const handleToggleMenuNavegacao = () => {
    setShowMenuNavegacao(!showMenuNavegacao)
    setShowMenuPerfil(false)
  }

  const handleCloseMenus = () => {
    setShowMenuPerfil(false)
    setShowMenuNavegacao(false)
  }

  return (
    <>
      <header className="header">
        <div className="header-left">
          <img src={logo} alt="Logo" className="header-logo" />
          <h1 className="header-title">{titulo}</h1>
        </div>
        <div className="header-right">
          <button
            onClick={handleToggleMenuPerfil}
            className="icon-button"
            aria-label="Menu de perfis"
          >
            <img src={papel} alt="Perfil" className="header-icon" />
          </button>
          <button
            onClick={handleToggleMenuNavegacao}
            className="icon-button"
            aria-label="Menu de navegação"
          >
            <img src={menu} alt="Menu" className="header-icon" />
          </button>
        </div>
      </header>

      {/* Menus */}
      {showMenuPerfil && (
        <MenuPerfil
          onClose={handleCloseMenus}
          position="right"
        />
      )}

      {showMenuNavegacao && (
        <MenuNavegacao
          onClose={handleCloseMenus}
          position="right"
        />
      )}
    </>
  )
}

export default Header