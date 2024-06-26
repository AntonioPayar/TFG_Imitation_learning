from capturadoras.capturadora_utils import *
import tensorflow as tf
from tensorflow.keras.models import load_model

lista_frames_manual_mapa = [None,None,None]
lista_frames_manual_pov = [None,None,None]
lisa_moviminetos = [None,None,None]
numero_listas = 0

movimineto_previo_detectado = [0,0,0]
bool_movimiento_detectado = False

#Modelos
modelo_mapa = None

def configuracion_gpu_keras():
    global modelo_mapa
    # Configurar para usar la GPU
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)  

            modelo_mapa = load_model('modelos/modelo_mapa.h5')     
            print("GPU preparada ...")
            print("Modelo Mapa preparado ...")
        except RuntimeError as e:
            print(e)

def prediccion_img_mapa(lista_img):

    # Normalizar cada imagen en la lista
    lista_imagenes_normalizadas = []
    #Normalizamos imagenes
    for imagen in lista_img:
        imagen_normalizada = imagen / 255.0
        lista_imagenes_normalizadas.append(imagen_normalizada)

    # Convertir la lista de imágenes normalizadas de nuevo a un array de NumPy
    lista_img = np.array(lista_imagenes_normalizadas)
    # Expandir las dimensiones para que sea compatible con la dimension del batch
    lista_img = np.expand_dims(lista_img, axis=0)

    # Hacer predicciones de el grupo de imagenes
    return modelo_mapa.predict(lista_img)

def modo_autonomo_moviminetos():

    configuracion_gpu_keras()
    # Crear una instancia del controlador del ratón
    time.sleep(5)       #Esperamos unos segundos hasta que empiece la partida

    lista_url_img_mini = [None, None,None, None,None]
    lista_img_mini = [None, None,None, None,None]
    lista_url_img_pov = [None, None,None, None,None]
    lista_img_pov = [None, None,None, None,None]
    lista_movimientos = [None, None,None, None,None]

    i = 0
    # ------------------------------Iniciar hilo para mantener las teclas presionadas
    comun_file.key_thread.start()

    while True:
        
        img_mini_mapa , img_np = cargar_pantalla()
        lista_movimientos[i] = captura_movimineto_raton()  #Captura el movimineto en este frame

        if img_mini_mapa.size != 0 and img_np.size != 0:

            # Obtiene la fecha y hora actual
            now = datetime.now()
            timestamp = now.strftime("%d-%H-%M-%S")

            mini_str = f"datos/fine_tuning/mini_mapa/mini_mapa_{timestamp}.jpg"
            pov_str = f"datos/fine_tuning/pov/pov_{timestamp}.jpg"

            # -------------------------Guarda las imágenes redimensionadas en formato JPG
            #cv2.imwrite(mini_str, img_mini_mapa)
            #cv2.imwrite(pov_str, img_np)

            #Almacenamos la localizacion de la img
            lista_url_img_mini[i] = mini_str
            lista_url_img_pov[i] = pov_str

            #Almacenamos la img
            lista_img_mini[i] = img_mini_mapa
            lista_img_pov[i] = img_np

            if i < 4:
                i = i + 1
            else:
                #print(lista_movimientos)
                media_movimientos = media(lista_movimientos)

                prediccion = prediccion_img_mapa(lista_img_mini)

                mover_raton_prediccion(int(prediccion[0][0]),int(prediccion[0][1]))
                time.sleep(0.05)

                comun_file.cola_imagenes_map.put(lista_img_mini)
                comun_file.cola_imagenes_pov.put(lista_img_pov)
                comun_file.cola_mov_raton.put(media_movimientos)    #Enviamos la actividad del usuario a la interfaz grafica

                #comprobar_movimineto(media_movimientos)
                #guardar_frames_previos(lista_img_mini,lista_img_pov,media_movimientos)
                
                i = 0
                lista_img_mini = [None, None,None, None,None]
                lista_img_pov = [None, None,None, None,None]
                lista_movimientos = [None, None,None, None,None]
            
            # Esperar 0.2 segundos antes de la próxima captura
            time.sleep(comun_file.intervalo_captura)

            # Salir del bucle si se presiona el boton finalizar
            if comun_file.get_Finalizacion == True:
                break
    #---------------- Detener el hilo de manera controlada
    comun_file.key_thread.join()
    
def comprobar_movimineto(movimiento):
    global movimineto_previo_detectado
    global bool_movimiento_detectado

    if movimiento != movimineto_previo_detectado:
        movimineto_previo_detectado = movimiento
        bool_movimiento_detectado = True
    else:
        bool_movimiento_detectado = False


    """
    Funcion que se encarga de guardar los ultimos segundos antes de activar el modo manual
    
    Almacenamos 3 listas de 5 framas previos
    Si el usuario activa el modo manual guardamos las imagens y la ruta en csv 

    Si el usuario no activa el modo manual no guardamos nada y borramos las imagenes y las sustituimos 
    por la siguientes

    Parámetros:
    lista_img_mini (list): Lista con los 5 frames capturados del minimapa
    lista_img_pov (list): Lista con los 5 frames capturados del pov
    moviminento (list): movimiento realizado en esos 5 frames
    """
def guardar_frames_previos(lista_img_mini,lista_img_pov,moviminento):
    global lista_frames_manual_mapa
    global lista_frames_manual_pov
    global lisa_moviminetos
    global numero_listas

    if numero_listas < 3:
        print(numero_listas)
        lista_frames_manual_mapa[numero_listas] = lista_img_mini
        lista_frames_manual_pov[numero_listas] = lista_img_pov
        lisa_moviminetos[numero_listas] = moviminento
        numero_listas = numero_listas + 1
    else:
        lista_frames_manual_mapa = [None,None,None]
        lista_frames_manual_pov = [None,None,None]
        lisa_moviminetos = [None,None,None]
        numero_listas = 0   


    """
    Funcion que se encarga de monitorizar el raton y el teclado para activar el modo manual
    
    """