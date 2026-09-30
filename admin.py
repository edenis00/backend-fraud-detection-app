from app.database.session import SessionLocal
from app.core.enums import UserRole
from app.users.models import User

email = input("Email of the account to promote: ").strip().lower()

with SessionLocal() as db:
    user = db.query(User).filter(User.email == email).one_or_none()
    if user is None:
        raise SystemExit("No account found for that email. Register it first.")
    user.role = UserRole.ADMIN
    db.commit()

print(f"{email} is now an admin.")