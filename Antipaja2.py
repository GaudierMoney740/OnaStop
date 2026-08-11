import ctypes
import re
import subprocess
import sys
import threading
import time
import webbrowser
import winreg
from tkinter import messagebox
from urllib.parse import urlparse

import psutil
import requests
import vdf
from pathlib import Path
import json
import tkinter as tk


activo = False

"""Detección"""

procesos = ["onanikki.exe", "AEONS_ECHO.exe", "AkoFirstEmbrace.exe", "Ark ReCode.exe", "Cozy Twinkie.exe", "demonbride.exe", "DemonHand.exe", "FAP N.A.F. ARCADE MODE.exe", "Heavy Metal Babes.exe", "HentaiGirlFantasy.exe", "Kaiju Princess 2.exe", "KaijuPrincess.exe"]

websBloqueadas = ["pornhub.com", "xvideos.com", "hentaila.tv", "kemono.cr", "rule34.xxx"]

tagsAdultas = ["Sexual Content",
    "Nudity",
    "NSFW",
    "Hentai",
    "Erotic"]

idsAdultas = [1,3,4]

def cachearWebs():
    try:
        with open("cacheWebs.txt", "w", encoding="utf-8") as f:
            json.dump(websBloqueadas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(e)

def cargarWebs():
    try:
        with open("cacheWebs.txt", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return []

def cachearProcesos():
    try:
        with open("cacheProcesos.txt", "w", encoding="utf-8") as f:
            json.dump(procesos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(e)

def cargarProcesos():
    try:
        with open("cacheProcesos.txt", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return []
def cachearManifest():
    ruta = "C:\\Program Files (x86)\\Steam\\steamapps"
    nombreId = {}
    carpeta = Path(ruta)
    if carpeta.exists():
        for archivo in carpeta.iterdir():
            if archivo.name.endswith(".acf"):
                datos = vdf.loads(archivo.read_text())
                appState = datos.get("AppState", {})
                if appState.get("installdir") and appState.get("appid"):
                    nombreId[appState.get("installdir").lower()] = appState.get("appid")
    with open("cacheManifest.txt", "w", encoding="utf-8") as f:
        json.dump(nombreId, f, ensure_ascii=False, indent=2)

def cargarCacheManifest():
    try:
        with open("cacheManifest.txt", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def cargarCacheTags():
    try:
        archivo = Path("cacheTags.txt")
        if archivo.exists():
            with open("cacheTags.txt", "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        print(e)
        return {}


idAdulto = cargarCacheTags()
def isAdulto(id):
    if str(id) not in idAdulto:
        url = f"https://steamspy.com/api.php?request=appdetails&appid={id}"
        url2 = f"https://store.steampowered.com/api/appdetails?appids={id}"
        adulto1 = False
        adulto2 = False
        try:
            #API: A
            resp1 = requests.get(url, timeout=10)
            if resp1.status_code == 200:
                datos = resp1.json()
                tags = datos.get("tags", {})

                for tag in tags:
                    if tag in tagsAdultas:
                        adulto1 = True

            resp2 = requests.get(url2, timeout=10)
            if resp2.status_code == 200:
                datos2 = resp2.json()
                if datos2.get(str(id), {}).get("success", False):
                    ids = datos2.get(str(id), {}).get("data", {}).get("content_descriptors", {}).get("ids", [])
                    for idcont in ids:
                        if idcont in idsAdultas:
                            adulto2 = True

            if adulto1 or adulto2:
                idAdulto[id] = True
            else:
                idAdulto[id] = False
            with open("CacheTags.txt", "w", encoding="utf-8") as f:
                json.dump(idAdulto, f, ensure_ascii=False, indent=2)
            if adulto1 or adulto2:
                return True
            else:
                return False
        except Exception as e:
            return False
    else:
        return idAdulto.get(id)

revisados = set()
def detectarProcesos():
    global activo
    while activo:
        try:
            for proc in psutil.process_iter():
                try:
                    nombre = proc.name()
                    pid = proc.pid
                    ruta = proc.exe()
                    if nombre in procesos and pid not in revisados:
                        proc.terminate()
                        revisados.add(pid)
                        ids = {"AEONS_ECHO.exe": "2832330", "AkoFirstEmbrace.exe": "3452230", "Ark ReCode.exe": "3587140",
                           "Cozy Twinkie.exe": "4576940", "demonbride.exe": "1250180", "DemonHand.exe": "3264850",
                           "Heavy Metal Babes.exe": "1386950", "HentaiGirlFantasy.exe": "1146950",
                           "Kaiju Princess 2.exe": "2289720", "KaijuPrincess.exe": "1732180"}
                        actuar(ids.get(nombre), nombre)
                    else:
                        path = Path(ruta)
                        partes = [p.lower() for p in path.parts]
                        cache = cargarCacheManifest()
                        id = 0
                        adulto = False
                        for i in range(len(partes)):
                            if i+2 < len(partes) and partes[i] == "steamapps" and partes[i + 1] == "common":
                                id = cache.get(partes[i + 2])
                                if id:
                                    adulto = isAdulto(id)
                        if adulto:
                            proc.terminate()
                            revisados.add(pid)
                            actuar(id, nombre)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(e)
        time.sleep(2)

def bloquearWeb():
    urla = ""
    urlb = ""
    try:
        with open(r"C:\Windows\System32\drivers\etc\hosts", "r+", encoding="utf-8") as f:
            contenido = f.read()
            lineas = contenido.split("\n")
            inicio = None
            final = None
            for line in lineas:
                if line.lower() == "# ANTIPAJA-START".lower():
                    inicio = lineas.index(line)
                if line.lower() == "# ANTIPAJA-END".lower():
                    final = lineas.index(line)
            if inicio is not None and final is not None and inicio < final:
                lineas =  lineas[:inicio] + lineas[final+1:]
            bloque = ["# ANTIPAJA-START"]
            for url in websBloqueadas:
                if not url.startswith("www."):
                    urla = url
                    urlb = "www." + url
                else:
                    urla = url.replace("www.", "")
                    urlb = url
                bloque.append("0.0.0.0\t"+ urla)
                bloque.append("0.0.0.0\t"+ urlb)
            bloque.append("# ANTIPAJA-END")
            lineas.extend(bloque)
            f.seek(0)
            texto = "\n".join(lineas) + "\n"
            f.write(texto)
            f.truncate()
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
            estado2.config(text="Webs: Activo")
    except Exception as e:
        print(e)

def desbloquearWeb():
    try:
        with open(r"C:\Windows\System32\drivers\etc\hosts", "r+", encoding="utf-8") as f:
            contenido = f.read()
            lineas = contenido.split("\n")
            inicio = None
            final = None
            for line in lineas:
                if line.lower() == "# ANTIPAJA-START".lower():
                    inicio = lineas.index(line)
                if line.lower() == "# ANTIPAJA-END".lower():
                    final = lineas.index(line)
            if inicio is not None and final is not None and inicio < final:
                lineas = lineas[:inicio] + lineas[final+1:]
            else:
                return
            f.seek(0)
            texto = "\n".join(lineas) + "\n"
            f.write(texto)
            f.truncate()
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
            estado2.config(text="Webs: Inactivo")
    except Exception as e:
        print(e)

def actuar(id, nombre):
    if id and id not in [0, None,]:
        desinstalar(id)
    inutilizar(nombre)

def desinstalar(gameId):
    try:
        comando = f"steam://uninstall/{gameId}"
        webbrowser.open(comando)
        time.sleep(3)
    except Exception as e:
        print(e)
        time.sleep(1)
def inutilizar(nombre):
    try:
        nombre_base = nombre if nombre.endswith(".exe") else nombre + ".exe"
        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\\" + nombre_base

        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Debugger",0, winreg.REG_SZ, "systray.exe")
        winreg.CloseKey(key)
        print("inutilizado, crack")
        return True
    except Exception as e:
        print("error al inutilizar")
        return False

def activar():
    global activo
    if activo:
        return
    estado.config(text="Ejecutables: Activo")
    activo = True
    hilo = threading.Thread(target=detectarProcesos, daemon=True)
    hilo.start()
def desactivar():
    global activo
    estado.config(text="Ejecutables: Inactivo")
    activo = False

def addPrograma():
    nombre = cajaTexto.get()
    if nombre:
        if not nombre.endswith(".exe"):
            messagebox.showwarning("Aviso", "El nombre introducido no es válido")
        else:
            procesos.append(nombre)
            cachearProcesos()
            programas.insert(tk.END, nombre)
            cajaTexto.delete(0, tk.END)
            messagebox.showinfo("Tarea completada", "Se ha añadido el programa con éxito")
    else:
        messagebox.showwarning("Aviso", "El nombre introducido es nulo")

def eliminarPrograma():
    indice = programas.curselection()
    if not indice:
        messagebox.showwarning("Aviso", "Selecciona un programa")
        return
    nombre = programas.get(indice)
    if nombre:
        try:
            del procesos[indice[0]]
            cachearProcesos()
            programas.delete(indice)
            messagebox.showinfo("Tarea completada", "Se ha eliminado el programa con éxito")
        except Exception as e:
            print(e)
            messagebox.showerror("Error", "Ha habido un error al eliminar")
    else:
        messagebox.showwarning("Aviso", "El programa no existe")

def validarUrl(url):
    if not url.startswith(("http://", "https://")):
        urlExamen = "https://" + url
    else:
        urlExamen = url

    try:
        result = urlparse(urlExamen)
        dominio = result.netloc
        patron = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(patron, dominio))
    except:
        return False

def addPag():
    nombre = cajaTexto2.get().lower()
    if nombre:
        if not validarUrl(nombre):
            messagebox.showwarning("Aviso", "La url introducida no es valida")
        else:
            websBloqueadas.append(nombre)
            cachearWebs()
            urls.insert(tk.END, nombre)
            cajaTexto2.delete(0, tk.END)
            bloquearWeb()
            messagebox.showinfo("Tarea completada", "Se ha añadido la url con éxito")
    else:
        messagebox.showwarning("Aviso", "La url introducida es nula")

def eliminarPag():
    indice = urls.curselection()
    if not indice:
        messagebox.showwarning("Aviso", "Selecciona una página")
        return
    nombre = urls.get(indice)
    if nombre:
        try:
            del websBloqueadas[indice[0]]
            cachearWebs()
            urls.delete(indice)
            messagebox.showinfo("Tarea completada", "Se ha eliminado el programa con éxito")
            bloquearWeb()
        except Exception as e:
            print(e)
            messagebox.showerror("Error", "Ha habido un error al eliminar")
    else:
        messagebox.showwarning("Aviso", "La url no existe")


def isAdmin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def acercaDe():
    win = tk.Toplevel()
    win.title("Acerca de")
    win.geometry("400x300")
    win.resizable(False, False)

    tk.Label(win, text="Version: 2.0").pack(pady=10)
    tk.Label(win, text="Motivaciones: Acabar con la lujuria y el pecado").pack(pady=5)
    tk.Label(win, text="Autor: GaudierMoney740").pack(pady=5)
    tk.Label(win, text="Email para el subnormal que no sepa usar la app: falangista@gmail.com").pack(pady=5)
    tk.Button(win, text="Cerrar", command=win.destroy).pack(pady=10)

def blank():
    pass

if __name__ == "__main__":
    if not isAdmin():
        if getattr(sys, "frozen", False):
            resp = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, None, None, 1)
            if resp <= 32:
                messagebox.showerror("Error", "Se necesitan permisos de administrador para ejecutar el programa")
        else:
            resp = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f"{__file__}", None, 1)
            if resp <= 32:
                messagebox.showerror("Error", "Se necesitan permisos de administrador para ejecutar el programa")
        sys.exit(0)
    else:
        cachearManifest()
        procs = cargarProcesos()
        if procs and procs not in [[],]:
            procesos = procs
        else:
            cachearProcesos()
        pags = cargarWebs()
        if pags and pags not in [[],]:
            websBloqueadas = pags
        else:
            cachearWebs()

        # GUI

        ventana = tk.Tk()
        ventana.title("AntiPaja 2026 Edition 2.0")
        ventana.geometry("500x500")
        ventana.resizable(False, False)

        areaEstados = tk.Frame(ventana)
        areaEstados.pack()
        estado = tk.Label(areaEstados, text="Ejecutables: Inactivo")
        estado.grid(row=0, column=0, padx=5)
        marco1 = tk.Frame(areaEstados)
        marco1.grid(row=1, column=0, padx=5)
        activarBoton = tk.Button(marco1, text="Activar", command=activar)
        activarBoton.grid(row=0, column=0)
        desactivarBoton = tk.Button(marco1, text="Desactivar", command=desactivar)
        desactivarBoton.grid(row=0, column=1)
        estado2 = tk.Label(areaEstados, text="Webs: Inactivo")
        estado2.grid(row=0, column=1)
        marco2 = tk.Frame(areaEstados)
        marco2.grid(row=1, column=1)
        activarBoton2 = tk.Button(marco2, text="Activar", command=bloquearWeb)
        activarBoton2.grid(row=0, column=0)
        desactivarBoton2 = tk.Button(marco2, text="Desactivar", command=desbloquearWeb)
        desactivarBoton2.grid(row=0, column=1)


        area1 = tk.Frame(ventana)
        area1.place(relx=0.3, rely=0.5, anchor="center")
        ejecutablesLabel = tk.Label(area1, text="Ejecutables:")
        ejecutablesLabel.grid(row=0, column=0, pady=10)
        programas = tk.Listbox(area1)
        programas.grid(row=1, column=0, pady=10)
        for p in procesos:
            programas.insert(tk.END, p)
        cajaTexto = tk.Entry(area1)
        cajaTexto.grid(row=2, column=0, pady=10)
        marco2 = tk.Frame(area1)
        marco2.grid(row=3, column=0, pady=10)
        addBoton = tk.Button(marco2, text="Añadir", command=addPrograma)
        addBoton.grid(row=1, column=0)
        eliminarBoton = tk.Button(marco2, text="Eliminar seleccionado", command=eliminarPrograma)
        eliminarBoton.grid(row=1, column=1)

        area2 = tk.Frame(ventana)
        area2.place(relx=0.7, rely=0.5, anchor="center")
        urlLabel = tk.Label(area2, text="Páginas web:")
        urlLabel.grid(row=0, column=0, pady=10)
        urls = tk.Listbox(area2)
        urls.grid(row=1, column=0, pady=10)
        for p in websBloqueadas:
            urls.insert(tk.END, p)
        cajaTexto2 = tk.Entry(area2)
        cajaTexto2.grid(row=2, column=0, pady=10)
        marco3 = tk.Frame(area2)
        marco3.grid(row=3, column=0, pady=10)
        addBoton2 = tk.Button(marco3, text="Añadir", command=addPag)
        addBoton2.grid(row=0, column=0)
        eliminarBoton2 = tk.Button(marco3, text="Eliminar seleccionado", command=eliminarPag)
        eliminarBoton2.grid(row=0, column=1)

        acercaDeBoton = tk.Button(ventana, text="Acerca de", command=acercaDe)
        acercaDeBoton.place(relx=0.1, rely=0.9, anchor="center")
        ventana.mainloop()

