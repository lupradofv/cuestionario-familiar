import unicodedata
import re

def extraer_valor(respuesta):
    try:
        return int(respuesta.split(' - ')[0])
    except:
        return respuesta if isinstance(respuesta, int) else 0
    
def invertir_valor(valor, escala_max):
    return (escala_max + 1) - valor if isinstance(valor, int) else valor


def normalizar_texto(texto):
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))  # quita acentos
    texto = re.sub(r"\s+", " ", texto)  # espacios múltiples a uno solo
    return texto

def asociar_id(nombre, apellido, nombre_paciente, apellido_paciente, SHEET_IDMAP):
    # Asegurar encabezados
    if len(SHEET_IDMAP.get_all_records()) == 0:
        SHEET_IDMAP.append_row(["ID", "Nombre Familiar", "Apellido Familiar", "Nombre Paciente", "Apellido Paciente"])

    nombre_clave = f"{normalizar_texto(nombre)}|{normalizar_texto(apellido)}|{normalizar_texto(nombre_paciente)}|{normalizar_texto(apellido_paciente)}"
    idmap = SHEET_IDMAP.get_all_values()[1:]

    for fila in idmap:
        clave_fila = f"{normalizar_texto(fila[1])}|{normalizar_texto(fila[2])}|{normalizar_texto(fila[3])}|{normalizar_texto(fila[4])}"
        if clave_fila == nombre_clave:
            return fila[0]

    nuevo_id = f"P{len(idmap) + 1:03d}"
    SHEET_IDMAP.append_row([nuevo_id, nombre.strip(), apellido.strip(), nombre_paciente.strip(), apellido_paciente.strip()])
    return nuevo_id



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


def procesar_cuestionario(respuestas):

    # 1. DSS-R (revisado)
    respuestas_self = [extraer_valor(r) for r in respuestas['2']]

    indices_IP = [0,9,15,18,22]
    indices_ER = [3,6,12,19,23]
    indices_FO = [5,11,16,21]
    indices_DO = [2,4,8,10,13]
    indices_EC = [1,7,14,17,20,24]

    media_IP = sum(respuestas_self[i] for i in indices_IP) / len(indices_IP)
    media_ER = sum(respuestas_self[i] for i in indices_ER) / len(indices_ER)
    media_FO = sum(respuestas_self[i] for i in indices_FO) / len(indices_FO)
    media_DO = sum(respuestas_self[i] for i in indices_DO) / len(indices_DO)
    media_EC = sum(respuestas_self[i] for i in indices_EC) / len(indices_EC)

    puntuacion_DSSR = (media_IP + (7 - media_ER) + (7 - media_FO) + (7 - media_DO) + (7 - media_EC)) / 5

    # 2. FACES-20Esp (revisado)
    respuestas_faces = [extraer_valor(r) for r in respuestas['3']]
    cohesion = [respuestas_faces[i-1] for i in [1,4,5,8,10,11,13,15,17,19]]
    adaptabilidad = [respuestas_faces[i-1] for i in [2,3,6,7,9,12,14,16,18,20]]
    media_cohesion = sum(cohesion) / len(cohesion)
    media_adaptabilidad = sum(adaptabilidad) / len(adaptabilidad)
    media_faces_total = sum(respuestas_faces) / len(respuestas_faces)

    # 3. AFPEM (Autoestigma) (revisado)
    respuestas_afpem = [extraer_valor(r) for r in respuestas['4']]
    for idx in [0,10,17,25,26,27]:
        respuestas_afpem[idx] = invertir_valor(respuestas_afpem[idx], 5)

    estereotipos = [respuestas_afpem[i-1] for i in [3,9,15,20,25]]
    culpabilidad = [respuestas_afpem[i-1] for i in [4,10,16,21]]
    devaluacion = [respuestas_afpem[i-1] for i in [5,6,11,12,17,22,26,29,30]]
    discriminacion = [respuestas_afpem[i-1] for i in [1,7,13,18,23,27]]
    separacion = [respuestas_afpem[i-1] for i in [2,8,14,19,24,28]]

    media_estereotipos = sum(estereotipos) / len(estereotipos)
    media_culpabilidad = sum(culpabilidad) / len(culpabilidad)
    media_devaluacion = sum(devaluacion) / len(devaluacion)
    media_discriminacion = sum(discriminacion) / len(discriminacion)
    media_separacion = sum(separacion) / len(separacion)

    # 4. PHQ-2 y GAD-2 (revisado)
    respuestas_phq4 = [extraer_valor(r) for r in respuestas['5']]
    ansiedad_valor = sum(respuestas_phq4[0:2])
    depresion_valor = sum(respuestas_phq4[2:4])
    ansiedad = 1 if ansiedad_valor >= 3 else 0
    depresion = 1 if depresion_valor >= 3 else 0

    # 5. WEMWBS – Bienestar Psicológico  (revisado)
    respuestas_wemwbs = [extraer_valor(r) for r in respuestas['6']]
    suma_bienestar = sum(respuestas_wemwbs)
    if suma_bienestar <= 17:
        interpretacion_bienestar = "Bajo"
    elif suma_bienestar <= 27:
        interpretacion_bienestar = "Medio"
    else:
        interpretacion_bienestar = "Alto"

    # 6. SSQ-6 – Satisfacción con Apoyo
    respuestas_ssq6 = [extraer_valor(r) for r in respuestas['7']]
    num_personas_ssq = respuestas.get('7n', [0]*6) 

    media_satisfaccion_ssq = sum(respuestas_ssq6) / len(respuestas_ssq6)
    media_apoyo_ssq = sum(num_personas_ssq) / sum(num_personas_ssq) if sum(num_personas_ssq) > 0 else 0

    # 7. Zarit
    respuestas_zarit = [extraer_valor(r) for r in respuestas['8']]
    for idx in [20,21]:
        respuestas_zarit[idx] = invertir_valor(respuestas_zarit[idx], 5)

    sobrecarga = [respuestas_zarit[i-1] for i in [1,2,3,6,8,9,10,11,12,14,17,22]]
    rechazo = [respuestas_zarit[i-1] for i in [4,5,13,18,19]]
    competencia = [respuestas_zarit[i-1] for i in [7,15,16,20,21]]

    total_zarit = sum(respuestas_zarit)

    if total_zarit <= 46:
        nivel_sobrecarga = "No sobrecarga"
    elif 47 <= total_zarit <= 55:
        nivel_sobrecarga = "Sobrecarga leve"
    else:
        nivel_sobrecarga = "Sobrecarga intensa"

    # 8. HFS – Subescala Perdón a Uno Mismo
    respuestas_hfs = [extraer_valor(r) for r in respuestas['9']]
    for idx in [1, 3, 5]:  # Ítems 2, 4, 6
        respuestas_hfs[idx] = invertir_valor(respuestas_hfs[idx], 7)
    media_hfs = sum(respuestas_hfs) / len(respuestas_hfs)
    if media_hfs < 3:
        interpretacion_hfs = "Baja disposición al perdón hacia uno mismo"
    elif 3 <= media_hfs < 5:
        interpretacion_hfs = "Moderada disposición al perdón hacia uno mismo"
    else:
        interpretacion_hfs = "Alta disposición al perdón hacia uno mismo"

    # GUARDAR RESULTADOS
    resultados = {
        "Puntuación Final DSS-R": round(puntuacion_DSSR,2),

        "Media Cohesión FACES": round(media_cohesion,2),
        "Media Adaptabilidad FACES": round(media_adaptabilidad,2),
        "Puntuación Total FACES": round(media_faces_total,2),

        "Estereotipos AFPEM": round(media_estereotipos,2),
        "Culpabilidad AFPEM": round(media_culpabilidad,2),
        "Devaluación AFPEM": round(media_devaluacion,2),
        "Discriminación AFPEM": round(media_discriminacion,2),
        "Separación AFPEM": round(media_separacion,2),

        "PHQ-2 Ansiedad": ansiedad_valor,
        "PHQ-2 Clasificación": "Positivo" if ansiedad else "Negativo",
        "GAD-2 Depresión": depresion_valor,
        "GAD-2 Clasificación": "Positivo" if depresion else "Negativo",

        "Bienestar Psicológico WEMWBS": suma_bienestar,
        "Interpretación Bienestar": interpretacion_bienestar,

        "Media Satisfacción SSQ-6": round(media_satisfaccion_ssq,2),
        "Media Apoyo SSQ-6": round(media_apoyo_ssq,2),

        "Sobrecarga Zarit": round(sum(sobrecarga),2),
        "Rechazo Zarit": round(sum(rechazo),2),
        "Competencia Zarit": round(sum(competencia),2),
        "Total Zarit": total_zarit,
        "Nivel Sobrecarga Zarit": nivel_sobrecarga,

        "Media HFS": round(media_hfs,2),
        "Interpretación HFS": interpretacion_hfs
    }
    print("Resultados procesados:", resultados)

    return resultados

