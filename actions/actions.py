# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from time import strftime
from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

import json
from datetime import date


def obtener_datos_arch(ruta):
    a_file = open(str(ruta), "r")
    json_object = json.load(a_file)
    a_file.close()
    return json_object

def guardar_datos_arch(ruta, datos):
    a_file = open(str(ruta), "w")
    json.dump(datos, a_file)
    a_file.close()

def borrar_tarea(id):
    datos = obtener_datos_arch("tareasEnDesarrollo.json")
    tarea = datos[str(id)]

    #desasignar la tarea completada del perfil del empleado
    empladoID = tarea["empleado"]
    empleados = obtener_datos_arch("employees.json")
    empleados[str(empladoID)]["tarea"] = -1
    guardar_datos_arch("employees.json", empleados)

    #guardar la tarea completada en tareas terminadas
    terminadas = obtener_datos_arch("tareasTerminadas.json")
    terminadas[str(id)] = tarea
    guardar_datos_arch("tareasTerminadas.json", terminadas)

    #eliminar tarea completada de tareas en desarrollo
    datos.pop(str(id))
    guardar_datos_arch("tareasEnDesarrollo.json", datos)

def definir_actitud(idEmpleado):
    quejas = obtener_datos_arch("quejas.json")
    empleados = obtener_datos_arch("employees.json")
    #si el empleado tiene muchas quejas de otros empleados se lo clasifica como "problematico"
    nroQuejas = 0
    for queja in quejas:
        if quejas[queja]["id"] == idEmpleado:
            nroQuejas = nroQuejas + 1
    if nroQuejas > 5:
        return "problematico"
    else:
    #si el empleado tiene muchas ausencias se lo clasifica como "irresponsable"
        cantFaltas = len(empleados[idEmpleado]["ausencias"])
        if cantFaltas > 10:
            return "irresponsable"
        else:
    #si el empleado realiza muchas quejas se lo clasifica como "quejoso"
            if empleados[idEmpleado]["cant quejas"] > 3:
                return "quejoso"
            else:
                return "normal"

def asignar_tarea(empleadoID):
    #dado un emplado buscar una tarea compatible y asignarla
    #obtener los datos necesarios
    tareas = obtener_datos_arch("tareas.json")
    empleados = obtener_datos_arch("employees.json")
    

    for tarea in tareas:
        tieneTodas = True
        if tareas[tarea]["rango"] == empleados[empleadoID]["rango"]:
            for habilidadReq in tareas[tarea]["habilidades necesarias"]:
                if tieneTodas == False:
                    break
                for habilidadEmp in empleados[empleadoID]["habilidades"]:
                    if habilidadReq == habilidadEmp:
                        tieneTodas = True
                        break
                    else:
                        tieneTodas = False
            if tieneTodas == True:

                empleados[empleadoID]["tarea"] = str(tarea)
                guardar_datos_arch("employees.json", empleados)

                #mover tarea a tareas en desarrollo
                enDesarrollo = obtener_datos_arch("tareasEnDesarrollo.json")
                enDesarrollo[tarea] = tareas[tarea]
                enDesarrollo[tarea]["empleado"] = str(empleadoID)
                hoy = date.today()
                enDesarrollo[tarea]["fecha inicio"] = hoy.strftime("%d-%m-%Y")
                guardar_datos_arch("tareasEnDesarrollo.json", enDesarrollo)

                #eliminar de tareas sin asignar
                tareas.pop(tarea)
                guardar_datos_arch("tareas.json", tareas)
                return tarea
    return int(-1)           

#accion para registrar ausencia
class ActionFaltar(Action):

    def name(self) -> Text:
        return "action_faltar"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        MAX_FALTAS = 6

        respuestas = {"problematico": "Recorda tener una buena actitud y un trabajo ordenado cuando regreses!", "irresponsable": "Recorda que faltar mucho al trabajo puede afectar tu desempenio y tener consecuencias graves.", "quejoso": ":)", "normal": ":)"}

        a_file = open("employees.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        intencion = str(tracker.latest_message["intent"]["name"])

        if (intencion == "justificar"):
            motivo = str(tracker.latest_message["text"])
            try:
                employee = json_object[str(tracker.get_slot("documento"))]
                actitud = definir_actitud(tracker.get_slot("documento"))

            except:
                dispatcher.utter_message(text="Perdon, no tenemos ese ID en nuestra base de datos.")
                return[]
            cantidad_ausencias = len(employee["ausencias"]) + 1
            if (cantidad_ausencias > MAX_FALTAS):
                msg = "Registramos correctamente tu ausencia, en total faltaste " + str(cantidad_ausencias) + " dias, eso excede el limite de la empresa. Un empleado de Recursos Humanos estara en contacto contigo. " + respuestas[actitud]
                dispatcher.utter_message(text=msg)
            else: 
                msg = "Registramos correctamente tu ausencia, en total faltaste " + str(cantidad_ausencias) + " dias. " +  respuestas[actitud]
                dispatcher.utter_message(text=msg)
            hoy = date.today()
            d1 = hoy.strftime("%d-%m-%Y")
            employee["ausencias"].append({d1:motivo})
            json_object[str(tracker.get_slot("documento"))] = employee

            a_file = open("employees.json", "w")
            json.dump(json_object, a_file)
            a_file.close()

        else:  
            dispatcher.utter_message(text=intencion)
        return[]

class ActionHorarios(Action):

    def name(self) -> Text:
        return "action_horarios"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        a_file = open("employees.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        hora_incio = int(tracker.get_slot("inicio"))
        hora_fin = int(tracker.get_slot("fin"))

        if (hora_fin <= hora_incio):
            dispatcher.utter_message(text="Lo siento, ese horario no es valido")
            return[]
        else:
            horarios_actuales = json_object[str(tracker.get_slot("documento"))]["horario"]
            cant_horas = horarios_actuales[1] - horarios_actuales[0]
            cant_horas_pedidas = hora_fin - hora_incio

            json_object[str(tracker.get_slot("documento"))]["pedidos"].append({"cambiar horas": [hora_incio, hora_fin]})

            a_file = open("employees.json", "w")
            json.dump(json_object, a_file)
            a_file.close()

            if (cant_horas_pedidas < cant_horas):
                dispatcher.utter_message(text="Ya registre tu pedido, tene en cuenta que la cantidad de horas que solicitaste son menores a las que tenes en este momento.")
            else:
                dispatcher.utter_message(text="Tu pedido fue registrado!")
        return[]

class ActionQueja(Action):

    def name(self) -> Text:
        return "action_queja"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intencion = str(tracker.latest_message["intent"]["name"]) 

        a_file = open("indiceEmpleados.json", "r")
        empleados = json.load(a_file)
        a_file.close()

        a_file = open("quejas.json", "r")
        quejas = json.load(a_file)
        a_file.close()

        companero = str(tracker.get_slot("companero"))

        if (intencion == "motivo"):
            try:
                id_companero = empleados[companero]
            except:
                dispatcher.utter_message(text="Perdon, no puedo encontrar ese companero, lo habras escrito bien?")
                return[]
            motivo = str(tracker.latest_message["text"])
            hoy = date.today()
            d1 = hoy.strftime("%d-%m-%Y")
            quejas.append({"fecha": d1, "empleado": companero, "id": id_companero, "motivo": motivo})

            a_file = open("quejas.json", "w")
            json.dump(quejas, a_file)
            a_file.close()

            dispatcher.utter_message(text="Tu queja ha sido regitrada!")
            return[]
        else:
            dispatcher.utter_message(text="Perdon no entendi eso, podrias reformular?")
            return[]

class ActionDias(Action):

    def name(self) -> Text:
        return "action_dias"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            MAX_DAYS = 20

            empleados = obtener_datos_arch("employees.json")
            tareasEnDesarrollo = obtener_datos_arch("tareasEnDesarrollo.json")

            idEmpleado = tracker.get_slot("documento")
            idTarea = empleados[str(idEmpleado)]["tarea"]

            diasAdicionales = tracker.get_slot("dias")

            if (idTarea == -1):
                dispatcher.utter_message(text="Parece que todavia no tenes ninguna tarea asignada. Si queres, me podes pedir que te asigne una.")
                return []
            else:
                tarea = tareasEnDesarrollo[str(idTarea)]
                dias = tarea["dias asignados"]
                if (int(dias) + int(diasAdicionales) > MAX_DAYS):
                    if (int(dias) == MAX_DAYS):
                        msg = "No puedo asignarte mas dias, tu tarea ya tiene el maximo de dias extras."
                    else:
                        msg = "No puedo asignarte " + str(diasAdicionales) + "extra, se pasa del limite de la empresa. Como maximo te puedo dar " + str(MAX_DAYS - int(dias)) + "dias mas."
                else:
                    msg = "Perfecto, se te asignaron " + str(diasAdicionales) + " dias extra."
                    tareasEnDesarrollo[str(idTarea)]["dias asignados"] = int(dias) + int(diasAdicionales)
                    guardar_datos_arch("tareasEnDesarrollo.json", tareasEnDesarrollo)
                dispatcher.utter_message(text=msg)
            return []

class ActionPedirTarea(Action):

    def name(self) -> Text:
        return "action_pedir_tarea"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            empleados = obtener_datos_arch("employees.json")
            tareas = obtener_datos_arch("tareasEnDesarrollo.json")
            idEmpleado = tracker.get_slot("documento")
            if (empleados[idEmpleado]["tarea"] > 0):
                idTarea = empleados[idEmpleado]["tarea"]
                msg = "Parece que ya tenes una tarea sin terminar, la de " + tareas[str(idTarea)]["nombre"] + " del proyecto " + tareas[str(idTarea)]["proyecto"]
                dispatcher.utter_message(text=msg)
            else:
                tareaAsignada = asignar_tarea(idEmpleado)
                if tareaAsignada != -1 :
                    msg = "Encontre una tarea para vos, la de " + tareas[str(tareaAsignada)]["nombre"] + " del proyecto " + tareas[str(tareaAsignada)]["proyecto"]
                    dispatcher.utter_message(text=msg)
                else:
                    dispatcher.utter_message("Ufa, parece que tenemos ninguna tarea para vos en este momento :(")
            return[]

class ActionFinalizarTarea(Action):

    def name(self) -> Text:
        return "action_finalizar_tarea"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            empleados = obtener_datos_arch("employees.json")
            idEmpleado = tracker.get_slot("documento")
            idTarea = empleados[idEmpleado]["tarea"]
            if (idTarea < 0):
                msg = "Parece que no tenes ninguna tarea asignada todavia. Te recomiendo que me pidas que te asigne una."
                dispatcher.utter_message(text=msg)
            else:
                borrar_tarea(idTarea)
                dispatcher.utter_message("Ya di por finalizada tu tarea, si queres me podes pedir otra.")
            return[]

