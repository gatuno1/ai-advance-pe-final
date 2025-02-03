#!/usr/bin/env python

import re
import json

"""
Este módulo contiene funciones para la obtención de los datos personales del paciente y los síntomas relacionados con su enfermedad.

Funciones disponibles:
- obtener_datos_paciente: Solicita al cliente los datos personales.
- registrar_sintomas: Solicita al paciente que ingrese sus síntomas.
- realizar_preguntas_relevantes: Genera preguntas relevantes basándose en los síntomas y características del paciente utilizando GPT-4o-mini.
"""



def obtener_datos_paciente():
    datos = {}
    intentos_maximos = 3

    # Validación con intentos limitados
    def solicitar_dato(pregunta, validacion_func, campo):
        intentos = 0
        ultima_respuesta = ""

        while intentos < intentos_maximos:
            respuesta = input(pregunta)
            ultima_respuesta = respuesta
            if validacion_func(respuesta):
                datos[campo] = respuesta if campo != "edad" else int(respuesta)
                return True
            print(f"⚠️ {campo.capitalize()} inválido. Inténtalo nuevamente.")
            intentos += 1

        # Si supera los intentos permitidos
        datos[campo] = ultima_respuesta
        return False

    print("\n🔹 **Registro de Datos Demográficos**")

    if not solicitar_dato("Ingresa tu nombre: ", validar_nombre, "nombre"):
        print("⛔ No es posible continuar sin un nombre válido.")
        guardar_datos(datos, False)
        return

    if not solicitar_dato("Ingresa tu RUT (Ejemplo: 12345678-9): ", validar_rut, "rut"):
        print("⛔ No es posible continuar sin un RUT válido.")
        guardar_datos(datos, False)
        return

    if not solicitar_dato("Ingresa tu sexo (M: Masculino, F: Femenino, N: No informa): ", validar_sexo, "sexo"):
        print("⛔ No es posible continuar sin un sexo válido.")
        guardar_datos(datos, False)
        return

    if not solicitar_dato("Ingresa tu edad (0-120 años): ", validar_edad, "edad"):
        print("⛔ No es posible continuar sin una edad válida.")
        guardar_datos(datos, False)
        return
    
    if not solicitar_dato("Ingresa tu peso (0-200 Kg): ", validar_peso, "peso"):
        print("⛔ No es posible continuar sin un peso valido")
        guardar_datos(datos, False)
        return

    # Si todos los datos son correctos
    guardar_datos(datos, True)
    print("✅ Datos guardados exitosamente en 'datos_demograficos.json'")

    return datos





def registrar_sintomas():
    """Solicita al paciente que ingrese sus síntomas."""
    print("\nIngrese los síntomas que está presentando (separados por coma):")
    sintomas = input("Síntomas: ")

    return [s.strip() for s in sintomas.split(",")]


def realizar_preguntas_relevantes(datos_basicos, sintomas, clientIA):
    """Genera preguntas relevantes basándose en los síntomas y características del paciente utilizando GPT-4o-mini."""
    print("\nEl modelo está analizando los síntomas y generando preguntas adicionales...")

    # Ajustar el prompt para incluir sexo, peso y edad del paciente
    prompt = (
        f"Paciente de {datos_basicos['edad']} años, sexo {datos_basicos['sexo']} y peso {datos_basicos['peso']} kg.\n"
        f"Síntomas reportados: {', '.join(sintomas)}\n"
        "Con base en estos síntomas y características del paciente, genere hasta 5 preguntas relevantes "
        "para obtener más detalles que complementen el diagnóstico. Las preguntas deben ser claras y específicas."
    )

    try:
        messages = [
            {
                "role": "system",
                "content": "Eres un asistente médico que ayuda a recopilar información relevante de pacientes.",
            },
            {"role": "user", "content": prompt},
        ]

        response = clientIA.chat.completions.create(
            model="gpt-4o-mini",  # Ajustado al modelo compatible
            messages=messages,
            temperature=0,
            max_tokens=1000,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
        )
        
        preguntas = response.choices[0].message.content.split("\n")
        respuestas = []
        for pregunta in preguntas:
            if pregunta.strip():
                respuesta = input(f"{pregunta.strip()} ")
                respuestas.append({
                    "pregunta": pregunta.strip(),
                    "respuesta": respuesta
                })

        # Generar un JSON con las preguntas y respuestas en el formato solicitado
        preguntas_respuestas = respuestas

        # Guardar las preguntas y respuestas en un archivo JSON con codificación UTF-8
        with open('preguntas_respuestas.json', 'w', encoding='utf-8') as f:
            json.dump(preguntas_respuestas, f, indent=4, ensure_ascii=False)
        print("1")

        return respuestas
    except Exception as e:
        print(f"Error al generar preguntas: {str(e)}")
        return []




# Funciones de validación
def validar_nombre(nombre):
    return bool(re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", nombre))

def validar_rut(rut):
    return bool(re.match(r"^[0-9]+-[0-9Kk]$", rut))

def validar_sexo(sexo):
    return sexo.upper() in ["M", "F", "N"]

def validar_edad(edad):
    return edad.isdigit() and 0 <= int(edad) <= 120

def validar_peso(peso):
    return peso.isdigit() and 0 <= int(peso) <= 200

def guardar_datos(datos, almacenado_correctamente):
    datos["almacenado_correctamente"] = almacenado_correctamente
    with open("datos_demograficos.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)