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
    empleados[str(empladoID)]["tarea"] = "null"
    guardar_datos_arch("employees.json", empleados)

    #guardar la tarea completada en tareas terminadas
    terminadas = obtener_datos_arch("tareasTerminadas.json")
    terminadas[str(id)] = tarea
    guardar_datos_arch("tareasTerminadas.json", terminadas)

    datos.pop(str(id))
    guardar_datos_arch("tareasEnDesarrollo.json", datos)

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
    
print(asignar_tarea("32446756"))

