from app.core.database import SessionLocal
from app.models import Usuario
from sqlalchemy import select

with SessionLocal() as session:
    query = select(Usuario).where(Usuario.rol == "Administrador")
    
    resultados = session.execute(query).scalars().all()
    
    print(f"Se encontraron {len(resultados)} resultados")
    for resultado in resultados: 
        print(resultado) 