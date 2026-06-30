from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException
import os

UTM_SECRET_KEY = os.getenv("UTM_SECRET_KEY")
ALGORITHM = "HS256"

def crear_token(data_user: dict):
    payload = {
        "email": data_user["email"],
        "name": data_user["name"],
        "user": data_user["id_user"],
        "uso": "crear_utm",
        "exp": datetime.utcnow() + timedelta(hours=120) # Expira en 5 días
    }

    token = jwt.encode(payload, UTM_SECRET_KEY, algorithm=ALGORITHM)
    print(token)
    return token


def validar_token(token: str):
    
    try:
        payload = jwt.decode(token, UTM_SECRET_KEY, algorithms=[ALGORITHM])

        if payload["uso"] != "crear_utm":
            raise HTTPException(status_code=403, detail="Token inválido")
        
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")