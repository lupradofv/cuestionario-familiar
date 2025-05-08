def extraer_valor(respuesta):
    try:
        return int(respuesta.split(' - ')[0])
    except:
        return respuesta if isinstance(respuesta, int) else 0
    
def invertir_valor(valor, escala_max):
    return (escala_max + 1) - valor if isinstance(valor, int) else valor

def asociar_id(nombre, apellido, SHEET_IDMAP):
    # Buscar si ya existe ese participante en la hoja de correspondencia
    id_participante = None
    nombre_clave = f"{nombre.strip().lower()}|{apellido.strip().lower()}"

    idmap = SHEET_IDMAP.get_all_values()[1:]  # Saltamos encabezado
    for fila in idmap:
        clave_fila = f"{fila[1].strip().lower()}|{fila[2].strip().lower()}"
        if clave_fila == nombre_clave:
            id_participante = fila[0]
            break

    # Si no existe, generar uno nuevo y registrar en hoja de correspondencia
    if not id_participante:
        num_registros = len(idmap) + 1
        id_participante = f"P{num_registros:03d}"
        SHEET_IDMAP.append_row([id_participante, nombre.strip(), apellido.strip()])

    return id_participante

def comprobar_respuestas_funciona(respuestas):
    incompletos = {}
    for bloque, contenido in respuestas.items():
        if isinstance(contenido, dict):
            if any(r in ["", None] for r in contenido.values()):
                incompletos.append(bloque)
        elif isinstance(contenido, list):
            if any(r in ["", None] for r in contenido):
                incompletos.append(bloque)

    return incompletos

def comprobar_respuestas(respuestas):
    incompletos = {}

    for bloque, contenido in respuestas.items():
        if isinstance(contenido, dict):
            faltantes = [campo for campo, valor in contenido.items() if valor in ["", None]]
            if faltantes:
                incompletos[bloque] = faltantes
        elif isinstance(contenido, list):
            faltantes = [i + 1 for i, valor in enumerate(contenido) if valor in ["", None]]
            if faltantes:
                incompletos[bloque] = faltantes

    return incompletos