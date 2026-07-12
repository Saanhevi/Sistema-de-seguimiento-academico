from pwdlib import PasswordHash

class ControladorContrasena: 
    password_hash = PasswordHash.recommended()
    
    def hashear(self, contrasena_plana):
        return self.password_hash.hash(contrasena_plana) #Retorna la contrasena hasheada
    
    def verificar_contrasena(self, contrasena_plana, hash_guardado):
        # Retorna true si la contrasena es correcta
        return self.password_hash.verify(contrasena_plana, hash_guardado)
    
controlador_contrasena = ControladorContrasena()

