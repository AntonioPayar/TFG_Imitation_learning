import tkinter as tk
from Xlib import display

listbox = None
scrollbar = None
frame = None
label = None
root = None
ventana = None
opcion_elegida = None

def list_box_ventanas_abiertas():
    global listbox
    global scrollbar
    global frame

    listbox = tk.Listbox(frame, height=10, width=50, selectmode=tk.SINGLE)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)

    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)#    Listbox para que use la barra de desplazamiento
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)



    for i in range(1, 1+2):
        listbox.insert(tk.END, i)     #Añadimos el monitor a la interfaz
    
    #display.flush() # Llamar a flush para asegurar que todas las operaciones pendientes se completen
    #display.close()
    
    # Asignar la función de doble clic al Listbox
    listbox.bind("<Double-1>", on_double_click)

def on_double_click(event):
    global listbox
    global scrollbar
    global label
    global ventana

    try:
        seleccion = listbox.curselection()
        if seleccion:
            index = seleccion[0]
            ventana = listbox.get(index)
            listbox.pack_forget()  # Ocultar el Listbox
            scrollbar.pack_forget()  # Ocultar el scrollbar
            label.config(text=f"Ventana seleccionada: {ventana}")
            label.pack(pady=20)  # Mostrar el Label
    except Exception as e:
        print(f"Error al procesar doble clic: {e}")

def boton_modo_grabacion():
    global root
    global opcion_elegida

    opcion_elegida = 0
    root.destroy()  # Cerrar la ventana principal

def boton_modo_autonomo():
    global root
    global opcion_elegida

    opcion_elegida = 1
    root.destroy()  # Cerrar la ventana principal


def interfaz_selccion_ventana():
    global frame
    global label
    global root

    # Crear la ventana principal
    root = tk.Tk()
    root.title("Roberick")

    # Crear un fila con imagenes mini_mapa y list_box 
    frame = tk.Frame(root)
    list_box_ventanas_abiertas()    #Creamos un listbox para seleccionar ventana
    frame.pack(pady=20)
    # Crear un Label para mostrar la ventana seleccionada (inicialmente oculto)
    label = tk.Label(root, text="", font=("Arial", 16))

    # Crear un marco Finalizado  
    frame02 = tk.Frame(root)
    frame02.pack(pady=20)

    # Crear Labels dentro del frame02font=("Helvetica", 10)
    label_tx_01 = tk.Label(frame02, text="ADVERTENCIA", bg="red", fg="white", font=("Helvetica", 20, "bold"))
    label_tx_02 = tk.Label(frame02, text="- Empezara a presionar boton (w)")
    label_tx_03 = tk.Label(frame02, text="- Estate jugando, dentro del juego antes de dar al boton")

    # Empaquetar los Labels
    label_tx_01.pack()
    label_tx_02.pack()
    label_tx_03.pack()
    
    boton02 = tk.Button(frame02, text="Grabación", command=boton_modo_grabacion , font=("Arial", 16) ,width=20, height=7, bg="grey", fg="white")
    boton02.pack(side=tk.LEFT, padx=5)

    boton03 = tk.Button(frame02, text="Modo Autonomo IA", command=boton_modo_autonomo , font=("Arial", 16) ,width=20, height=7, bg="grey", fg="white")
    boton03.pack(side=tk.LEFT, padx=5)

    root.mainloop()

    return ventana , opcion_elegida