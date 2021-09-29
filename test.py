import json

a_file = open("employees.json", "r")
json_object = json.load(a_file)
a_file.close()

horarios_actuales = json_object["42839269"]["horario"]
print(horarios_actuales[0])
print(horarios_actuales[1])
cant_horas = horarios_actuales[1] - horarios_actuales[0]
print(cant_horas)