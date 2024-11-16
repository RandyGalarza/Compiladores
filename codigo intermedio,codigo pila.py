import re
from anytree import Node, RenderTree

# Definimos los operadores
operadores = {
    '+': 'operador aritmetico',
    '-': 'operador aritmetico',
    '*': 'operador aritmetico',
    '/': 'operador aritmetico',
    '=': 'operador de asignacion',
    'if': 'estructura de control',
    'while': 'estructura de control',
    'for': 'estructura de control'
}

# Expresiones regulares para los literales y patrones
literal_numeric = re.compile(r'^\d+(\.\d+)?$')
identifier_pattern = re.compile(r'^[a-zA-Z_]\w*$')

# Solicitar múltiples líneas de código
codigo = []
print("Ingrese el código a analizar (presiona Enter dos veces para terminar):")
while True:
    linea = input()  
    if linea == "":
        break
    codigo.append(linea)

# Unimos todas las líneas capturadas en un solo texto
codigo = "\n".join(codigo)

# Separar el código por líneas
program = codigo.split("\n")

tokens_totales = []

# Analizar línea por línea
for line in program:
    tokens = re.findall(r"[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]*)?|[+\-*/=]+|[.,;:{}()\[\]]", line)
    tokens_totales.extend(tokens)

# Inicio del análisis sintáctico
print("\n--- Análisis Sintáctico ---\n")
current_token_index = 0

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
    print(f"Error de análisis: {mensaje}")

def auto_insertar_punto_coma():
    print("Advertencia: faltaba ';', se insertó automáticamente.")
    tokens_totales.insert(current_token_index, ';')

def auto_insertar_asignacion():
    print("Advertencia: faltaba '=', se insertó automáticamente.")
    tokens_totales.insert(current_token_index, '=')

def parse_programa():
    nodos = []
    while current_token_index < len(tokens_totales):
        nodo = parse_sentencia()
        if nodo:  # Solo agregamos nodos válidos, no None
            nodos.append(nodo)
    return Node("programa", children=nodos)

def parse_bloque():
    sentencias = []
    consumir_token()  # Consumir la llave de apertura '{'
    while obtener_token_actual() != '}':
        if obtener_token_actual() is None:
            error("Se esperaba '}'")
            break
        sentencia = parse_sentencia()
        if sentencia:
            sentencias.append(sentencia)
    consumir_token()  # Consumir la llave de cierre '}'
    return Node("bloque", children=sentencias) if sentencias else None

def parse_expresion():
    node = parse_termino()
    while True:
        token = obtener_token_actual()
        if token in ['+', '-']:
            operador = token
            consumir_token()
            siguiente_termino = parse_termino()
            if siguiente_termino:  # Solo agregamos nodos válidos
                node = Node("expresión", children=[node, Node(operador), siguiente_termino])
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
            if siguiente_factor:  # Solo agregamos nodos válidos
                node = Node("término", children=[node, Node(operador), siguiente_factor])
        else:
            break
    return node

def parse_factor():
    token = obtener_token_actual()
    if token is None:
        return None
    if literal_numeric.match(token):
        consumir_token()
        return Node("número", children=[Node(token)])
    elif token == '(':
        consumir_token()
        node = parse_expresion()
        if obtener_token_actual() == ')':
            consumir_token()
        return node
    elif identifier_pattern.match(token):
        consumir_token()
        return Node("identificador", children=[Node(token)])
    elif token in operadores.keys():
        consumir_token()
        return Node("operador", children=[Node(token)])
    return None

def parse_sentencia():
    token = obtener_token_actual()
    if token is None:
        return None
    if literal_numeric.match(token) or token in ['+', '-', '*', '/']:
        expresion = parse_expresion()
        if obtener_token_actual() != ';':
            auto_insertar_punto_coma()
        consumir_token()
        return expresion
    elif identifier_pattern.match(token):
        return parse_asignacion()
    elif token == 'if':
        return parse_if()
    elif token == 'while':
        return parse_while()
    elif token == 'for':
        return parse_for()
    elif token == '{':
        return parse_bloque()
    elif token == ';':
        consumir_token()
        return None
    else:
        consumir_token()  # Consumir token y continuar

def parse_asignacion():
    variable = obtener_token_actual()
    if identifier_pattern.match(variable):
        consumir_token()
        if obtener_token_actual() != '=':
            auto_insertar_asignacion()
        consumir_token()
        expresion = parse_expresion()
        if obtener_token_actual() != ';':
            auto_insertar_punto_coma()
        consumir_token()
        if expresion:  # Asegurarnos que la expresión no sea None
            return Node("asignación", children=[Node(variable), expresion])
    return None

def parse_if():
    consumir_token()  # Consumir 'if'
    if obtener_token_actual() == '(':
        consumir_token()  # Consumir '('
        condicion = parse_expresion()
        if obtener_token_actual() == ')':
            consumir_token()  # Consumir ')'
            cuerpo = parse_bloque()
            if cuerpo:
                return Node("if", children=[condicion, cuerpo])
    return None

def parse_while():
    consumir_token()  # Consumir 'while'
    if obtener_token_actual() == '(':
        consumir_token()  # Consumir '('
        condicion = parse_expresion()
        if obtener_token_actual() == ')':
            consumir_token()  # Consumir ')'
            cuerpo = parse_bloque()
            if cuerpo:
                return Node("while", children=[condicion, cuerpo])
    return None

def parse_for():
    consumir_token()  # Consumir 'for'
    if obtener_token_actual() == '(':
        consumir_token()  # Consumir '('
        inicializacion = parse_asignacion()
        condicion = parse_expresion()
        actualizacion = parse_asignacion()
        if obtener_token_actual() == ')':
            consumir_token()  # Consumir ')'
            cuerpo = parse_bloque()
            if cuerpo:
                return Node("for", children=[inicializacion, condicion, actualizacion, cuerpo])
    return None

# Generación de código en tres direcciones y en pila
codigo_pila = []
codigo_tres_direcciones = []

def generar_codigo(nodo, temp_count, tipo_codigo="tres_direcciones"):
    if nodo is None:
        return None

    if nodo.name == "asignación":
        # Asignación: variable = expresión
        variable = nodo.children[0].name
        expresion = generar_codigo(nodo.children[1], temp_count, tipo_codigo)
        if tipo_codigo == "tres_direcciones":
            temp_var = f"t{temp_count}"
            temp_count += 1
            # Código de tres direcciones para la asignación
            codigo_tres_direcciones.append(f"{temp_var} = {expresion}")
            codigo_tres_direcciones.append(f"{variable} = {temp_var}")
        elif tipo_codigo == "pila":
            # Operación de pila para asignación
            print(f"Código en pila para: {variable} = {expresion}")
            codigo_pila.append(f"push {expresion}")
            codigo_pila.append(f"pop {variable}")
    elif nodo.name == "expresión" or nodo.name == "término":
        # Operaciones de suma o resta: t1 = left operador right
        left = generar_codigo(nodo.children[0], temp_count, tipo_codigo)
        operador = nodo.children[1].name
        right = generar_codigo(nodo.children[2], temp_count, tipo_codigo)
        temp_var = f"t{temp_count}"
        temp_count += 1
        if tipo_codigo == "tres_direcciones":
            # Código de tres direcciones para operaciones aritméticas
            codigo_tres_direcciones.append(f"{temp_var} = {left} {operador} {right}")
        elif tipo_codigo == "pila":
            # Código de pila para operaciones aritméticas
            codigo_pila.append(f"push {left}")
            codigo_pila.append(f"push {right}")
            if operador == "+":
                codigo_pila.append("add")
            elif operador == "-":
                codigo_pila.append("sub")
            elif operador == "*":
                codigo_pila.append("mul")
            elif operador == "/":
                codigo_pila.append("div")
            codigo_pila.append(f"pop {temp_var}")
        return temp_var
    return nodo.name

# Ejecutar análisis y generación de código
arbol_sintactico = parse_programa()

# Imprimir el árbol sintáctico
print("\n--- Árbol Sintáctico ---\n")
for pre, _, node in RenderTree(arbol_sintactico):
    print(f"{pre}{node.name}")

# Generar el código en tres direcciones
print("\n--- Código Intermedio (Tres Direcciones) ---\n")
temp_count = 1
for instruccion in arbol_sintactico.children:
    generar_codigo(instruccion, temp_count, tipo_codigo="tres_direcciones")

for instruccion in codigo_tres_direcciones:
    print(instruccion)

# Generar el código en pila
print("\n--- Código en Pila ---\n")
temp_count = 1
for instruccion in arbol_sintactico.children:
    generar_codigo(instruccion, temp_count, tipo_codigo="pila")

for instruccion in codigo_pila:
    print(instruccion)
