import re

print()
print("/--------Analisador Lexico------/")
print()

# Operadores
operadores = {
    '+': 'operador aritmetico',
    '-': 'operador aritmetico',
    '*': 'operador aritmetico',
    '/': 'operador aritmetico',
    '%': 'operador aritmetico',
    '=': 'operador de asignacion',
    '==': 'operador relacional',
    '!=': 'operador relacional',
    '<': 'operador relacional',
    '>': 'operador relacional',
    '<=': 'operador relacional',
    '>=': 'operador relacional',
    '&&': 'operador logico',
    '||': 'operador logico',
    '!': 'operador logico'
}

# Delimitadores
delimitadores = {
    '(': 'parentesis',
    ')': 'parentesis',
    '{': 'llave',
    '}': 'llave',
    '[': 'corchete',
    ']': 'corchete',
    ';': 'punto y coma',
    ',': 'coma',
    ':': 'dos puntos'  
}

# Palabras clave
keywords = {
    'if': 'keyword',
    'else': 'keyword',
    'while': 'keyword',
    'for': 'keyword',
    'return': 'keyword'
}

# Expresiones regulares para los literales y patrones
literal_numeric = re.compile(r'^\d+(\.\d+)?$')
literal_string = re.compile(r'^[\'\"].*[\'\"]$')
literal_boolean = {'True': 'literal booleano', 'False': 'literal booleano'}
literal_null = {'null': 'literal nulo', 'None': 'literal nulo'}
identifier_pattern = re.compile(r'^[a-zA-Z_]\w*$')
comment_single_line = re.compile(r'^(//|#).*')
comment_multi_line = re.compile(r'/\*[\s\S]*?\*/')
separator_pattern = re.compile(r'\s+')

# Solicitar múltiples líneas de código hasta que el usuario ingrese una línea vacía
codigo = []
print("Ingrese el código a analizar (presiona Enter dos veces para terminar):")
while True:
    linea = input()  # Captura cada línea
    if linea == "":  # Termina la entrada si se ingresa una línea vacía
        break
    codigo.append(linea)

# Unimos todas las líneas capturadas en un solo texto
codigo = "\n".join(codigo)

# Remover comentarios multilínea
codigo = re.sub(comment_multi_line, '', codigo)

# Separar el código por líneas
program = codigo.split("\n")

count = 0
empty_line_count = 0  # Contador de líneas vacías consecutivas

# Analizar línea por línea
for line in program:
    count += 1
    # Si la línea está vacía, incrementamos el contador de líneas vacías
    if line.strip() == "":
        empty_line_count += 1
    else:
        empty_line_count = 0  # Reiniciar si encontramos una línea no vacía
    
    # Si hay dos líneas vacías consecutivas, detener el análisis
    if empty_line_count >= 2:
        print("Finalizando análisis.")
        break

    print(f"line #{count} \n{line}")
    tokens = re.findall(r"[a-zA-Z_]\w*|//.*|#.*|[0-9]+(?:\.[0-9]*)?|[.,;:{}()\[\]]|[+\-*/%<>=!&|]+|\".*?\"|'.*?'|\S", line)
    print("Los tokens son:", tokens)
    print(f"Line #{count} Propiedades \n")

    # Conjunto para almacenar tokens ya procesados en la línea
    tokens_procesados = set()

    for token in tokens:
        # Evitar procesar el mismo token más de una vez por línea
        if token in tokens_procesados:
            continue
        
        tokens_procesados.add(token)

        if token in operadores:
            print(f"Token: '{token}' -> Categoria: Operador, Tipo: {operadores[token]}")
        elif token in delimitadores:
            print(f"Token: '{token}' -> Categoria: Delimitador, Tipo: {delimitadores[token]}")
        elif token in keywords:
            print(f"Token: '{token}' -> Categoria: Palabra clave")
        elif token in literal_boolean:
            print(f"Token: '{token}' -> Categoria: Literal, Tipo: {literal_boolean[token]}")
        elif token in literal_null:
            print(f"Token: '{token}' -> Categoria: Literal, Tipo: {literal_null[token]}")
        elif literal_numeric.match(token):
            print(f"Token: '{token}' -> Categoria: Literal, Tipo: Literal numerico")
        elif literal_string.match(token):
            print(f"Token: '{token}' -> Categoria: Literal, Tipo: Literal de cadena")
        elif identifier_pattern.match(token):
            print(f"Token: '{token}' -> Categoria: Identificador")
        elif comment_single_line.match(token):
            print(f"Token: '{token}' -> Categoria: Comentario")
        elif separator_pattern.match(token):
            print(f"Token: '{token}' -> Categoria: Separador")
        else:
            print(f"Token: '{token}' -> Categoria: Desconocido")
    
    print("=====================================")
