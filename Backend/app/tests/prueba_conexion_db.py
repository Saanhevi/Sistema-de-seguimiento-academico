from app.core.database import SessionLocal
from sqlalchemy import select, literal 

with SessionLocal() as session: 
    query = select(literal(50))
    
    resultado = session.execute(query).scalar()
    
    print(resultado)