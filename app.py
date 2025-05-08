import streamlit as st
import pandas as pd
import datetime
import os
import json

from correccion import procesar_cuestionario
from utils import asociar_id
# Si vas a usar Google Sheets
USE_GOOGLE_SHEETS = True  
COLUMNS_GOOGLE_SHEET = [
    # Datos sociodemográficos
    "Fecha", "Idioma", "ID", "Género", "Edad", "País", "Ciudad",
    "Estado civil", "Estado laboral", "Ingresos anuales", "Nivel de estudios",
    "Nombre paciente", "Apellido paciente", "Centro de atención", "Convive con paciente",
    "Relación", "Relación antes enfermedad", "Relación ahora enfermedad", "Última visita centro",
    "Dificultades asistencia",
    
    # Resultados de escalas
    "Puntuación Final DSS-R",
    "Media Cohesión FACES", "Media Adaptabilidad FACES", "Puntuación Total FACES",
    "Estereotipos AFPEM", "Culpabilidad AFPEM", "Devaluación AFPEM", "Discriminación AFPEM", "Separación AFPEM",
    "PHQ-2 Ansiedad", "GAD-2 Depresión",
    "Total Zarit", "Nivel Sobrecarga Zarit"
]


if USE_GOOGLE_SHEETS:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    CREDS = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    CLIENT = gspread.authorize(CREDS)
    SHEET = CLIENT.open("Respuestas Cuestionario IA").worksheet("Respuestas")
    SHEET_IDMAP = CLIENT.open("Respuestas Cuestionario IA").worksheet("Correspondencia")


st.set_page_config(page_title="Cuestionario Familiar", page_icon="🧠")

# Idioma
idioma = st.radio("Elige el idioma / Choose your language", ["Español", "English"])

def t(texto_esp, texto_eng):
    return texto_esp if idioma == "Español" else texto_eng

st.title(t("🧠 Cuestionario para Familiares - Salud Mental", "🧠 Family Mental Health Questionnaire"))

st.info(t(
    "📝 Este cuestionario forma parte de un estudio que busca comprender mejor las necesidades de los familiares de personas con problemas de salud mental y su relación con el tratamiento. Su participación es voluntaria y puede retirarse en cualquier momento. La evaluación dura entre 30 y 45 minutos.",
    "📝 This questionnaire is part of a study aiming to better understand the needs of family members of people with mental health issues and their involvement in treatment. Participation is voluntary and you may withdraw at any time. The assessment lasts approximately 30–45 minutes."
))

# Consentimiento informado
consentimiento = st.checkbox(t(
    "He leído la información y acepto participar voluntariamente.",
    "I have read the information and voluntarily agree to participate."
))

if consentimiento:
    with st.form("cuestionario"):
        st.write(t("Por favor, responde las siguientes preguntas...", "Please answer the following questions..."))

        ########################################################################
        # 1. Datos Sociodemográficos
        ########################################################################
        st.header(t("📚 Comencemos con algunas preguntas iniciales.", "📚 Let's start with some initial questions."))
        nombre_familiar = st.text_input(t("Nombre", "Full name"))
        apellido_familiar = st.text_input(t("Apellido", "Last name"))

        opciones_genero_es = ["", "Hombre", "Mujer", "Otro"]
        opciones_genero_en = ["", "Male", "Female", "Other"]
        genero = st.selectbox(t("Género", "Gender"), opciones_genero_es if idioma == "Español" else opciones_genero_en)
        edad = st.number_input(t("Edad", "Age"), 10, 100)
        pais = st.text_input(t("País", "Country"))
        ciudad = st.text_input(t("Ciudad", "City"))
        opciones_estado_civil_es = ["", "Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Separado/a", "Pareja de hecho"]
        opciones_estado_civil_en = ["", "Single", "Married", "Divorced", "Widowed", "Separated", "Common-law partner"]
        estado_civil = st.selectbox(
            t("Estado civil", "Marital status"),
            opciones_estado_civil_es if idioma == "Español" else opciones_estado_civil_en
        )
        
        opciones_estado_labora_es = ["", "Trabajando/a", "Jubilado/a", "Nunca he trabajado", "Desempleado/a", "Incapacidad laboral"]
        opciones_estado_labora_en = ["", "Working", "Retired", "Never worked", "Unemployed", "Disability"]
        estado_labora = st.selectbox(
            t("Estado laboral", "Employment status"),
            opciones_estado_labora_es if idioma == "Español" else opciones_estado_labora_en
        )

        ingresos_anuales = st.selectbox(
            t("Ingresos anuales", "Annual income"), 
            ["", "Menos de 10.000€", "10.000-20.000€", "20.000-30.000€", "Más de 30.000€"] if idioma == "Español" else
            ["", "Less than €10,000", "€10,000-20,000", "€20,000-30,000", "More than €30,000"]
        )
        
        opciones_nivel_estudios_es = ["", "Sin estudios", "Primaria (lectura y escritura)", "Secundaria (FP, ESO, BUP, Bachillerato, COU)", "Superior (Licenciatura/ Grado)"]
        opciones_nivel_estudios_en = ["", "No studies", "Primary (reading and writing)", "Secondary (Vocational Training, ESO, BUP, Baccalaureate, COU)", "Higher (Degree)"]
        nivel_estudios = st.selectbox(
            t("Nivel de estudios", "Level of education"),
            opciones_nivel_estudios_es if idioma == "Español" else opciones_nivel_estudios_en
        )

        respuestas_0 = {
            "Nombre": nombre_familiar,
            "Apellido": apellido_familiar,
            "Género": genero,
            "Edad": edad,
            "País": pais,
            "Ciudad": ciudad,
            "Estado civil": estado_civil,
            "Estado laboral": estado_labora,
            "Ingresos anuales": ingresos_anuales,
            "Nivel de estudios": nivel_estudios
        }

        ########################################################################
        # 2. Relación Familiar
        ########################################################################
        st.markdown(t("## 👨‍👩‍👦 Bloque 1",
                    "## 👨‍👩‍👦 Block 1"))
        nombre_paciente = st.text_input(t("Nombre del paciente", "Patient's full name"))
        apellido_paciente = st.text_input(t("Apellido del paciente", "Patient's last name"))
        centro = st.text_input(t("Centro de atención", "Care center"))

        si_no_es = ["Sí", "No"]
        si_no_en = ["Yes", "No"]
        convivencia = st.radio(
            t("¿Convive con su familiar?", "Do you live with the patient?"), 
            si_no_es if idioma == "Español" else si_no_en
        )

        relacion = st.text_input(
            t("¿Qué relación tiene con el paciente? (madre, pareja...)", "What is your relationship with the patient? (mother, partner...)")
        )

        relacion_antes = st.selectbox(
            t("Relación antes de la enfermedad", "Relationship before the illness"),
            ["", "Problemática", "Distante", "Normal", "De gran intimidad", "Otra"]
        )
        relacion_ahora = st.selectbox(
            t("Relación ahora", "Relationship now"),
            ["", "Problemática", "Distante", "Normal", "De gran intimidad", "Otra"]
        )
        opciones_ultima_visita_es = ["", "Menos de 1 mes", "1-3 meses", "3-6 meses", "6-12 meses", "Más de 1 año"]
        opciones_ultima_visita_en = ["", "Less than 1 month", "1-3 months", "3-6 months", "6-12 months", "More than 1 year"]
        ultima_visita = st.selectbox(
            t("Última visita al centro del paciente", "Last visit to the patient's center"),
            opciones_ultima_visita_es if idioma == "Español" else opciones_ultima_visita_en
        )
        
        opciones_dificultad_es = [
            "Problemas económicos", "Distancia", "Falta de tiempo", "Cuido de otra persona", 
            "Me cuesta generar la rutina para ir al grupo", "No me han ofrecido intervención grupal",
            "No me dan citas aunque las pido", "No me siento cómoda en las citas",
            "No comparto la visión de los terapeutas", "No me siento escuchada",
            "Mi familiar no quiere que vaya", "Estoy mal psicológicamente", "Otra razón"
        ]
        opciones_dificultad_en = [
            "Economic problems", "Distance", "Lack of time", "Caregiver of another person",
            "Hard to generate the routine to go", "Not offered group intervention",
            "No appointments given despite requesting", "Feel uncomfortable emotionally",
            "Don't share therapists' vision", "Don't feel heard",
            "Family member does not want me to go", "Mentally unwell", "Other reason"
        ]
        
        dificultad = st.multiselect(
            t("Razones por las que cuesta ir a cita o grupo", "Reasons why it is difficult to attend appointments or group"),
            opciones_dificultad_es if idioma == "Español" else opciones_dificultad_en
        )

        st.write(t("Si seleccionó 'Otra razón', descríbala aquí:", "If you selected 'Other reason', describe it here:"))
        otra_dificultad = st.text_area(t("Otra dificultad", "Other difficulty"))
        if otra_dificultad:
            dificultad.append(otra_dificultad)


        respuestas_1 = {
            "Nombre paciente": nombre_paciente,
            "Apellido paciente": apellido_paciente,
            "Centro de atención": centro,
            "Convive con paciente": convivencia,
            "Relación": relacion,
            "Relación antes enfermedad": relacion_antes,
            "Relación ahora enfermedad": relacion_ahora,
            "Última visita centro": ultima_visita,
            "Dificultades asistencia": ", ".join(dificultad)
        }

        # Barra de progreso de avance 📈
        st.progress(15, text=t("⏳ Has completado aproximadamente el 15% del cuestionario",
                               "⏳ You've completed approximately 15% of the questionnaire"))
        
        st.divider()
        st.markdown(t("### 👨‍👩‍👧‍👦 ¡Ahora continuamos! Más preguntas sobre ti y tu familia.", 
                    "### 👨‍👩‍👧‍👦 Let's continue! More questions about you and your family."))

        ##############################################################################################################
        # Diferenciación del Self (Escala de 1-6) 🙇‍♀️🙇
        ##############################################################################################################
        st.markdown(t("## 🙇 Bloque 2", 
                    "## 🙇 Block 2"))
        st.write(t(
            "A continuación, encontrarás unas preguntas acerca de ti y de tus relaciones con los demás. Por favor, lee cuidadosamente cada pregunta y decide qué respuesta se corresponde con tu situación. Todas las respuestas son correctas; lo importante es que reflejen tu situación y tu experiencia.", 
            "Next, you will find some questions about yourself and your relationships with others. Please read each question carefully and decide which answer corresponds to your situation. All answers are correct; the important thing is that they reflect your situation and your experience."
        ))
    
        opciones_diferenciacion = [
            "1 - Muy en desacuerdo", "2 - En desacuerdo", "3 - Más bien en desacuerdo",
            "4 - Más bien de acuerdo", "5 - De acuerdo", "6 - Muy de acuerdo"
        ] if idioma == "Español" else [
            "1 - Strongly disagree", "2 - Disagree", "3 - Somewhat disagree",
            "4 - Somewhat agree", "5 - Agree", "6 - Strongly agree"
        ]

        preguntas_self = [
            t("Tiendo a permanecer fiel a mis ideas incluso en situaciones de tensión", 
              "I tend to remain true to my ideas even in tense situations"),
            t("A menudo me siento inhibido/a cuando estoy con mi familia", 
              "I often feel inhibited around my family"),
            t("Tiendo a hacer que mis padres/parejas hagan lo que yo quiero", 
              "I tend to make my parents/partners do what I want"),
            t("En ocasiones, mis sentimientos me desbordan y no me dejan pensar con claridad", 
              "Sometimes my feelings overwhelm me and prevent me from thinking clearly"),
            t("Suelo tratar de imponer mis ideas y deseos a los demás", 
              "I tend to impose my ideas and wishes on others"),
            t("Con frecuencia, me muestro de acuerdo con los demás para evitar disgustarles", 
              "I often agree with others to avoid upsetting them"),
            t("A veces me siento como si estuviera en una montaña rusa emocional", 
              "Sometimes I feel like I'm on an emotional roller coaster"),
            t("Siempre evitaré recurrir a alguien de mi familia en busca de apoyo emocional", 
              "I always avoid seeking emotional support from my family"),
            t("Tiendo a presionar a los demás para pensar y hacer las cosas a mi manera", 
              "I tend to pressure others to think and act my way"),
            t("Distingo mis pensamientos y sentimientos de los de los demás con facilidad", 
              "I easily distinguish my own thoughts and feelings from those of others"),
            t("Me gusta salirme siempre con la mía",
              "I always like to get my way"),
            t("Mis decisiones se ven influidas fácilmente por la presión de los demás",
              "My decisions are easily influenced by the pressure of others"),
            t("Se me hiere con mucha facilidad",
              "I am easily hurt"),
            t("Me molesto cuando los demás no piensan como yo",
              "I get upset when others don't think like me"),
            t("Cuando estoy con mi familia o con mi pareja, a menudo me siento reprimido/a",
              "When I'm with my family or partner, I often feel repressed"),
            t("Puedo juzgar por mí mismo/a si hago o no hago bien las cosas",
              "I can judge for myself whether I do things right or wrong"),
            t("En ocasiones, cambio mis opiniones para evitar discusiones con los demás",
              "Sometimes I change my opinions to avoid arguments with others"),
            t("Siento como si entre mis familiares y yo se hubiera roto el vínculo",
              "I feel like the bond between my family and me has broken"),
            t("Tengo un conjunto de valores y creencias bien definido",
              "I have a well-defined set of values and beliefs"),
            t("Me afectan las cosas de forma mucho más intensa que a los demás",
              "Things affect me much more intensely than others"),
            t("Evito contarle a la gente mis problemas",
              "I avoid telling people my problems"),
            t("Tiendo a evitar discrepar, para que los demás no se molesten",
              "I tend to avoid disagreeing so that others are not upset"),
            t("Tengo claro quién soy, lo que creo, lo que defiendo, y lo que haré o no haré",
              "I am clear about who I am, what I believe, what I stand for, and what I will or will not do"),
            t("A menudo sufro altibajos emocionales",
              "I often suffer emotional ups and downs"),
            t("La gente a la que quiero no conoce mis verdaderos pensamientos ni sentimientos sobre algunas cosas",
              "The people I love do not know my true thoughts or feelings about some things")
        ]

        respuestas_2 = []
        
        for i, pregunta in enumerate(preguntas_self, 1):
          respuestas_2.append(st.radio(f"**{i}. {pregunta}**", opciones_diferenciacion, key=f"self_{i}"))

        # Barra de progreso de avance 📈
        st.progress(35, 
                    text= t("⏳ ¡Ya has completado el 35% del cuestionario!",
                    "⏳ You've completed 35% of the questionnaire!"))
        
        st.divider()
        st.markdown(t("### 🌟 ¡Buen trabajo! Vamos a seguir...",
                    "### 🌟 Good job! Let's continue..."))

        ##############################################################################################################
        # Funcionamiento Familiar (Escala de 1-5) 🏠💬
        ##############################################################################################################
        st.markdown(t("## 🏠 Bloque 3", 
                      "## 🏠 Block 3"))
        st.write(t(
            "Valora cómo describen tu familia estas afirmaciones:",
            "Rate how these statements describe your family:"
        ))

        opciones_funcionamiento = [
            "1 - Nunca", "2 - Casi nunca", "3 - A veces", "4 - Casi siempre", "5 - Siempre"
        ] if idioma == "Español" else [
            "1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Always"
        ]

        
        preguntas_funcionamiento = [
            t("Los miembros de la familia se sienten muy cercanos unos a otros", 
              "Family members feel very close to each other"),
            t("Cuando hay que resolver problemas, se siguen las propuestas de los hijos", 
              "When problems arise, children's proposals are followed"),
            t("La disciplina en casa es justa (normas, consecuencias, castigos)", 
              "Discipline at home is fair (rules, consequences, punishments)"),
            t("Se asumen las decisiones que se toman juntos en familia", 
                "Decisions made together as a family are accepted"),
            t("Los miembros de la familia se piden ayuda mutuamente", 
              "Family members ask each other for help"),
            t("Se tiene en cuenta la opinión de los hijos en la disciplina", 
              "Children's opinions are considered in discipline"),
            t("Cuando surgen problemas, negociamos para encontrar una solución", 
              "When problems arise, we negotiate to find a solution"),
            t("En nuestra familia hacemos cosas juntos", 
              "In our family, we do things together"),
            t("Todos pueden decir libremente lo que quieren", 
              "Everyone can freely say what they want"),
            t("Nos reunimos frecuentemente en familia (salón, cocina...)", 
              "We often gather as a family (living room, kitchen, etc.)"),
            t("Nos gusta pasar tiempo libre juntos",
              "We like to spend free time together"),
            t("En nuestra familia, a todos nos resulta fácil expresar nuestra opinión",
                "In our family, it is easy for everyone to express their opinion"),
            t("Los miembros de la familia se apoyan unos a otros en los momentos difíciles",
                "Family members support each other in difficult times"),
            t("En nuestra familia se intentan nuevas formas de resolver los problemas",
                "In our family we try new ways to solve problems"),
            t("Los miembros de la familia comparten intereses y hobbies",
                "Family members share interests and hobbies"),
            t("Todos tenemos voz y voto en las decisiones familiares importantes",
                "We all have a say in important family decisions"),
            t("Los miembros de la familia se consultan unos a otros sus decisiones",
                "Family members consult each other about their decisions"),
            t("Los padres y los hijos hablan juntos sobre el castigo",
                "Parents and children talk together about punishment"),
            t("La unidad familiar es una preocupación principal",
                "Family unity is a main concern"),
            t("Los miembros de la familia comentamos los problemas y nos sentimos muy bien con las soluciones encontradas",
                "Family members discuss problems and feel good about the solutions found")
        ]

        respuestas_3 = []
        for i, pregunta in enumerate(preguntas_funcionamiento, 1):
            respuestas_3.append(
                st.radio(f"**{i}. {pregunta}**", opciones_funcionamiento, key=f"func_{i}")
            )

        # Barra de progreso de avance 📈
        st.progress(50, 
                    text=t("⏳ ¡Has completado un 50%! ¡Ánimo!",
                    "⏳ You've completed 50%! Keep going!"))
        
        st.divider()
        st.markdown(t("### 🚀 ¡Seguimos! ¡Queda poco!",
                    "### 🚀 Let's keep going! Almost done!"))
        ##############################################################################################################
        # Estigma Familiar (Escala de 1-5) 🙈💔
        ##############################################################################################################
        st.markdown(t("## 🙈 Bloque 4",
                    "## 🙈 Block 4"))
        st.write(t(
            "¿En qué medida estas afirmaciones reflejan tu experiencia personal?",
            "To what extent do these statements reflect your personal experience?"
        ))

        opciones_estigma = [
            "1 - Definitivamente falso", "2 - Mayormente falso", "3 - Ni verdadero ni falso", 
            "4 - Mayormente verdadero", "5 - Definitivamente verdadero"
        ] if idioma == "Español" else [
            "1 - Definitely false", "2 - Mostly false", "3 - Neither true nor false", 
            "4 - Mostly true", "5 - Definitely true"
        ]

        preguntas_estigma = [
            t("Me sentiría cómodo diciéndole a mis amistades que mi familiar tiene una enfermedad mental",
              "I would feel comfortable telling my friends that my family member has a mental illness"),
            t("Necesito esconder la enfermedad mental de mi familiar",
              "I need to hide my family member's mental illness"),
            t("La enfermedad mental de mi familiar se refleja negativamente en mí",
              "My family member's mental illness reflects negatively on me"),
            t("Me siento culpable porque mi familiar tenga una enfermedad mental",
              "I feel guilty because my family member has a mental illness"),
            t("La enfermedad mental de mi familiar me hace sentir incómodo en situaciones sociales",
              "My family member's mental illness makes me uncomfortable in social situations"),
            t("Me siento abochornado por tener un familiar con enfermedad mental",
              "I feel ashamed of having a family member with a mental illness"),
            t("No puedo vivir mi vida como quisiera porque tengo un familiar con una enfermedad mental",
                "I can't live my life as I would like because I have a family member with a mental illness"),
            t("Tengo que ser selectivo sobre a quién le cuento que mi familiar tiene enfermedad mental",
              "I have to be selective about telling people about my family member's mental illness"),
            t("Las personas con enfermedades mentales en sus familias no deberían tener hijos",
                "People with mental illnesses in their families shouldn't have children"),
            t("Me siento responsable de causar la enfermedad mental de mi familiar",
              "I feel responsible for causing my family member's mental illness"),
            t("Mi vida es más plena porque tengo un familiar con una enfermedad mental",
              "My life is fuller because I have a family member with a mental illness"),
            t("Me siento avergonzado por tener un familiar con una enfermedad mental",
              "I feel ashamed to have a family member with a mental illness"),
            t("Tener un familiar con una enfermedad mental me ha hecho preocuparme más por mi propia salud mental",
              "Having a family member with a mental illness has made me more concerned about my own mental health"),
            t("La gente no quiere hablar conmigo debido a la enfermedad mental de mi familiar",
              "People don't want to talk to me because of my family member's mental illness"),
            t("Me preocupa ser etiquetado como alguien que tiene un familiar con una enfermedad mental",
              "I worry about being labeled as someone who has a family member with a mental illness"),
            t("La gente me culpa de la enfermedad mental de mi familiar",
              "People blame me for my family member's mental illness"),
            t("Mi identidad se ha visto negativamente afectada por la enfermedad mental de mi familiar",
              "My identity has been negatively affected by my family member's mental illness"),
            t("Tengo la esperanza de que algún día las enfermedades mentales serán tratadas como otras enfermedades",
              "I hope that one day mental illnesses will be treated like other illnesses"),
            t("Me siento fuera de lugar en el mundo porque tengo un familiar con una enfermedad mental",
              "I feel out of place in the world because I have a family member with a mental illness"),
            t("Sigo buscando señales de que mi familiar no tiene realmente una enfermedad mental",
              "I keep looking for signs that my family member doesn't really have a mental illness"),
            t("Me culpo por la enfermedad mental de mi familiar",
              "I blame myself for my family member's mental illness"),
            t("Cuando mi familiar con una enfermedad mental es juzgado, me siento juzgado también",
              "When my family member with a mental illness is judged, I feel judged too"),
            t("Me siento discriminado porque tengo un familiar con una enfermedad mental",
              "I feel discriminated against because I have a family member with a mental illness"),
            t("Me siento aislado porque tengo un familiar con una enfermedad mental",
              "I feel isolated because I have a family member with a mental illness"),
            t("Minimizo la gravedad de la enfermedad mental de mi familiar cuando la describo a las personas",
              "I minimize the severity of my family member's mental illness when I describe it to people"),
            t("Soy una persona más fuerte porque tengo un familiar con una enfermedad mental",
              "I am a stronger person because I have a family member with a mental illness"),
            t("Los profesionales de la salud valoran mi conocimiento acerca de la enfermedad mental de mi familiar",
              "Health professionals value my knowledge about my family member's mental illness"),
            t("Puedo hablar abiertamente sobre enfermedades mentales con otros miembros de mi familia",
              "I can openly talk about mental illnesses with other family members"),
            t("Me siento devastado de que mi familiar tenga una enfermedad mental",
              "I feel devastated that my family member has a mental illness"),
            t("Mi autoestima se ha visto deteriorada debido a la enfermedad mental de mi familiar",
              "My self-esteem has deteriorated due to my family member's mental illness")
        ]

        respuestas_4 = []
        for i, pregunta in enumerate(preguntas_estigma, 1):
            respuestas_4.append(
                st.radio(f"**{i}. {pregunta}**", opciones_estigma, key=f"estigma_{i}")
            )

        st.progress(70, text=t("⏳ ¡Ya has completado un 70%!",
                               "⏳ You've completed 70%!"))
        
        st.divider()
        st.markdown(t("### 🌟 ¡Muy bien! Solo faltan las algunas preguntas...",
                      "### 🌟 Very good! Just a few questions left..."))
        ##############################################################################################################
        # PHQ-4 (Ansiedad y Depresión) 😰😔
        ##############################################################################################################
        st.markdown(t("## 🌟 Bloque 5",
                    "## 🌟 Block 5"))
        st.write(t(
            "En las últimas dos semanas, ¿con qué frecuencia te han afectado los siguientes problemas?",
            "In the past two weeks, how often have you been bothered by the following problems?"
        ))

        
        opciones_phq4 = [
            "1 - Nunca", "2 - Varios días", "3 - Más de la mitad de los días", "4 - Casi todos los días"
        ] if idioma == "Español" else [
            "1 - Not at all", "2 - Several days", "3 - More than half the days", "4 - Nearly every day"
        ]
        preguntas_phq4 = [
            t("Sentirse nervioso o ansioso", "Feeling nervous or anxious"),
            t("No poder parar o controlar las preocupaciones", "Not being able to stop or control worrying"),
            t("Poco interés o placer en hacer las cosas", "Little interest or pleasure in doing things"),
            t("Sentirse deprimido o desesperanzado", "Feeling down or hopeless")
        ]

        respuestas_5 = []
        for i, pregunta in enumerate(preguntas_phq4, 1):
            respuestas_5.append(
                st.radio(f"**{i}. {pregunta}**", opciones_phq4, key=f"phq4_{i}")
            )

        st.progress(75, text=t("⏳ ¡Completado 75%! ¡Ya falta poco!",
                               "⏳ Completed 75%! Almost there!"))

        ##############################################################################################################
        # WEMWBS (Bienestar Psicológico) 🌈✨
        ##############################################################################################################
        st.markdown(t("## 🌈 Bloque 6",
                    "## 🌈 Block 6"))
        st.write(t("Por favor, señale la casilla que mejor describa cómo se ha sentido durante las últimas 2 semanas.", 
            "Please check the box that best describes how you have felt during the last 2 weeks."))

        opciones_wemwbs = [
            "1 - Nunca", "2 - Muy pocas veces", "3 - Algunas veces", "4 - Muchas veces", "5 - Siempre o casi siempre"
        ] if idioma == "Español" else [
            "1 - Never", "2 - Very rarely", "3 - Sometimes", "4 - Often", "5 - Always or almost always"
        ]

        preguntas_wemwbs = [
            t("Me he sentido optimista respecto al futuro", "I have felt optimistic about the future"),
            t("Me he sentido útil", "I have felt useful"),
            t("Me he sentido relajado/a", "I have felt relaxed"),
            t("He afrontado bien los problemas", "I have coped well with problems"),
            t("He podido pensar con claridad", "I have been able to think clearly"),
            t("Me he sentido cercano/a a los demás", "I have felt close to others"),
            t("He sido capaz de tomar mis propias decisiones", "I have been able to make my own decisions")
        ]

        respuestas_6 = []
        for i, pregunta in enumerate(preguntas_wemwbs, 1):
            respuestas_6.append(
                st.radio(f"**{i}. {pregunta}**", opciones_wemwbs, key=f"wemwbs_{i}")
            )

        st.progress(80, text=t("⏳ ¡Completado 80%! ¡Casi, casi!",
                               "⏳ Completed 80%! Almost there!"))
        st.divider()

        ###############################################################################
        # Apoyo social (SSQ6)
        ###############################################################################
        st.markdown(t("## 🤝 Bloque 7",
                      "## 🤝 Block 7"))
        st.write(t(
            "Las siguientes preguntas se refieren a personas de tu entorno que te ayudan o apoyan. Marca con qué satisfacción cuentas con su ayuda.",
            "The following questions refer to people in your environment who help or support you. Mark how satisfied you are with the help you receive."
        ))

        opciones_ssq6 = [
            "1 - Muy insatisfecho", "2 - Bastante insatisfecho", "3 - Poco satisfecho",
            "4 - Ni satisfecho ni insatisfecho", "5 - Bastante satisfecho", "6 - Muy satisfecho"
        ] if idioma == "Español" else [
            "1 - Very dissatisfied", "2 - Quite dissatisfied", "3 - Not very satisfied",
            "4 - Neither satisfied nor dissatisfied", "5 - Quite satisfied", "6 - Very satisfied"
        ]

        preguntas_ssq6 = [
            t("Contar con alguien para distraerse cuando se siente agobiado", 
            "Count on someone to distract you when you feel overwhelmed"),
            t("Contar con alguien que le ayude a relajarse cuando está tenso o bajo presión", 
            "Count on someone to help you relax when you are tense or under pressure"),
            t("Alguien que le acepte totalmente, con sus peores y mejores cualidades", 
            "Someone who accepts you completely, with your worst and best qualities"),
            t("Contar con alguien para cuidarle, a pesar de todo lo que le está sucediendo", 
            "Count on someone to take care of you, despite everything that is happening to you"),
            t("Contar con alguien que le ayude a encontrarse mejor cuando se siente realmente deprimido", 
            "Count on someone to help you feel better when you are really depressed"),
            t("Contar con alguien que le consuele cuando está muy disgustado", 
            "Count on someone to comfort you when you are very upset")
        ]

        respuestas_7 = []
        for i, pregunta in enumerate(preguntas_ssq6, 1):
            respuestas_7.append(
                st.radio(f"**{i}. {pregunta}**", opciones_ssq6, key=f"ssq6_{i}")
            )

        st.progress(85, text=t("⏳ ¡Completado 85%! ¡Últimos pasitos!",
                               "⏳ Completed 85%! Last steps!"))
        st.divider()

        ###############################################################################
        # Zarit (Carga Emocional)
        ###############################################################################
        st.markdown(t("### 🧠 Bloque 8",
                      "### 🧠 Block 8"))
        st.write(t(
            "A continuación, se presenta una lista de afirmaciones que reflejan cómo se sienten a veces las personas que cuidan a otros. Indique con qué frecuencia se siente usted así:",
            "Below is a list of statements that reflect how caregivers sometimes feel. Indicate how often you feel this way:"
        ))

        opciones_zarit = [
            "1 - Nunca", "2 - Rara vez", "3 - A veces", "4 - Frecuentemente", "5 - Casi siempre"
        ] if idioma == "Español" else [
            "1 - Never", "2 - Rarely", "3 - Sometimes", "4 - Often", "5 - Almost always"
        ]

        preguntas_zarit = [
            t("¿Siente que su familiar solicita más ayuda de la que realmente necesita?", "Do you feel that your family member asks for more help than they really need?"),
            t("¿Siente que debido al tiempo que dedica a su familiar ya no dispone de tiempo suficiente para usted?", "Do you feel that due to the time you spend with your family member you no longer have enough time for yourself?"),
            t("¿Se siente estresado/a cuando tiene que cuidar a su familiar y atender otras responsabilidades (familia, trabajo)?", "Do you feel stressed when you have to care for your family member and attend to other responsibilities (family, work)?"),
            t("¿Se siente avergonzado por la conducta de su familiar?", "Do you feel embarrassed by your family member's behavior?"),
            t("¿Se siente irritado/a cuando está cerca de su familiar?", "Do you feel irritated when you are close to your family member?"),
            t("¿Cree que la situación afecta negativamente su relación con amigos u otros familiares?", "Do you think the situation negatively affects your relationship with friends or other family members?"),
            t("¿Siente temor por el futuro que le espera a su familia?", "Do you fear for the future awaiting your family?"),
            t("¿Siente que su familiar depende demasiado de usted?", "Do you feel that your family member depends too much on you?"),
            t("¿Se siente agotado/a cuando debe estar junto a su familiar?", "Do you feel exhausted when you have to be with your family member?"),
            t("¿Siente que su salud se ha resentido debido a cuidar a su familiar?", "Do you feel that your health has worsened due to caring for your family member?"),
            t("¿Siente que ha perdido su vida privada debido a su familiar?", "Do you feel you have lost your private life because of your family member?"),
            t("¿Cree que su vida social se ha visto afectada por cuidar a su familiar?", "Do you think your social life has been affected by caring for your family member?"),
            t("¿Se siente incómodo al invitar amigos a casa por su familiar?", "Do you feel uncomfortable inviting friends home because of your family member?"),
            t("¿Cree que su familiar espera que usted le cuide como única persona disponible?", "Do you think your family member expects you to care for them as their only caregiver?"),
            t("¿Siente que no tiene suficiente dinero para cubrir el cuidado de su familiar además de sus propios gastos?", "Do you feel you do not have enough money to cover your family member’s care along with your own expenses?"),
            t("¿Siente que no podrá cuidar de su familiar mucho más tiempo?", "Do you feel that you won't be able to care for your family member much longer?"),
            t("¿Siente que ha perdido el control de su vida desde que su familiar enfermó?", "Do you feel you have lost control of your life since your family member's illness started?"),
            t("¿Le gustaría poder delegar el cuidado de su familiar a otras personas?", "Would you like to delegate your family member's care to other people?"),
            t("¿Se siente inseguro sobre qué hacer con su familiar?", "Do you feel unsure about what to do with your family member?"),
            t("¿Siente que debería hacer más por su familiar?", "Do you feel that you should be doing more for your family member?"),
            t("¿Cree que podría cuidar mejor a su familiar de lo que lo hace?", "Do you think you could care for your family member better than you currently do?"),
            t("En general: ¿Se siente muy sobrecargado por tener que cuidar de su familiar?", "In general: Do you feel very overwhelmed by having to care for your family member?")
        ]

        respuestas_8 = []
        for i, pregunta in enumerate(preguntas_zarit, 1):
            respuestas_8.append(
                st.radio(f"**{i}. {pregunta}**", opciones_zarit, key=f"zarit_{i}")
            )

        st.progress(90, text=t("⏳ ¡Completado 90%! ¡Ya casi terminamos!",
                               "⏳ Completed 90%! Almost done!"))
        st.divider()	

        ###############################################################################
        # Autocompasión (SCS)
        ###############################################################################


        st.markdown(t("## 💖 Bloque 9",
                      "## 💖 Block 9"))
        st.write(t(
            "Piensa en cómo sueles reaccionar ante situaciones negativas. No hay respuestas correctas o incorrectas, simplemente tu experiencia.",
            "Think about how you typically react to negative events. There are no right or wrong answers, just your experience."
        ))

        opciones_scs = [
            "1 - Siempre falso para mí", "2 - Casi siempre falso para mí", "3 - Más bien falso para mí",
            "4 - Ni cierto ni falso para mí", "5 - Más bien cierto para mí", "6 - Casi siempre cierto para mí",
            "7 - Siempre cierto para mí"
        ] if idioma == "Español" else [
            "1 - Always false for me", "2 - Almost always false for me", "3 - Mostly false for me",
            "4 - Neither true nor false for me", "5 - Mostly true for me", "6 - Almost always true for me",
            "7 - Always true for me"
        ]


        preguntas_scs = [
            t("Aunque al principio me siento mal cuando me equivoco, con el tiempo puedo darme un respiro", 
            "Although I feel bad at first when I make a mistake, I eventually give myself a break"),
            t("Me guardo rencor a mí mismo/a por las cosas negativas que he hecho", 
            "I hold a grudge against myself for the negative things I've done"),
            t("Aprender de las cosas malas que he hecho me ayuda a superarlas", 
            "Learning from the bad things I've done helps me overcome them"),
            t("Me resulta realmente difícil aceptarme cuando he cometido un error", 
            "I find it really difficult to accept myself when I have made a mistake"),
            t("Con el tiempo voy comprendiendo los errores que he cometido", 
            "Over time I come to understand the mistakes I have made"),
            t("No dejo de criticarme por las cosas negativas que he sentido, pensado, dicho o hecho", 
            "I keep criticizing myself for the negative things I have felt, thought, said or done")
        ]

        respuestas_9 = []
        for i, pregunta in enumerate(preguntas_scs, 1):
            respuestas_9.append(
                st.radio(f"**{i}. {pregunta}**", opciones_scs, key=f"scs_{i}")
            )

        st.progress(95, text=t("⏳ ¡Completado 95%! ¡Uno más y terminamos!",
                               "⏳ Completed 95%! One more and we're done!"))
        st.divider()

        ###############################################################################
        # Satisfaccion con la IA
        ###############################################################################
        st.markdown(t("## 🤖 Satisfacción con la IA",
                      "## 🤖 Satisfaction with AI"))

        st.write(t("¿Cómo ha sido su experiencia con la herramienta de evaluación a través de la inteligencia artificial?", 
            "How has your experience been with the assessment tool through artificial intelligence?"))

    
        opciones_ia = [
            "1 - Muy en desacuerdo", "2 - En desacuerdo", "3 - Neutral",
            "4 - De acuerdo", "5 - Muy de acuerdo"
        ] if idioma == "Español" else [
            "1 - Strongly disagree", "2 - Disagree", "3 - Neutral",
            "4 - Agree", "5 - Strongly agree"
        ] 

        preguntas_ia = [
            t("Las explicaciones recibidas durante toda la experiencia fueron coherentes.", 
              "The explanations received throughout the experience were coherent."),
            t("La experiencia me ayudó a entender la fiabilidad del sistema de IA.",
              "The experience helped me understand the reliability of the AI system."),
            t("Me siento seguro/a al usar el sistema de IA.",
              "I feel safe using the AI system."),
            t("La información presentada durante la experiencia fue clara.",
              "The information presented during the experience was clear."),
            t("La experiencia fue coherente con mis expectativas.",
              "The experience was consistent with my expectations."),
            t("La presentación de la experiencia fue adecuada para mis necesidades.",
              "The presentation of the experience was suitable for my needs."),
            t("La experiencia mejoró mi comprensión sobre cómo funciona el sistema de IA.",
              "The experience improved my understanding of how the AI system works."),
            t("La experiencia me ayudó a generar confianza en el sistema de IA.",
              "The experience helped me build trust in the AI system."),
            t("La experiencia me ayudó a tomar decisiones más informadas.",
              "The experience helped me make more informed decisions."),
            t("Recibí las explicaciones de manera oportuna y eficiente.",
              "I received the explanations in a timely and efficient manner."),
            t("La información presentada fue personalizada de acuerdo con los requisitos de mi rol.",
              "The information presented was personalized according to the requirements of my role."),
            t("La información presentada fue comprensible dentro de los requisitos de mi rol.",
              "The information presented was understandable within the requirements of my role."),
            t("La información presentada mostró que el sistema de IA funciona bien.",
              "The information presented showed that the AI system works well."),
            t("La experiencia ayudó a completar la tarea prevista usando el sistema de IA.",
              "The experience helped complete the intended task using the AI system."),
            t("La experiencia avanzó de forma lógica.",
              "The experience progressed logically."),
            t("La experiencia fue satisfactoria.",
              "The experience was satisfactory."),
            t("La información presentada durante la experiencia fue suficientemente detallada.",
              "The information presented during the experience was sufficiently detailed."),
            t("La experiencia respondió a todas mis necesidades de explicación.",
              "The experience met all my explanation needs.")
        ]            

        respuestas_10 = []
        for i, pregunta in enumerate(preguntas_ia, 1):
            respuestas_10.append(
                st.radio(f"**{i}. {pregunta}**", opciones_ia, key=f"ia_{i}")
            )

        st.progress(100, text=t("🏁 ¡100% Completado!",
                                "🏁 100% Completed!"))


        ##############################################################################################################
        # Últimas preguntas + envío de datos 🚀
        ##############################################################################################################
        st.success(t(
            "🎉 ¡Has llegado al final del cuestionario!",
            "🎉 You have reached the end of the questionnaire!"
        ))

        enviar = st.form_submit_button(t("📨 Enviar respuestas", "📨 Submit responses"))

        if enviar:
                        
            # Procesar respuestas
            respuestas = {
                "datos": respuestas_0,
                "familiar": respuestas_1,
                "self": respuestas_2,
                "faces": respuestas_3,
                "afpem": respuestas_4,
                "phq4": respuestas_5,
                "wemwbs": respuestas_6,
                "ssq6": respuestas_7,
                "zarit": respuestas_8,
                "scs": respuestas_9,
                "ia": respuestas_10
            }
            incompletos = [bloque for bloque, lista in respuestas.items() if any(r in ["", None] for r in lista)]
            st.write(incompletos)
            if incompletos:
                st.error(t(
                    f"⚠️ Faltan respuestas en: {', '.join(incompletos)}. Por favor, completa todas las preguntas.",
                    f"⚠️ Missing answers in: {', '.join(incompletos)}. Please complete all questions."
                ))
            else:
                st.balloons()
                resultados = procesar_cuestionario(respuestas)
                idx = asociar_id(nombre_familiar, apellido_familiar, SHEET_IDMAP)

                # Crear diccionario de resultados
                datos_resultados = {
                    "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Idioma": idioma,
                    "ID": idx,
                    "Género": genero,
                    "Edad": edad,
                    "País": pais,
                    "Ciudad": ciudad,
                    "Estado civil": estado_civil,
                    "Estado laboral": estado_labora,
                    "Ingresos anuales": ingresos_anuales,
                    "Nivel de estudios": nivel_estudios,
                    "Nombre paciente": nombre_paciente,
                    "Apellido paciente": apellido_paciente,
                    "Centro de atención": centro,
                    "Convive con paciente": convivencia,
                    "Relación": relacion,
                    "Relación antes enfermedad": relacion_antes,
                    "Relación ahora enfermedad": relacion_ahora,
                    "Última visita centro": ultima_visita,
                    "Dificultades asistencia": ', '.join(dificultad),
                }

                # Guardar datos
                if USE_GOOGLE_SHEETS:
                    datos = {**datos_resultados, **resultados}
                    if len(SHEET.get_all_records()) == 0:
                      SHEET.append_row(COLUMNS_GOOGLE_SHEET)
                    fila = [datos.get(col, "") for col in COLUMNS_GOOGLE_SHEET]
                    SHEET.append_row(fila)
                    st.success(t(
                    "✅ ¡Respuestas enviadas correctamente! Muchísimas gracias por tu colaboración 💙",
                    "✅ Responses submitted successfully! Thank you very much for your collaboration 💙"
                    ))
                else:
                    archivo = "respuestas_chatbot.csv"
                    existe = os.path.isfile(archivo)
                    pd.DataFrame([datos_resultados]).to_csv(archivo, mode='a', header=not existe, index=False)
                    st.success(t("✅ ¡Respuestas guardadas en archivo CSV!", "✅ Answers saved in CSV file!"))

else:
    st.warning(t(
        "Debes aceptar participar para continuar con el cuestionario.",
        "You must agree to participate to continue the questionnaire."
    ))