from capturadoras.capturadora_utils import *
import tensorflow as tf
import subprocess
from tensorflow.keras.models import load_model


modelo_mapa = None

def configuracion_gpu_keras(modelo):
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
    def __init__(self,monitor,csv_mini,csv_pov):
        super().__init__(monitor,csv_mini,csv_pov)
        self.vaciar_memoria_temporal()
    
    def vaciar_memoria_temporal(self):
        self.numero_listas = 0
        self.lista_frames_manual_mapa = [None,None,None]
        self.lista_frames_manual_pov = [None,None,None]
        self.lista_url_manual_mapa = [None,None,None]
        self.lista_url_manual_pov = [None,None,None]
        self.lista_moviminetos_manual = [None,None,None]

    def prediccion_img_mapa(self):
        global modelo_mapa
        # Normalizar cada imagen en la lista
        lista_mapa_normalizado = []
        lista_pov_normalizado = []
        #Normalizamos imagenes
        for img_mapa, img_pov in zip(self.lista_img_mini,self.lista_img_pov):
            img_mapa_normalizada = img_mapa / 255.0
            img_pov_normalizada = img_pov / 255.0
            lista_mapa_normalizado.append(img_mapa_normalizada)
            lista_pov_normalizado.append(img_pov_normalizada)

        # Convertir la lista de imágenes normalizadas de nuevo a un array de NumPy
        lista_mapa_normalizado = np.array(lista_mapa_normalizado)
        lista_pov_normalizado = np.array(lista_pov_normalizado)

        # Expandir las dimensiones para que sea compatible con la dimension del batch
        lista_mapa_normalizado = np.expand_dims(lista_mapa_normalizado, axis=0)
        lista_pov_normalizado = np.expand_dims(lista_pov_normalizado, axis=0)

        # Crear un array de NumPy que contenga los dos arrays anteriores
        merge_array = [lista_mapa_normalizado, lista_pov_normalizado]

        # Hacer predicciones de el grupo de imagenes
        prediccion_modelo = modelo_mapa.predict(merge_array)
        # Convertir las probabilidades a etiquetas de clase
        predicted_classes = np.argmax(prediccion_modelo, axis=1)
        return predicted_classes
    

    def mover_raton_prediccion(self,movimiento):
        if movimiento == 0:
            print("Izquierda")
            subprocess.run(['xdotool', 'mousemove_relative', '--', str(-500), str(0)])
        elif movimiento == 1 :
            print("Derecha")
            subprocess.run(['xdotool', 'mousemove_relative', '--', str(500), str(0)])
        elif movimiento == 2 :
            print("Avanza")
    
    def comprobar_movimineto(self):

        if [self.lista_movimientos[0],self.lista_movimientos[1]] != [0,0]:
            return True
        else:
            return False
    

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
    def guardar_frames_previos(self):

        if self.numero_listas < 3:
            self.lista_frames_manual_mapa[self.numero_listas] = self.lista_img_mini
            self.lista_frames_manual_pov[self.numero_listas] = self.lista_img_pov

            self.lista_url_manual_mapa[self.numero_listas] = self.lista_url_img_mini
            self.lista_url_manual_pov[self.numero_listas] = self.lista_url_img_pov

            self.lista_moviminetos_manual[self.numero_listas] = self.lista_movimientos
            self.numero_listas = self.numero_listas + 1
        else:
            self.vaciar_memoria_temporal()
    
    def guardar_modo_manual(self):

        for i in range(self.numero_listas):
            lista_mapa = self.lista_frames_manual_mapa[i]
            lista_pov = self.lista_frames_manual_pov[i]
            lista_movimiento = self.lista_moviminetos_manual[i]

            lista_url_map = self.lista_url_manual_mapa[i]
            lista_url_pov = self.lista_url_manual_pov[i]
            
            #Todos los datos temporales los preparamos y guardamos
            self.preparacion_datos_pandas(lista_mapa,lista_pov,lista_movimiento,lista_url_map,lista_url_pov)
        
        #Eliminamos todos los frames ya guardados
        self.vaciar_memoria_temporal()

    

    def preparacion_datos_pandas(self,lista_mapa,lista_pov,lista_movimiento,lista_url_map,lista_url_pov):

        # Crear DataFrames para cada matriz
        row ={'mini_01': lista_url_map[0], 'mini_02': lista_url_map[1], 'mini_03': lista_url_map[2], 'mini_04': lista_url_map[3],'mini_05': lista_url_map[4], 'mouse_final':str(lista_movimiento)}
        row_pov = {'pov_01': lista_url_pov[0], 'pov_02': lista_url_pov[1], 'pov_03': lista_url_pov[2], 'pov_04': lista_url_pov[3],'pov_05': lista_url_pov[4], 'mouse_final':str(lista_movimiento)}


        for i in range(len(lista_mapa)):
            #Guarda las imágenes JPG
            cv2.imwrite(lista_url_map[i], lista_mapa[i])
            cv2.imwrite(lista_url_pov[i], lista_pov[i])
        
        #Guardamos datos en csv
        self.guardar_csv(row,row_pov)


    def get_screenshot(self):

        for i in range(5):
            self.posicion_i = i
            #print("Imagen..."+str(i))
            img_mini_mapa , img_np = self.cargar_pantalla()

            # Obtiene la fecha y hora actual
            now = datetime.now()
            timestamp = now.strftime("%d-%H-%M-%S-%f")

            #Creamos el nombre de las imgs
            mini_str = f"datos/fine_tuning/mini_mapa/mini_mapa_{timestamp}.jpg"
            pov_str = f"datos/fine_tuning/pov/pov_{timestamp}.jpg"

            #Almacenamos la localizacion de la img
            self.lista_url_img_mini[i] = mini_str
            self.lista_url_img_pov[i] = pov_str
            #Almacenamos la img
            self.lista_img_mini[i] = img_mini_mapa
            self.lista_img_pov[i] = img_np
            #Pausa entre capturas
            time.sleep(0.01)
        print("----------------------------") 


    # Función principal para ejecutar en hilos
    def run(self):

        mouse_thread = threading.Thread(target=self.get_mouse_movement)
        capture_thread = threading.Thread(target=self.get_screenshot)
        
        mouse_thread.start()
        capture_thread.start()

        mouse_thread.join()
        capture_thread.join()

        #Guardamos la lista anterior por si activa el modo manual
        self.guardar_frames_previos()

        if self.comprobar_movimineto() == True:
            self.guardar_modo_manual()

        #Realizamos predicciones sobre el mapa
        prediccion_movimineto = self.prediccion_img_mapa()
        #Ejecutamos la accion
        self.mover_raton_prediccion(int(prediccion_movimineto))

        #Enviamos las imagenes a la interfaz grafica
        comun_file.cola_imagenes_map.put(self.lista_img_mini)
        comun_file.cola_imagenes_pov.put(self.lista_img_pov)
        comun_file.cola_mov_raton.put(self.lista_movimientos)