import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk ,ImageGrab
import subprocess
import queue

from comun_file import  *

# Globales Interfaz
root = None
frame = None
frame02 = None
frame03 = None
frame04 = None
label = None
label_clientes_serverX = None
label_tiempo = None
boton02 = None

texto_label_contador = None
cuenta_atras_label = None
#Para comprobar el tiempo de grabacion
hora_inicio = datetime.now().strftime("%H:%M:%S")
hora_inicio = datetime.strptime(hora_inicio, "%H:%M:%S")

def clientes_X():
    # Comando a ejecutar
    comando = "xlsclients | wc -l"

    # Ejecutar el comando y capturar la salida
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

    # Verificar si la ejecución fue exitosa
    if resultado.returncode == 0:
        # Imprimir el resultado obtenido
        return str(resultado.stdout.strip())
        #print(f"Número de clientes conectados: {resultado.stdout.strip()}")
    else:
        # Manejar el caso de error si es necesario
        print(f"Error al ejecutar el comando: {resultado.stderr}")

def iniciar_cuenta_atras(segundos):
    global texto_label_contador
    global cuenta_atras_label

    if segundos > 0:
        minutos, segundos_restantes = divmod(segundos, 60)
        cuenta_atras_label.config(text=f"{minutos:02}:{segundos_restantes:02}")
        root.after(1000, iniciar_cuenta_atras, segundos - 1)
    else:
        cuenta_atras_label.config(text="¡Grabando!")
        texto_label_contador.pack_forget()
        cuenta_atras_label.pack_forget()

def mostrar_imagenes_gr(lista,frame,size):

    # Limpiar el frame antes de agregar nuevas imágenes
    for widget in frame.winfo_children():
        widget.destroy()

    referencias_imagenes = []  # Lista para mantener referencias de las imágenes
    for i in range(len(lista)):
        img_pil = Image.fromarray(lista[i])  # Convertir numpy array a PIL Image
        img_resized = img_pil.resize(size, Image.BICUBIC)  # Redimensionar la imagen
        img_tk = ImageTk.PhotoImage(img_resized)  # Convertir a PhotoImage
        referencias_imagenes.append(img_tk)  # Mantener una referencia a la imagen
        label_01 = tk.Label(frame, image=img_tk)
        label_01.pack(side="left", padx=10)
    
    # Asignar referencias de imagen al frame para evitar recolección de basura
    frame.image_refs = referencias_imagenes

def actualizar_hora():
    global hora_inicio,label_tiempo

    hora_fin = datetime.now().strftime("%H:%M:%S")
    hora_fin = datetime.strptime(hora_fin, "%H:%M:%S")  # Convertimos las cadenas de tiempo en objetos datetime

    # Calculamos la diferencia entre las horas
    diferencia = hora_fin - hora_inicio

    # Extraemos la diferencia en horas, minutos y segundos
    diferencia_horas = diferencia.seconds // 3600
    diferencia_minutos = (diferencia.seconds // 60) % 60
    diferencia_segundos = diferencia.seconds % 60

    # Formateamos el resultado en el formato deseado
    resultado_formateado = "{:02d}:{:02d}:{:02d}".format(diferencia_horas, diferencia_minutos, diferencia_segundos)
    label_tiempo.config(text=resultado_formateado)


def finalizar_gr():
    global key_thread , stop_event
    global root
    
    # Detener el hilo de presionar teclas
    stop_event.set()
    key_thread.join()
    root.destroy()  # Cerrar la ventana principal


def check_queue_gr():
    global cola_imagenes_map
    global cola_imagenes_pov
    global root ,frame ,frame02 ,label ,label_clientes_serverX
    try:
        actualizar_hora()
        # Obtenemos una lista de imágenes de la cola
        lista_imagenes_map = cola_imagenes_map.get_nowait()
        lista_imagenes_pov = cola_imagenes_pov.get_nowait()
        mov_raton = cola_mov_raton.get_nowait()
        n_clientes = "Nº clientes servidorX : "+ clientes_X()+"/23"
     
        mostrar_imagenes_gr(lista_imagenes_map,frame,(150,110))
        mostrar_imagenes_gr(lista_imagenes_pov,frame02,(520,300))
        label.config(text=str(mov_raton))
        label_clientes_serverX.config(text=str(n_clientes))
    except queue.Empty:
        pass
    # Volver a comprobar la cola después de un corto intervalo
    root.after(1, check_queue_gr)

def interfaz_grabacion():
    global root
    global frame
    global frame02
    global frame03
    global frame04
    global label , label_clientes_serverX ,label_tiempo
    global boton02
    global texto_label_contador
    global cuenta_atras_label

    # Crear la ventana principal
    root = tk.Tk()
    root.title("Teudorico")

    # Crear la etiqueta para el texto "Quedan:"
    texto_label_contador = tk.Label(root, text="Empiece ya a jugar:", font=("Arial", 48))
    texto_label_contador.pack(pady=20)

    # Crear la etiqueta para mostrar la cuenta atrás
    cuenta_atras_label = tk.Label(root, text="00:05", font=("Arial", 48))
    cuenta_atras_label.pack(pady=20)

    # Crear un fila con imagenes mini_mapa y list_box 
    frame = tk.Frame(root)
    frame.pack(pady=20)

    # Crear un fila con imagenes pov
    frame02 = tk.Frame(root)
    frame02.pack(pady=20)

    # Crear un fila con el movimiento registrado
    frame03 = tk.Frame(root)
    frame03.pack(pady=20)
    label = tk.Label(frame03, text="", font=("Arial", 18), bg="yellow", fg="blue")
    label.pack(pady=20)

    label_clientes_serverX = tk.Label(frame03, text="", font=("Arial", 18), bg="orange", fg="blue")
    label_clientes_serverX.pack(pady=20)

    label_tiempo = tk.Label(frame03, text=" ", font=("Helvetica", 10))
    label_tiempo.pack(pady=20)

    # Crear un marco Finalizado  
    frame04 = tk.Frame(root)
    frame04.pack(pady=20)

    
    boton02 = tk.Button(frame04, text="RECORDING ⏺️", command=finalizar_gr , font=("Arial", 16) ,width=120, height=7, bg="red", fg="white")
    boton02.pack()

    # Iniciar la cuenta atrás de 5 segundos al iniciar la aplicación
    root.after(1000, iniciar_cuenta_atras, 5)

    # Iniciar la comprobación de la cola
    check_queue_gr()   #Tenemos que comprobar la cola de images constantemente
    root.mainloop()

    

