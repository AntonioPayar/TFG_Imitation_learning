import pygetwindow as gw
from PIL import ImageGrab ,ImageDraw
import numpy as np
import cv2
from ultralytics import YOLO
from PIL import Image
from pynput.mouse import Listener, Button
import numpy as np
import pandas as pd
import win32api, win32con, win32gui
import time
from keras.models import load_model
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0' 

def capturar_pantalla(aimlab,model_yolo,DF):

    # Asegúrate de que la ventana esté visible
    if aimlab.isMinimized:
        aimlab.restore()

    # Trae la ventana al frente
    aimlab.activate()


    while True:
        # Obtiene las coordenadas de la ventana
        left, top, right, bottom = aimlab.left, aimlab.top, aimlab.right, aimlab.bottom
        
        # Ajustar las coordenadas
        top = top + 100
        bottom = bottom - 100

        # Captura la pantalla en las coordenadas de la ventana
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))

        # Convierte la imagen a un array de numpy
        img_np = np.array(screenshot)

        # Convierte de BGR a RGB
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Redimensiona la imagen a un tamaño más pequeño 
        img_resized = cv2.resize(img_np, 
                                 (img_np.shape[1] // 2,
                                  img_np.shape[0] // 2))

        DF,img_resized = detectar_objetos(img_resized,
                                          img_np.shape[1]/2,
                                          img_np.shape[0]/2,
                                          model_yolo,
                                          DF)

        # Muestra la imagen en una ventana de OpenCV
        cv2.imshow("q para salir", img_resized)

        # Salir del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    return DF


def detectar_objetos(img,centro_x,centro_y,model_yolo,DF):

    #Si tenemos modelo para disparar lo cargamos
    modelo_aim = load_model('modelos/modelo.h5')
    modelo_aim.compile(optimizer='adam', loss='mean_squared_error')

    results = model_yolo(img) 
    # Load the original image
    image = img 

    results = results[0]

    if len(results.boxes) > 0:
        distancias = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy.tolist()[0]  # Obtenemos las coordenadas de la caja
            conf = box.conf.item()  # Obtenemos la confianza
            class_id = int(box.cls.item())  # Obtenemos el ID de la clase

            if class_id == 32: #Solo queremos detectar balones
                # Dibujamos la caja de detección en la imagen
                color = (0, 255, 0)  # Color verde
                label = f"Clase {class_id} - Confianza: {conf:.2f}"  # Etiqueta con la clase y la confianza

                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)  # Dibujamos la caja     
                aim_x = ((x1 + x2)/2)
                aim_y = ((y1 + y2)/2)

                cv2.circle(image, (int(centro_x),int(centro_y)), 5, (255, 165, 0), thickness=10)
                cv2.circle(image, (int(aim_x),int(aim_y)), 1, (0, 0, 255), thickness=1)
                cv2.putText(image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)  # Dibujamos la etiqueta

                #shot_x , shot_y = disparar_sin_modelo(int(aim_x),int(aim_y),int(centro_x),int(centro_y))
                shot_x , shot_y = disparar_modelo(int(x1), int(y1),
                                                  int(x2), int(y2),
                                                  modelo_aim)
                
                # DF = insertar_df(int(x1), int(y1),
                #                  int(x2), int(y2),
                #                  DF,
                #                  shot_x,shot_y)

    return DF,image

def disparar_sin_modelo(aim_x,aim_y,centro_x,centro_y):
    # Calcula la diferencia en coordenadas entre el centro de la bounding box y el centro de la pantalla
    x = int(aim_x - centro_x / 2)
    y = int(aim_y - centro_y / 2)

    # Move mouse and shoot
    scale = 1
    x = int(x * scale)
    y = int(y * scale)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
    time.sleep(0.05)

    # ------ Hacer Click------ 
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    # ------ Hacer Click------
    return x , y

def disparar_modelo(box_x1,box_y1,
                    box_x2,box_y2,
                    modelo):
    
    input_data = np.array([[box_x1, box_y1, box_x2, box_y2, abs(box_x2 - box_x1) * abs(box_y2 - box_y1)]])
    
    # Hacer predicciones con el modelo
    predicciones = modelo.predict(input_data)


    # ------ Mover Raton------ 
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, predicciones[0][0], predicciones[0][1], 0, 0)
    time.sleep(0.05)

    # ------ Hacer Click------ 
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, predicciones[0][0], predicciones[0][1], 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, predicciones[0][0], predicciones[0][1], 0, 0)
    # ------ Hacer Click------
    return predicciones[0][0],predicciones[0][1]


def insertar_df(box_x1,box_y1,
                box_x2,box_y2,
                DF ,
                shot_x ,shot_y):
    
    area = abs(box_x2 - box_x1) * abs(box_y2 - box_y1)

    # Añadir datos al DataFrame
    row = {'box_x1': box_x1, 'box_y1': box_y1, 'box_x2': box_x2, 'box_y2': box_y2, 'area': area ,'mouse_final':[int(shot_x),int(shot_y)]}

    # Create a DataFrame from the row
    row_df = pd.DataFrame([row])
    # Append the row DataFrame to the main DataFrame
    DF = pd.concat([DF, row_df], ignore_index=True)

    return DF

