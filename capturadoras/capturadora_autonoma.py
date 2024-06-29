from capturadoras.capturadora_utils import *
import tensorflow as tf
from tensorflow.keras.models import load_model


modelo_mapa = None

def configuracion_gpu_keras(self,modelo):
    global modelo_mapa
    # Configurar para usar la GPU
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)  
                print("Modelo y GPU preparada ..")
            modelo_mapa = load_model(modelo)     
        except RuntimeError as e:
            print(e)


class CapturadoraAutonoma(Capturadora):
    def __init__(self,monitor):
        super().__init__(monitor)
        self.movimineto_previo_detectado = [0,0]
        self.bool_movimiento_detectado = False
        self.lista_frames_manual_mapa = [None,None,None]
        self.lista_frames_manual_pov = [None,None,None]

        self.lista_url_img_mini = [None, None,None, None,None]
        self.lista_img_mini = [None, None,None, None,None]
        self.lista_url_img_pov = [None, None,None, None,None]
        self.lista_img_pov = [None, None,None, None,None]
        self.lista_movimientos = [None, None,None, None,None]
        self.lisa_moviminetos = [None,None]
        self.numero_listas = 0

    def prediccion_img_mapa(self):
        global modelo_mapa
        # Normalizar cada imagen en la lista
        lista_imagenes_normalizadas = []
        #Normalizamos imagenes
        for imagen in self.lista_img_mini:
            imagen_normalizada = imagen / 255.0
            lista_imagenes_normalizadas.append(imagen_normalizada)

        # Convertir la lista de imágenes normalizadas de nuevo a un array de NumPy
        lista_imagenes_normalizadas = np.array(lista_imagenes_normalizadas)
        # Expandir las dimensiones para que sea compatible con la dimension del batch
        lista_imagenes_normalizadas = np.expand_dims(lista_imagenes_normalizadas, axis=0)

        # Hacer predicciones de el grupo de imagenes
        prediccion_modelo = modelo_mapa.predict(lista_imagenes_normalizadas)
        #Convertimos las predicciones a int64
        prediccion_modelo = prediccion_modelo.astype(np.int64)
        return prediccion_modelo
    

    def mover_raton_prediccion(self,delta_x, delta_y):
        mouse = Controller()
        mouse.move(delta_x, delta_y)
        print(f"Ratón movido a: {delta_x}, {delta_y}")
    
    def comprobar_movimineto(self,movimiento):

        if movimiento != self.movimineto_previo_detectado:
            self.movimineto_previo_detectado = movimiento
            self.bool_movimiento_detectado = True
        else:
            self.bool_movimiento_detectado = False
    

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
    def guardar_frames_previos(self,lista_img_mini,lista_img_pov,moviminento):

        if self.numero_listas < 3:
            self.lista_frames_manual_mapa[self.numero_listas] = lista_img_mini
            self.lista_frames_manual_pov[self.numero_listas] = lista_img_pov
            self.lisa_moviminetos[self.numero_listas] = moviminento
            self.numero_listas = self.numero_listas + 1
        else:
            self.lista_frames_manual_mapa = [None,None,None]
            self.lista_frames_manual_pov = [None,None,None]
            self.lisa_moviminetos = [None,None,None]
            self.numero_listas = 0

    def get_screenshot(self):

        for i in range(5):
            self.posicion_i = i
            #print("Imagen..."+str(i))
            img_mini_mapa , img_np = self.cargar_pantalla()

            # Obtiene la fecha y hora actual
            now = datetime.now()
            timestamp = now.strftime("%d-%H-%M-%S-%f")

            #Creamos el nombre de las imgs
            mini_str = f"datos/grabacion/mini_mapa/mini_mapa_{timestamp}.jpg"
            pov_str = f"datos/grabacion/pov/pov_{timestamp}.jpg"

            #Guarda las imágenes JPG
            #cv2.imwrite(mini_str, img_mini_mapa)
            #cv2.imwrite(pov_str, img_np)

            #Almacenamos la localizacion de la img
            self.lista_url_img_mini[i] = mini_str
            self.lista_url_img_pov[i] = pov_str
            #Almacenamos la img
            self.lista_img_mini[i] = img_mini_mapa
            self.lista_img_pov[i] = img_np
            #Pausa entre capturas
            time.sleep(0.2)
        print("----------------------------") 


    # Función principal para ejecutar en hilos
    def run(self):

        mouse_thread = threading.Thread(target=self.get_mouse_movement)
        capture_thread = threading.Thread(target=self.get_screenshot)
        
        mouse_thread.start()
        capture_thread.start()

        mouse_thread.join()
        capture_thread.join()

        #Realizamos predicciones sobre el mapa
        prediccion_movimineto = self.prediccion_img_mapa()
        #Ejecutamos la accion
        self.mover_raton_prediccion(int(prediccion_movimineto[0][0]),int(prediccion_movimineto[0][1]))

        #Enviamos las imagenes a la interfaz grafica
        comun_file.cola_imagenes_map.put(self.lista_img_mini)
        comun_file.cola_imagenes_pov.put(self.lista_img_pov)
        comun_file.cola_mov_raton.put(self.lista_movimientos)