# app/infra/jwt_utils.py
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException

# URL do JWKS do Supabase (substitua pela sua URL)
JWKS_URL = "https://jhzvuymbztpt hauoqxjr.supabase.co/auth/v1/jwks"
SUPABASE_ISSUER = "https://jhzvuymbztpt hauoqxjr.supabase.co/auth/v1"

jwks_client = PyJWKClient(JWKS_URL)


def validar_token_supabase(token: str) -> str:
    """
    Valida token JWT do Supabase e retorna o user_id (sub).
    Lança HTTPException 401 se o token for inválido.
    """
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            issuer=SUPABASE_ISSUER,
            options={"verify_aud": False}  # Supabase não usa audience por padrão
        )

        return payload["sub"]  # user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erro ao validar token: {str(e)}")