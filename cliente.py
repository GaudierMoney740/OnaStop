import json
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox

import requests

clave = ""
contrasena = ""

def actualizarCodigo():
    global clave
    global contrasena
    def actualizarLabel():
        global clave
        label.config(text=f"Clave: {clave}")
    while True:
        pet = requests.post("http://localhost:5002/code", json=json.dumps({"contrasena": contrasena}))
        pet.raise_for_status()
        clave = pet.json().get("codigoUnico")
        ventana.after(0, actualizarLabel)
        time.sleep(1)



def pedirContrasena():
    global contrasena
    win = tk.Toplevel()
    win.title("Introduce tu contraseña")
    win.geometry("300x300")
    win.resizable(width=False, height=False)
    label = tk.Label(win, text="Introduce tu contraseña:")
    label.pack()
    entry = tk.Entry(win)
    entry.pack()
    def autenticar():
        global contrasena
        cont = entry.get()
        pet = requests.post("http://localhost:5002/validarcont", json=json.dumps({"contrasena": cont}))
        pet.raise_for_status()
        if pet.json().get("estado"):
            messagebox.showinfo("Cliente", "La contraseña es correcta")
            contrasena = cont
            win.destroy()
        else:
            messagebox.showwarning("Cliente", "La contraseña es incorrecta")
    boton = tk.Button(win, text="Enviar", command=autenticar)
    boton.pack()

    win.wait_window()

if __name__ == "__main__":
    ventana = tk.Tk()
    ventana.withdraw()
    pedirContrasena()
    ventana.deiconify()
    if contrasena == "":
        messagebox.showerror("Error", "Has cerrado la ventana sin introducir la contraseña")
        ventana.destroy()
        sys.exit(0)
    threading.Thread(target=actualizarCodigo, daemon= True).start()
    ventana.title("Cliente clave temporal")
    ventana.geometry("500x500")
    ventana.resizable(width=False, height=False)
    label = tk.Label(ventana, text=f"Clave: {clave}")
    label.pack()
    ventana.mainloop()