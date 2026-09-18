// src/pages/ConfiguracoesPage.jsx
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Eye, EyeOff, User, Trash2, Save, LogOut } from 'lucide-react'
import { supabase } from '../services/supabaseClient'
import Header from '../components/Header/Header'
import './ConfiguracoesPage.css'

function ConfiguracoesPage() {
  const navigate = useNavigate()
  const [usuario, setUsuario] = useState(null)
  const [nome, setNome] = useState('')
  const [novaSenha, setNovaSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [mostrarNovaSenha, setMostrarNovaSenha] = useState(false)
  const [mostrarConfirmarSenha, setMostrarConfirmarSenha] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    carregarUsuario()
  }, [])

  async function carregarUsuario() {
    try {
      const { data: { user } } = await supabase.auth.getUser()

      if (!user) {
        navigate('/login')
        return
      }

      setUsuario(user)

      // Buscar dados do usuário na tabela usuario
      const { data: userData } = await supabase
        .from('usuario')
        .select('*')
        .eq('id', user.id)
        .single()

      if (userData) {
        setNome(userData.nome || '')
      }
    } catch (err) {
      console.error('❌ Erro ao carregar usuário:', err)
      navigate('/login')
    }
  }

  async function handleSalvarDados() {
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      // Atualizar nome na tabela usuario
      const { error } = await supabase
        .from('usuario')
        .update({ nome })
        .eq('id', usuario.id)

      if (error) throw error

      setSuccess('Dados atualizados com sucesso!')
    } catch (err) {
      setError(err.message || 'Erro ao atualizar dados')
    } finally {
      setLoading(false)
    }
  }

  async function handleAlterarSenha() {
    setError('')
    setSuccess('')

    if (!novaSenha || !confirmarSenha) {
      setError('Preencha todos os campos de senha')
      return
    }

    if (novaSenha !== confirmarSenha) {
      setError('As senhas não conferem')
      return
    }

    if (novaSenha.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres')
      return
    }

    setLoading(true)

    try {
      const { error } = await supabase.auth.updateUser({
        password: novaSenha
      })

      if (error) throw error

      setSuccess('Senha alterada com sucesso!')
      setNovaSenha('')
      setConfirmarSenha('')
    } catch (err) {
      setError(err.message || 'Erro ao alterar senha')
    } finally {
      setLoading(false)
    }
  }

  async function handleExcluirConta() {
    if (!window.confirm('Tem certeza que deseja excluir sua conta? Esta ação não pode ser desfeita.')) {
      return
    }

    setError('')
    setLoading(true)

    try {
      // Excluir da tabela usuario
      const { error } = await supabase
        .from('usuario')
        .delete()
        .eq('id', usuario.id)

      if (error) throw error

      // Excluir conta auth
      await supabase.auth.admin.deleteUser(usuario.id)

      await supabase.auth.signOut()
      navigate('/login')
    } catch (err) {
      setError(err.message || 'Erro ao excluir conta')
      setLoading(false)
    }
  }

  async function handleLogout() {
    await supabase.auth.signOut()
    navigate('/login')
  }

  return (
    <div className="config-container">
      {/* Cabeçalho Reutilizável */}
      <Header titulo="Catequese Divino Espírito Santo" />

      {/* Conteúdo Principal */}
      <main className="config-content">
        <h1 className="config-title">Configurações da Conta</h1>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {success && (
          <div className="success-message">
            {success}
          </div>
        )}

        {/* Dados do Usuário */}
        <div className="config-section">
          <h2 className="section-title">
            <User size={20} />
            Dados Pessoais
          </h2>

          <div className="form-group">
            <label className="form-label">Nome:</label>
            <input
              type="text"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              className="form-input"
              placeholder="Seu nome"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email:</label>
            <input
              type="email"
              value={usuario?.email || ''}
              className="form-input"
              disabled
              style={{ background: '#f5f5f5' }}
            />
          </div>

          <button
            className="btn-save"
            onClick={handleSalvarDados}
            disabled={loading}
          >
            <Save size={18} />
            Salvar Dados
          </button>
        </div>

        {/* Alterar Senha */}
        <div className="config-section">
          <h2 className="section-title">
            🔒 Alterar Senha
          </h2>

          <div className="form-group">
            <label className="form-label">Nova Senha:</label>
            <div className="password-input-group">
              <input
                type={mostrarNovaSenha ? 'text' : 'password'}
                value={novaSenha}
                onChange={(e) => setNovaSenha(e.target.value)}
                className="form-input"
                placeholder="Digite sua nova senha"
                disabled={loading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setMostrarNovaSenha(!mostrarNovaSenha)}
                disabled={loading}
              >
                {mostrarNovaSenha ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Confirmar Nova Senha:</label>
            <div className="password-input-group">
              <input
                type={mostrarConfirmarSenha ? 'text' : 'password'}
                value={confirmarSenha}
                onChange={(e) => setConfirmarSenha(e.target.value)}
                className="form-input"
                placeholder="Confirme sua nova senha"
                disabled={loading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setMostrarConfirmarSenha(!mostrarConfirmarSenha)}
                disabled={loading}
              >
                {mostrarConfirmarSenha ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <button
            className="btn-change-password"
            onClick={handleAlterarSenha}
            disabled={loading || !novaSenha || !confirmarSenha}
          >
            🔒 Alterar Senha
          </button>
        </div>

        {/* Excluir Conta */}
        <div className="config-section danger-zone">
          <h2 className="section-title danger">
            <Trash2 size={20} />
            Zona de Perigo
          </h2>

          <p className="danger-text">
            Excluir sua conta é permanente e não pode ser desfeito.
          </p>

          <button
            className="btn-delete"
            onClick={handleExcluirConta}
            disabled={loading}
          >
            <Trash2 size={18} />
            Excluir Conta
          </button>
        </div>

        {/* Logout */}
        <div className="config-footer">
          <button
            className="btn-logout"
            onClick={handleLogout}
          >
            <LogOut size={18} />
            Sair
          </button>
        </div>
      </main>
    </div>
  )
}

export default ConfiguracoesPage