from sqlalchemy.orm import DeclarativeBase # É a classe-base do sistema declarativo do SQLAlchemy.

class Base(DeclarativeBase): # Será herdada pelas três classes de modelo.
    pass