from capturadoras.capturadora_utils import *


def modo_autonomo_moviminetos():

    time.sleep(5)       #Esperamos unos segundos hasta que empiece la partida

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
            moviminento = detector_movimiento()
            comun_file.cola_imagenes_map.put(lista_img_mini)
            comun_file.cola_imagenes_pov.put(lista_img_pov)
            comun_file.cola_mov_raton.put(moviminento)    #Enviamos la actividad del usuario a la interfaz grafica
            
            i = 0
            lista_img_mini = [None, None,None, None,None]
            lista_img_pov = [None, None,None, None,None]
        
        # Esperar 0.5 segundos antes de la próxima captura
        time.sleep(0.2)

        # Salir del bucle si se presiona el boton finalizar
        if comun_file.get_Finalizacion == True:
            break

def detector_movimiento():
    global exit_event
    global keys_number

    # Crear y comenzar un nuevo hilo para el listener
    mouse_thread = threading.Thread(target=mouse_listener)
    keyboard_thread  = threading.Thread(target=keyboard_listener)

    mouse_thread.start()
    keyboard_thread.start()

    # Esperar hasta que se establezca el evento para salir del bucle
    exit_event.wait()

    moviminento = [int(keys_number),int(mouse_coords["x"]),int(mouse_coords["y"])]
    keys_number = 0

    return moviminento