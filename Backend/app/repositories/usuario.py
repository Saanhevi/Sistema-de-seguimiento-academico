from app.models.usuario import Usuario
from sqlalchemy import select

class UsuarioRepository: 
    
    def __init__(self, session):
        self.session = session # Se pasa la session que crea el servicio
    
    def buscar_por_correo(self, correo):
        query = select(Usuario).where(Usuario.correo == correo) # Se busca por correo
        resultado = self.session.execute(query).scalars().first() # Se guarda el primer y unico registro 
            
        return resultado 
    
    def buscar_por_id(self, id_usuario):
        query = select(Usuario).where(Usuario.id_usuario == id_usuario) # Se busca por id_usuario
        resultado = self.session.execute(query).scalars().first()
            
        return resultado
    
    def crear(self, usuario: Usuario):
        self.session.add(usuario)
        self.session.commit()   
        
        self.session.refresh(usuario) # Se refresca el objeto usuario para que incluya el id
        return usuario
    
    def actualizar(self, nuevo_usuario: Usuario):
        # El nuevo usuario es actualizado por el servicio
        self.session.commit()
            
        return nuevo_usuario
    
    def eliminar(self, usuario: Usuario):            
        self.session.delete(usuario) #Se borra el usuario
            
        self.session.commit() # Se realiza la transaccion
            
            