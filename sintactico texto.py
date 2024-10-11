import re
from anytree import Node, RenderTree

# Definimos los operadores
operadores = {
    '+': 'operador aritmetico',
    '-': 'operador aritmetico',
    '*': 'operador aritmetico',
    '/': 'operador aritmtico',
    '=': 'operador de asignacion',
    'if': 'estructura de control',
    'while': 'estructura de control',
    'for': 'estructura de control'
}

# Expresiones regulares para los literales y patrones
literal_numeric = re.compile(r'^\d+(\.\d+)?$')
identifier_pattern = re.compile(r'^[a-zA-Z_]\w*$')

# Solicitar multiples lineas de codigo
codigo = []
print("Ingrese el codigo a analizar (presiona Enter dos veces para terminar):")
while True:
    linea = input()  
    if linea == "":
        break
    codigo.append(linea)

# Unimos todas las lineas capturadas en un solo texto
codigo = "\n".join(codigo)

# Separar el codigo por lineas
program = codigo.split("\n")

tokens_totales = []

# Analizar linea por linea
for line in program:
    tokens = re.findall(r"[a-zA-Z_]\w*|[0-9]+(?:\.[0-9]*)?|[+\-*/=]+|[.,;:{}()\[\]]", line)
    tokens_totales.extend(tokens)

# Inicio del analisis sintactico
print("\n--- Analisis Sintactico ---\n")
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
    print(f"Error de analisis: {mensaje}")

def auto_insertar_punto_coma():
    print("Advertencia: faltaba ';', se inserto automaticamente.")
    tokens_totales.insert(current_token_index, ';')

def auto_insertar_asignacion():
    print("Advertencia: faltaba '=', se inserto automaticamente.")
    tokens_totales.insert(current_token_index, '=')

def parse_programa():
    nodos = []
    while current_token_index < len(tokens_totales):
        nodo = parse_sentencia()
        if nodo:  # Solo agregamos nodos validos, no None
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
            if siguiente_termino:  # Solo agregamos nodos validos
                node = Node("expresion", children=[node, Node(operador), siguiente_termino])
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
            if siguiente_factor:  # Solo agregamos nodos validos
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
        if expresion:  # Asegurarnos que la expresion no sea None
            return Node("asignacion", children=[Node(variable), expresion])
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

# Prueba de visualizacion del arbol sintactico
try:
    arbol_sintactico = parse_programa()

    # Visualizacion con anytree en texto
    print("\n--- arbol Sintactico ---\n")
    for pre, fill, node in RenderTree(arbol_sintactico):
        print(f"{pre}{node.name}")

except Exception as e:
    print(e)
