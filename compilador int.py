import tkinter as tk 
from tkinter import messagebox
import re
import threading

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
    # Eliminar los espacios en blanco y saltos de línea innecesarios antes de tokenizar
    codigo_sin_espacios = ''.join(codigo.split())
    tokens_totales = re.findall(r"[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]*)?|[+\-*/=]+|[.,;:{}()\[\]]", codigo_sin_espacios)
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

# Función para simular la ejecución 
def simular_ejecucion(codigo):
    try:
        local_vars = {}
        exec(codigo, {}, local_vars)  # Ejecutar el código en un espacio controlado
        return local_vars  # Devolver las variables locales generadas
    except Exception as e:
        return f"Error de ejecución: {str(e)}"

# Función principal de compilación
def compilar(codigo):
    global codigo_tres_direcciones
    codigo_tres_direcciones.clear() # Limpiar la lista antes de cada compilación
    if codigo.count('(') != codigo.count(')'):
        return "Error: Los paréntesis no están balanceados."
    if codigo.count('"') % 2 != 0:
        return "Error: Las comillas no están balanceadas."
    
    arbol_sintactico = parse_programa(codigo)
    generar_codigo(arbol_sintactico, temp_count=1)
    
    variables_resultado = simular_ejecucion(codigo)

    resultado = "Compilación exitosa.\nResultado final:\n"
    if isinstance(variables_resultado, dict):
        salida_resultado = []
        for var, valor in variables_resultado.items():
            if var == 'print':
                salida_resultado.append(valor)
        if salida_resultado:
            resultado += "\n".join(map(str, salida_resultado))
        else:
            resultado += str(list(variables_resultado.values())[-1])
    else:
        resultado = variables_resultado  # Si hubo error de ejecución, mostrar el error.
    
    return resultado

# Función para ejecutar en un hilo separado
def compilar_en_hilo(codigo, label_resultado):
    resultado = compilar(codigo)
    label_resultado['text'] = resultado  # Actualizar el texto de la etiqueta sin acumularlo

# Crear la interfaz gráfica
def crear_interfaz():
    ventana = tk.Tk()
    ventana.title("Compilador Básico de Python")
    ventana.configure(bg='black')

    # Área de texto para ingresar código
    texto_input = tk.Text(ventana, height=15, width=50, bg='black', fg='white', insertbackground='white')
    texto_input.pack(padx=10, pady=10)

    # Etiqueta para mostrar los resultados de la compilación
    label_resultado = tk.Label(ventana, text="Uniguajira", justify="left", bg='black', fg='white')
    label_resultado.pack(padx=10, pady=10)

    # Función para manejar el botón de compilación
    def compilar_codigo():
        codigo = texto_input.get("1.0", "end-1c")
        if codigo:
            threading.Thread(target=compilar_en_hilo, args=(codigo, label_resultado)).start()

    # Botón para compilar
    boton_compilar = tk.Button(ventana, text="Compilar", command=compilar_codigo, bg='gray', fg='white')
    boton_compilar.pack(pady=10)

    ventana.mainloop()

# Ejecutar la interfaz gráfica
crear_interfaz()
