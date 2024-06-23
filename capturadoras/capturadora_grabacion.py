from capturadoras.capturadora_utils import *


def modo_grabacion_movimientos():

    time.sleep(5)       #Esperamos unos segundos hasta que empiece la partida

    lista_url_img_mini = [None, None,None, None,None]
    lista_img_mini = [None, None,None, None,None]
    lista_url_img_pov = [None, None,None, None,None]
    lista_img_pov = [None, None,None, None,None]

    i = 0

    while True:
        
        img_mini_mapa , img_np = cargar_pantalla()  #Esta en capturadora_utils.py

        
        if img_mini_mapa.size != 0 and img_np.size != 0:
            # Obtiene la fecha y hora actual
            now = datetime.now()
            timestamp = now.strftime("%d-%H-%M-%S")

            mini_str = f"datos/mini_mapa/mini_mapa_{timestamp}.jpg"
            pov_str = f"datos/pov/pov_{timestamp}.jpg"

            # -------------------------------------------------Guarda las imágenes redimensionadas en formato JPG
            # cv2.imwrite(mini_str, img_mini_mapa)
            # cv2.imwrite(pov_str, img_np)

            #Almacenamos la localizacion y la propia img
            lista_url_img_mini[i] = mini_str
            lista_url_img_pov[i] = pov_str
            lista_img_mini[i] = img_mini_mapa
            lista_img_pov[i] = img_np

            if i < 4:
                i = i + 1
            else:
                #-----------Almacenamos las img y csv
                moviminento = modo_grabacion_almacenar_informacion(lista_url_img_mini,lista_url_img_pov)

                #Enviamos las imagenes a la interfaz grafica
                comun_file.cola_imagenes_map.put(lista_img_mini)
                comun_file.cola_imagenes_pov.put(lista_img_pov)
                comun_file.cola_mov_raton.put(moviminento)

                i = 0
                lista_img_mini = [None, None,None, None,None]
                lista_img_pov = [None, None,None, None,None]
            
            # Esperar 0.5 segundos antes de la próxima captura
            time.sleep(0.2)

            # Salir del bucle si se presiona el boton finalizar
            if comun_file.get_Finalizacion == True:
                break

def modo_grabacion_almacenar_informacion(img_mini,img_pov):
    global exit_event
    global keys_number

    # Crear y comenzar un nuevo hilo para el listener combinado
    listener_thread = threading.Thread(target=mouse_and_keyboard_listener)
    listener_thread.start()
    # Esperar hasta que se establezca el evento para salir del bucle
    listener_thread.join()
    
    #exit_event.wait()
    

    # print(f'Las coordenadas finales del mouse son ({mouse_coords["x"]}, {mouse_coords["y"]})')

    moviminento = [int(keys_number),int(mouse_coords["x"]),int(mouse_coords["y"])]
    keys_number = 0

    # Crear DataFrames para cada matriz
    row ={'mini_01': img_mini[0], 'mini_02': img_mini[1], 'mini_03': img_mini[2], 'mini_04': img_mini[3],'mini_05': img_mini[4], 'mouse_final':moviminento}
    row_pov = {'pov_01': img_pov[0], 'pov_02': img_pov[1], 'pov_03': img_pov[2], 'pov_04': img_pov[3],'pov_05': img_pov[4], 'mouse_final':moviminento}

    # guardar_csv(row,row_pov)
    
    return moviminento