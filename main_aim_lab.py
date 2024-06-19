
from capturadora_aim_lab import *


DF = pd.DataFrame()

#Yolo
model_yolo = YOLO("modelos/yolov8n.pt")

try:
    aimlab = gw.getWindowsWithTitle("aimlab_tb")[0]
except IndexError:
    print(" 😡 Abra desde Steam Aimlab para poder empezar 😡")


DF = capturar_pantalla(aimlab,model_yolo,DF)


#Guardamos el DF en CSV
DF.to_csv('datos/datos_aim_lab.csv', index=False)



