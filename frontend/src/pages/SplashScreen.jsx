import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './SplashScreen.css'
import logo from "../assets/logo.png"

function SplashScreen() {
  const navigate = useNavigate()

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/login')
    }, 5000) // 5 segundos

    return () => clearTimeout(timer)
  }, [navigate])

  return (
    <div className="splash-container">
      <div className="splash-content">
        {/* Imagem redonda*/}
        <div className="splash-image">
          <img src={logo} alt="Catequese Divino Espírito Santo" style = {{width: "250px", height:"250px", borderRadius: "50%", objectFit:"cover" }}/>
        </div>

        <h1 className="splash-text">
          Catequese Divino Espírito Santo
        </h1>
      </div>
    </div>
  )
}

export default SplashScreen