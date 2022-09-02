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
        PROCESS.append(
            subprocess.Popen(
                'python client.py -a 127.0.0.1 -p 7776 -n name1',
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        )
        PROCESS.append(
            subprocess.Popen(
                'python client.py -a 127.0.0.1 -p 7776 -n name2',
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        )
        PROCESS.append(
            subprocess.Popen(
                'python client.py -a 127.0.0.1 -p 7776 -n name3',
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        )
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
