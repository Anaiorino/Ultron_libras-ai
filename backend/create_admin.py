from backend.database import SessionLocal, Base, engine
from backend.models import User
import hashlib

Base.metadata.create_all(bind=engine)

db = SessionLocal()


def hash_password(password: str):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


email = "anaiorino.8@gmail.com"

existing_user = db.query(User).filter(User.email == email).first()

if existing_user:
    existing_user.role = "ADMIN"
    existing_user.password = hash_password("Anaiorino.8")
    print("Usuário admin atualizado.")
else:
    admin = User(
        name="Ana Carolina",
        email=email,
        password=hash_password("Anaiorino.8"),
        role="ADMIN"
    )

    db.add(admin)
    print("Usuário admin criado.")

db.commit()
db.close()