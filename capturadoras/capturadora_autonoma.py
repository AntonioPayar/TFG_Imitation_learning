from capturadoras.capturadora_utils import *


deteccion_teclado = False
deteccion_raton = False

def on_move(x, y):
    global mouse_coords,exit_event
    global deteccion_raton

    deteccion_raton = True
    comun_file.cola_deteccion_raton.put(deteccion_raton)    #Enviamos la actividad del usuario a la interfaz grafica

    mouse_coords['x'] = x
    mouse_coords['y'] = y
    # Establecer el evento para salir del bucle
    exit_event.set()

def on_key_press(key):
    global keys_pressed
    global deteccion_teclado

    deteccion_teclado = True
    comun_file.cola_deteccion_teclado.put(deteccion_teclado)    #Enviamos la actividad del usuario a la interfaz grafica
    try:
        if key.char in ['w', 'a', 's', 'd']:
            keys_pressed.add(key.char)
            check_combinations()
    except AttributeError:
        pass

def on_key_release(key):
    global keys_pressed
    global deteccion_teclado

    deteccion_teclado = False
    comun_file.cola_deteccion_teclado.put(deteccion_teclado)    #Enviamos la actividad del usuario a la interfaz grafica
    try:
        if key.char in ['w', 'a', 's', 'd']:
            keys_pressed.discard(key.char)
    except AttributeError:
        pass

def check_combinations():
    global keys_number

    if 'w' in keys_pressed:
        keys_number = 1  
    elif 'a' in keys_pressed:
        keys_number = 2
    elif 's' in keys_pressed:
        keys_number = 3 
    elif 'd' in keys_pressed:
        keys_number = 4  
    elif 'w' in keys_pressed and 'a' in keys_pressed:
        keys_number = 5
    elif 'w' in keys_pressed and 'd' in keys_pressed:
        keys_number = 6 
    elif 's' in keys_pressed and 'a' in keys_pressed:
        keys_number = 7
    elif 's' in keys_pressed and 'd' in keys_pressed:
        keys_number = 8

def mouse_listener():
    # Listener para el movimiento del mouse
    with Listener(on_move=on_move) as listener:
        listener.join()

def keyboard_listener():
    with KeyboardListener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()


def modo_autonomo_moviminetos():
    global deteccion_raton

    time.sleep(5)       #Esperamos unos segundos hasta que empiece la partida

    # Crear y comenzar un nuevo hilo para el listener
    mouse_thread = threading.Thread(target=mouse_listener)
    keyboard_thread  = threading.Thread(target=keyboard_listener)

    mouse_thread.start()
    keyboard_thread.start()
    # Esperar hasta que se establezca el evento para salir del bucle
    exit_event.wait()
    deteccion_raton = False

    # Asegúrate de que la ventana esté visible
    if comun_file.cod_window.isMinimized:
        comun_file.cod_window.restore()

    # Trae la ventana al frente
    comun_file.cod_window.activate()

    lista_url_img_mini = [None, None,None, None,None]
    lista_img_mini = [None, None,None, None,None]
    lista_url_img_pov = [None, None,None, None,None]
    lista_img_pov = [None, None,None, None,None]

    i = 0

    while True:
        
        img_mini_mapa , img_np = cargar_pantalla()

        # Obtiene la fecha y hora actual
        now = datetime.now()
        timestamp = now.strftime("%d-%H-%M-%S")

        mini_str = f"datos/mini_mapa/mini_mapa_{timestamp}.jpg"
        pov_str = f"datos/pov/pov_{timestamp}.jpg"

        #Almacenamos la localizacion y la propia img
        lista_url_img_mini[i] = mini_str
        lista_url_img_pov[i] = pov_str
        lista_img_mini[i] = img_mini_mapa
        lista_img_pov[i] = img_np

        if i < 4:
            i = i + 1
        else:
            comun_file.cola_imagenes_map.put(lista_img_mini)
            comun_file.cola_imagenes_pov.put(lista_img_pov)
            i = 0
            lista_img_mini = [None, None,None, None,None]
            lista_img_pov = [None, None,None, None,None]
        
        # Esperar 0.5 segundos antes de la próxima captura
        time.sleep(0.2)

        # Salir del bucle si se presiona el boton finalizar
        if comun_file.get_Finalizacion == True:
            break