"""Лаунчер"""

import subprocess

PROCESS = []

string = 'Выберите действие:\n\ts - запустить клиенты\n\tx - закрыть все ' \
         'окна\n\tq - выход\n---> '

while True:
    ACTION = input(string)

    if ACTION == 'q':
        break
    elif ACTION == 's':
        for i in range(2):
            PROCESS.append(
                subprocess.Popen(
                    'python client.py -a 127.0.0.1 -p 7776 -m send',
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            )
        for i in range(2):
            PROCESS.append(
                subprocess.Popen(
                    'python client.py -a 127.0.0.1 -p 7776 -m listen',
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            )
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
