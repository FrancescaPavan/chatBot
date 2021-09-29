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

#accion para registrar ausencia
class ActionFaltar(Action):

    def name(self) -> Text:
        return "action_faltar"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        MAX_FALTAS = 6

        a_file = open("employees.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        intencion = str(tracker.latest_message["intent"]["name"])

        if (intencion == "justificar"):
            motivo = str(tracker.latest_message["text"])
            try:
                employee = json_object[str(tracker.get_slot("documento"))]
            except:
                dispatcher.utter_message(text="Perdon, no tenemos ese ID en nuestra base de datos.")
                return[]
            cantidad_ausencias = len(employee["ausencias"]) + 1
            if (cantidad_ausencias > MAX_FALTAS):
                msg = "Registramos correctamente tu ausencia, en total faltaste " + str(cantidad_ausencias) + " dias, eso excede el limite de la empresa. Un empleado de Recursos Humanos estara en contacto contigo."
                dispatcher.utter_message(text=msg)
            else: 
                msg = "Registramos correctamente tu ausencia, en total faltaste " + str(cantidad_ausencias) + " dias."
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

            a_file = open("employees.json", "r")
            json_object = json.load(a_file)
            a_file.close()

            id = str(tracker.get_slot('documento'))
            try:
                user_info = json_object[id]
            except:
                dispatcher.utter_message(text="Perdon ese ID no existe en mi base de datos\n\n")
                return[]
            tarea = int(tracker.get_slot('tarea'))
            for job in json_object[id]["tareas"]:
                if (job["id"] == tarea):
                    current_days = job["dias asignados"]
                    new_days = int(tracker.get_slot('dias'))
                    if (current_days + new_days <= MAX_DAYS ):
                        msg = "Genial, se te asignaron" + str(new_days) + " dias mas para tu tarea de ID " + str(tarea)
                        dispatcher.utter_message(text=msg)
                        dispatcher.utter_message(text="Con que mas te puedo ayudar?")
                        job["dias asignados"] = new_days + current_days

                        a_file = open("employees.json", "w")
                        json.dump(json_object, a_file)
                        a_file.close()

                        return[]
                    else:
                        msg = "Perdon, no puedo asignarle " + str(new_days) + " a esa area, excede el limite de la empresa. Puedo asignarle un maximo de " + str(MAX_DAYS - current_days) + " dias."
                        dispatcher.utter_message(text=msg)
                        return[]
                dispatcher.utter_message(text="Perdon, no puedo encontrar esa tarea. Por favor checkea que sea correcto o proba con otro ID.")    
                return[]
            return []