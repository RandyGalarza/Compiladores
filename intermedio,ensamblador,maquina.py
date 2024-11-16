import tkinter as tk
from tkinter import messagebox
import re

# Definir los operadores
operadores = ['+', '-', '*', '/']

# Expresiones regulares para los literales y patrones
literal_numeric = re.compile(r'^\d+(\.\d+)?$')
identifier_pattern = re.compile(r'^[a-zA-Z_]\w*$')

# Variables para manejo de tokens y errores
tokens_totales = []
current_token_index = 0

# Funciones para trabajar con los tokens
def obtener_token_actual():
    global current_token_index
    if current_token_index < len(tokens_totales):
        return tokens_totales[current_token_index]
    else:
        return None

def consumir_token():
    global current_token_index
    current_token_index += 1

def error(mensaje):
    raise Exception(f"Error de análisis: {mensaje}")

def parse_programa(codigo):
    global tokens_totales
    tokens_totales = re.findall(r"[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]*)?|[+\-*/=]+|[.,;:{}()\[\]]", codigo)
    return parse_sentencia()

def parse_sentencia():
    token = obtener_token_actual()
    if token is None:
        return None
    if literal_numeric.match(token) or token in operadores:
        expresion = parse_expresion()
        return expresion
    elif identifier_pattern.match(token):
        return parse_asignacion()
    else:
        consumir_token()  # Consumir token y continuar

def parse_expresion():
    node = parse_termino()
    while True:
        token = obtener_token_actual()
        if token in operadores:
            operador = token
            consumir_token()
            siguiente_termino = parse_termino()
            if siguiente_termino:
                node = (node, operador, siguiente_termino)
        else:
            break
    return node

def parse_termino():
    node = parse_factor()
    while True:
        token = obtener_token_actual()
        if token in ['*', '/']:
            operador = token
            consumir_token()
            siguiente_factor = parse_factor()
            if siguiente_factor:
                node = (node, operador, siguiente_factor)
        else:
            break
    return node

def parse_factor():
    token = obtener_token_actual()
    if token is None:
        return None
    if literal_numeric.match(token):
        consumir_token()
        return token
    elif identifier_pattern.match(token):
        consumir_token()
        return token
    elif token == '(':
        consumir_token()
        node = parse_expresion()
        if obtener_token_actual() == ')':
            consumir_token()
        return node
    return None

def parse_asignacion():
    variable = obtener_token_actual()
    if identifier_pattern.match(variable):
        consumir_token()
        if obtener_token_actual() != '=':
            error("Se esperaba '=' para la asignación")
        consumir_token()
        expresion = parse_expresion()
        return ('=', variable, expresion)
    return None

# Generación de código intermedio
codigo_tres_direcciones = []

def generar_codigo(nodo, temp_count):
    if nodo is None:
        return None

    if isinstance(nodo, tuple) and nodo[0] == '=':
        variable = nodo[1]
        expresion = generar_codigo(nodo[2], temp_count)
        temp_var = f"t{temp_count}"
        temp_count += 1
        codigo_tres_direcciones.append(f"{temp_var} = {expresion}")
        codigo_tres_direcciones.append(f"{variable} = {temp_var}")
    elif isinstance(nodo, tuple) and len(nodo) == 3:
        left = generar_codigo(nodo[0], temp_count)
        operador = nodo[1]
        right = generar_codigo(nodo[2], temp_count)
        temp_var = f"t{temp_count}"
        temp_count += 1
        codigo_tres_direcciones.append(f"{temp_var} = {left} {operador} {right}")
        return temp_var
    elif isinstance(nodo, str):  # Si es un número o un identificador
        return nodo

# Generación de ensamblador (más cercano al código de máquina)
codigo_ensamblador = []

def generar_ensamblador(codigo_tres_direcciones):
    for instruccion in codigo_tres_direcciones:
        parts = instruccion.split(' ')
        if '=' in parts[1]:  # Asignación
            var = parts[0]
            operando = parts[2]
            codigo_ensamblador.append(f"LOAD {operando}")
            codigo_ensamblador.append(f"STORE {var}")
        else:  # Operación
            var = parts[0]
            left = parts[2]
            operador = parts[3]
            right = parts[4]
            codigo_ensamblador.append(f"LOAD {left}")
            if operador == '+':
                codigo_ensamblador.append(f"ADD {right}")
            elif operador == '-':
                codigo_ensamblador.append(f"SUB {right}")
            elif operador == '*':
                codigo_ensamblador.append(f"MUL {right}")
            elif operador == '/':
                codigo_ensamblador.append(f"DIV {right}")
            codigo_ensamblador.append(f"STORE {var}")

# Generación de código de máquina (simulada como instrucciones binarias)
codigo_maquina = []

def generar_codigo_maquina(codigo_ensamblador):
    for instruccion in codigo_ensamblador:
        if 'LOAD' in instruccion:
            codigo_maquina.append(f"0001 {instruccion.split()[1]}")
        elif 'STORE' in instruccion:
            codigo_maquina.append(f"0010 {instruccion.split()[1]}")
        elif 'ADD' in instruccion:
            codigo_maquina.append(f"0011 {instruccion.split()[1]}")
        elif 'SUB' in instruccion:
            codigo_maquina.append(f"0100 {instruccion.split()[1]}")
        elif 'MUL' in instruccion:
            codigo_maquina.append(f"0101 {instruccion.split()[1]}")
        elif 'DIV' in instruccion:
            codigo_maquina.append(f"0110 {instruccion.split()[1]}")
        else:
            codigo_maquina.append(f"ERROR: Instrucción no válida")

# Función principal
def compilar(codigo):
    # Asegurarse de que el código esté bien escrito
    if codigo.count('(') != codigo.count(')'):
        messagebox.showerror("Error", "Los paréntesis no están balanceados.")
        return
    if codigo.count('"') % 2 != 0:
        messagebox.showerror("Error", "Las comillas no están balanceadas.")
        return

    # Parsear el código fuente
    arbol_sintactico = parse_programa(codigo)

    # Generar código intermedio
    generar_codigo(arbol_sintactico, temp_count=1)

    # Generar ensamblador
    generar_ensamblador(codigo_tres_direcciones)

    # Generar código de máquina
    generar_codigo_maquina(codigo_ensamblador)

    # Mostrar resultados
    resultado = "Código Intermedio (Tres Direcciones):\n"
    resultado += '\n'.join(codigo_tres_direcciones)
    resultado += "\n\nCódigo Ensamblador:\n"
    resultado += '\n'.join(codigo_ensamblador)
    resultado += "\n\nCódigo de Máquina:\n"
    resultado += '\n'.join(codigo_maquina)
    return resultado

# Interfaz gráfica
def mostrar_ventana_resultado(codigo):
    resultado = compilar(codigo)
    
    # Crear una ventana emergente con el resultado
    result_window = tk.Toplevel()
    result_window.title("Resultado de la compilación")
    
    label_resultado = tk.Label(result_window, text=resultado, justify="left")
    label_resultado.pack(padx=10, pady=10)

def mostrar_ventana_codigo():
    # Crear la ventana emergente para ingresar código
    codigo_ventana = tk.Tk()
    codigo_ventana.withdraw()  # Ocultar la ventana principal (evita que se quede abierta)
    
    # Crear un campo de texto para ingresar múltiples líneas
    texto_input = tk.Text(codigo_ventana, height=10, width=50)
    texto_input.pack(padx=10, pady=10)
    
    # Función para detectar el Enter (dos veces)
    def detectar_enter(event):
        if event.keysym == 'Return':  # Si presionamos Enter
            codigo = texto_input.get("1.0", tk.END).strip()
            if codigo:  # Solo si el código no está vacío
                mostrar_ventana_resultado(codigo)  # Mostrar el resultado después de la compilación
    
    # Asociar la detección de la tecla Enter
    texto_input.bind('<Return>', detectar_enter)
    
    # Mostrar la ventana de código
    codigo_ventana.deiconify()
    codigo_ventana.mainloop()

# Iniciar la interfaz de usuario principal
if __name__ == "__main__":
    mostrar_ventana_codigo()
