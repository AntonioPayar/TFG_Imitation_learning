from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import torch
from PIL import Image
import numpy as np
import mss

# GPU use
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Usando el dispositivo: {device}")
#Yolo
yolo = YOLO("modelos/yolov8n.pt")

def cargar_pantalla():
        img_mini_mapa = None
        img_pov = None

        with mss.mss() as sct:
            # Captura el monitor donde esta el juego
            sct_img = sct.grab(sct.monitors[1])
            
            # Convertir la captura en una imagen de PIL
            screenshot = Image.frombytes("RGB", (sct_img.width, sct_img.height), sct_img.rgb)

            #Creamos la imagen pov
            img_pov = np.array(screenshot)
            img_pov = cv2.cvtColor(img_pov, cv2.COLOR_RGB2BGR)


            return img_pov

def imagenes_tiempo_real():
    while True:
        # Captura la pantalla
        img_pov = cargar_pantalla()

        img_pov = prediccione(img_pov)

        # Redimensionar la imagen
        resized_img = cv2.resize(img_pov, (640, 480))
        
        # Mostrar la imagen en una ventana de OpenCV
        cv2.imshow('Screen Capture', resized_img)
        
        # Espera 1 ms y verifica si se presionó la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def prediccione(img):
    global yolo
    # Realizar la predicción
    results = yolo.predict(source=img, show=True, classes=[0],conf=0.5, device=device) 

    # Dibujar los cuadros delimitadores en la imagen
    for result in results:
        for box in result.boxes:
            # Convertir las coordenadas del tensor a enteros
            x1, y1, x2, y2 = box.xyxy[0].int().tolist()
            conf = box.conf[0].item()
            class_id = int(box.cls[0].item())
            label = f"Person: {conf:.2f}"

            # Dibujar el cuadro delimitador y la etiqueta
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return img

if __name__ == '__main__':
    #imagenes_real time
    imagenes_tiempo_real()


