import re
import dns.resolver
from typing import Tuple, Optional

def validar_email(email: str) -> Tuple[bool, str]:
    """
    Valida una dirección de email.
    
    Args:
        email (str): La dirección de email a validar
        
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    
    # Verificar que el email no esté vacío
    if not email or not email.strip():
        return False, "El email no puede estar vacío"
    
    # Eliminar espacios en blanco
    email = email.strip()
    
    # Patrón regex para validar formato básico de email
    patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Verificar formato básico
    if not re.match(patron_email, email):
        return False, "Formato de email inválido"
    
    # Dividir en usuario y dominio
    try:
        usuario, dominio = email.split('@')
    except ValueError:
        return False, "El email debe contener exactamente un símbolo @"
    
    # Validar longitud del usuario
    if len(usuario) < 1:
        return False, "El nombre de usuario no puede estar vacío"
    if len(usuario) > 64:
        return False, "El nombre de usuario es demasiado largo (máximo 64 caracteres)"
    
    # Validar longitud del dominio
    if len(dominio) < 1:
        return False, "El dominio no puede estar vacío"
    if len(dominio) > 255:
        return False, "El dominio es demasiado largo (máximo 255 caracteres)"
    
    # Validar que el dominio tenga al menos un punto
    if '.' not in dominio:
        return False, "El dominio debe contener al menos un punto"
    
    # Validar que no empiece o termine con punto
    if dominio.startswith('.') or dominio.endswith('.'):
        return False, "El dominio no puede empezar o terminar con punto"
    
    # Validar que no tenga puntos consecutivos
    if '..' in dominio:
        return False, "El dominio no puede tener puntos consecutivos"
    
    # Validar caracteres especiales en el usuario
    caracteres_invalidos = ['<', '>', '"', "'", '(', ')', '[', ']', '\\', ';', ':', ',', ' ']
    for char in caracteres_invalidos:
        if char in usuario:
            return False, f"El nombre de usuario no puede contener el carácter '{char}'"
    
    # Validar que el usuario no empiece o termine con punto
    if usuario.startswith('.') or usuario.endswith('.'):
        return False, "El nombre de usuario no puede empezar o terminar con punto"
    
    # Validar que no tenga puntos consecutivos en el usuario
    if '..' in usuario:
        return False, "El nombre de usuario no puede tener puntos consecutivos"
    
    return True, "Email válido"

def validar_email_con_dns(email: str) -> Tuple[bool, str]:
    """
    Valida una dirección de email y verifica que el dominio tenga registros MX.
    
    Args:
        email (str): La dirección de email a validar
        
    Returns:
        Tuple[bool, str]: (es_valido, mensaje_error)
    """
    
    # Primero validar formato básico
    es_valido, mensaje = validar_email(email)
    if not es_valido:
        return False, mensaje
    
    # Extraer dominio
    dominio = email.split('@')[1]
    
    # Verificar registros MX del dominio
    try:
        dns.resolver.resolve(dominio, 'MX')
        return True, "Email válido y dominio verificado"
    except dns.resolver.NXDOMAIN:
        return False, "El dominio no existe"
    except dns.resolver.NoAnswer:
        return False, "El dominio no tiene registros MX válidos"
    except Exception as e:
        return False, f"Error al verificar el dominio: {str(e)}"

def validar_email_simple(email: str) -> bool:
    """
    Validación simple de email usando regex.
    
    Args:
        email (str): La dirección de email a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))

# Ejemplos de uso
if __name__ == "__main__":
    # Lista de emails para probar
    emails_prueba = [
        "usuario@dominio.com",
        "usuario.nombre@dominio.com",
        "usuario+tag@dominio.com",
        "usuario@dominio.co.uk",
        "usuario@dominio",
        "@dominio.com",
        "usuario@",
        "usuario@@dominio.com",
        "usuario@dominio..com",
        "usuario..nombre@dominio.com",
        "usuario<@dominio.com",
        "",
        "   ",
        "usuario@dominio.com   ",
        "usuario@dominio.com.",
        ".usuario@dominio.com"
    ]
    
    print("=== Validación de Emails ===\n")
    
    for email in emails_prueba:
        es_valido, mensaje = validar_email(email)
        estado = "✅ VÁLIDO" if es_valido else "❌ INVÁLIDO"
        print(f"{estado}: {email}")
        print(f"   Mensaje: {mensaje}")
        print()
    
    print("=== Validación Simple ===")
    for email in emails_prueba:
        es_valido = validar_email_simple(email)
        estado = "✅ VÁLIDO" if es_valido else "❌ INVÁLIDO"
        print(f"{estado}: {email}") 