from app.core.security import controlador_contrasena

#Prueba verificacion
resultado_hash = controlador_contrasena.hashear("SAMUEL")
print(f"El resultado es: {resultado_hash}")

contrasena_prueba = "samuel"
# Retorna False
print(controlador_contrasena.verificar_contrasena(contrasena_prueba, resultado_hash))
# Retorna True
print(controlador_contrasena.verificar_contrasena("SAMUEL", resultado_hash))

