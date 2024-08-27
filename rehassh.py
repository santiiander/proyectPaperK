from middlewares.security import hash_password
from config.database import SessionLocal
from models.usuario import Usuario

def rehash_password(email: str, new_password: str):
    db = SessionLocal()
    user = db.query(Usuario).filter(Usuario.email == email).first()

    if user:
        new_hashed_password = hash_password(new_password)
        user.hashed_password = new_hashed_password
        db.commit()
        print(f"Contraseña actualizada para {email}")
    else:
        print("Usuario no encontrado")

if __name__ == "__main__":
    email = "user@example.com"
    new_password = "tu_nueva_contraseña_segura"
    rehash_password(email, new_password)
