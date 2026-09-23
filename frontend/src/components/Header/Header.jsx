// frontend/src/components/Header/Header.jsx
import { useState, useEffect } from 'react'
import { supabase } from '../../services/supabaseClient'
import logo from '../../assets/logo.png'
import divino from '../../assets/divino.png'
import papel from '../../assets/role.png'
import menu from '../../assets/menu.png'
import MenuPerfil from '../MenuPerfil/MenuPerfil'
import MenuNavegacao from '../MenuNavegacao/MenuNavegacao'
import { useAuth } from '../../hooks/useAuth'
import './Header.css'

function Header({ titulo = 'Catequese Divino Espírito Santo' }) {
  const [showMenuPerfil, setShowMenuPerfil] = useState(false)
  const [showMenuNavegacao, setShowMenuNavegacao] = useState(false)
  const [perfilAtivoInfo, setPerfilAtivoInfo] = useState(null)
  const { user, papeis } = useAuth()

  const perfilAtivo = localStorage.getItem('perfil_ativo')

  useEffect(() => {
    buscarPerfilAtivoInfo()
  }, [perfilAtivo])

  async function buscarPerfilAtivoInfo() {
    if (!perfilAtivo) {
      setPerfilAtivoInfo(null)
      return
    }

    try {
      const { data: papelData } = await supabase
        .from('tipo_papel_usuario')
        .select('codigo, descricao')
        .eq('codigo', perfilAtivo)
        .single()

      if (papelData) {
        setPerfilAtivoInfo({
          codigo: papelData.codigo,
          descricao: papelData.descricao
        })
      }
    } catch (error) {
      console.error('Erro ao buscar perfil ativo:', error)
    }
  }

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

  const getPerfilColor = (codigo) => {
    switch (codigo) {
      case 'COORDENADOR_GERAL':
        return '#B2ADB3'
      case 'COORDENADOR_ETAPA':
        return '#8B888C'
      case 'CATEQUISTA':
        return '#A8B8A8'
      case 'RESPONSAVEL':
        return '#B8A8A8'
      default:
        return '#CCCCCC'
    }
  }

  return (
    <>
      <header className="header">
        <div className="header-left">
          <img src={logo} alt="Logo" className="header-logo" />
          <h1 className="header-title">{titulo}</h1>
          <img src={divino} alt="Divino Espírito Santo" className="header-divino" />
        </div>
        
        <div className="header-right">
          {perfilAtivoInfo && (
            <div
              className="perfil-badge"
              style={{ backgroundColor: getPerfilColor(perfilAtivoInfo.codigo) }}
            >
              {perfilAtivoInfo.descricao || perfilAtivoInfo.codigo}
            </div>
          )}

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