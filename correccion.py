import datetime
import pandas as pd

from utils import extraer_valor, invertir_valor

def procesar_cuestionario(respuestas):

    # 1. DSS-R
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

    # 2. FACES-20Esp
    respuestas_faces = [extraer_valor(r) for r in respuestas['3']]
    cohesion = [respuestas_faces[i-1] for i in [1,4,5,8,10,11,13,15,17,19]]
    adaptabilidad = [respuestas_faces[i-1] for i in [2,3,6,7,9,12,14,16,18,20]]
    media_cohesion = sum(cohesion) / len(cohesion)
    media_adaptabilidad = sum(adaptabilidad) / len(adaptabilidad)
    media_faces_total = sum(respuestas_faces) / len(respuestas_faces)

    # 3. AFPEM (Autoestigma)
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

    # 4. PHQ-2 y GAD-2
    respuestas_phq4 = [extraer_valor(r) for r in respuestas['5']]
    ansiedad = sum(respuestas_phq4[0:2])
    depresion = sum(respuestas_phq4[2:4])

    # 5. Zarit
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
        "PHQ-2 Ansiedad": ansiedad,
        "GAD-2 Depresión": depresion,
        "Total Zarit": total_zarit,
        "Nivel Sobrecarga Zarit": nivel_sobrecarga
    }
    print("Resultados procesados:", resultados)

    return resultados

