from sqlalchemy.orm import Session
from app.db.models import User
from app.core.security import get_password_hash


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieve a user by email address.
    
    Args:
        db: Database session
        email: Email address to search for
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str) -> User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        email: User's email address
        password: Plain text password (will be hashed)
        
    Returns:
        Newly created User object
    """
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
