import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
import multiprocessing


def zoom_frame_minimapa(frame,zoom_factor):

    # Obtiene las dimensiones del fotograma
    height, width, _ = frame.shape

    # Calcula las dimensiones del área de zoom
    zoom_height, zoom_width = height // zoom_factor, width // zoom_factor

    horizontal_offset = 70 
    vertical_offset = 53
    right_margin = 87

    # Calcula las coordenadas del área de zoom, incluyendo el desplazamiento horizontal
    x_start = horizontal_offset
    x_end = (x_start + zoom_width)-right_margin
    y_start = vertical_offset
    y_end = (y_start + zoom_height)+60

    # Recorta el área de zoom basado en la esquina seleccionada 
    cropped_frame = frame[y_start:y_end, x_start:x_end]

    return cropped_frame

def procesar_frames_minimapa():
    video_path = 'datos\Black Ops Sniper Challenge.mp4'  
    cap = cv2.VideoCapture(video_path)

    #Yolo
    yolo_segmentation = YOLO("modelos\yolov8n-seg.pt")

    names = yolo_segmentation.model.names

    if not cap.isOpened():
        print("Error al abrir el video")
        exit()

    ventanas = ["mini_01","mini_02","mini_03","mini_04","mini_05"]
    i = 0

    while cap.isOpened():
        # Lee un fotograma
        ret, frame = cap.read()
        if not ret:
            print("No se pueden obtener más fotogramas (fin del video o error)")
            break

        frame = zoom_frame_minimapa(frame,6)

        # Crea una ventana
        cv2.namedWindow(ventanas[i], cv2.WINDOW_NORMAL)
        cv2.resizeWindow(ventanas[i], 215, 215)  # Ajusta el tamaño de la ventana

        # Redimensiona el fotograma para que se ajuste a la ventana
        resized_frame = cv2.resize(frame, (215, 215))

        # Muestra el fotograma procesado
        cv2.imshow(ventanas[i], resized_frame)

        if i < 4:
            i = i + 1
        else:
            i = 0

        # Presiona 'q' para salir
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Libera el objeto captura y cierra todas las ventanas
    cap.release()
    cv2.destroyAllWindows()

def procesar_frames_pov():
    video_path = 'datos\Black Ops Sniper Challenge.mp4'  
    cap = cv2.VideoCapture(video_path)

    #Yolo
    yolo_segmentation = YOLO("modelos\yolov8n-seg.pt")

    names = yolo_segmentation.model.names

    if not cap.isOpened():
        print("Error al abrir el video")
        exit()

    ventanas = ["pov_01","pov_02","pov_03","pov_04","pov_05"]
    i = 0

    while cap.isOpened():
        # Lee un fotograma
        ret, frame = cap.read()
        if not ret:
            print("No se pueden obtener más fotogramas (fin del video o error)")
            break

        # Crea una ventana
        cv2.namedWindow(ventanas[i], cv2.WINDOW_NORMAL)
        cv2.resizeWindow(ventanas[i], 360, 240)  # Ajusta el tamaño de la ventana

        # Redimensiona el fotograma para que se ajuste a la ventana
        resized_frame = cv2.resize(frame, (1280, 720))

        # Muestra el fotograma procesado
        cv2.imshow(ventanas[i], resized_frame)

        if i < 4:
            i = i + 1
        else:
            i = 0

        # Presiona 'q' para salir
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Libera el objeto captura y cierra todas las ventanas
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Crear procesos
    proceso_minimap = multiprocessing.Process(target=procesar_frames_minimapa)
    proceso_frame = multiprocessing.Process(target=procesar_frames_pov)

    # Iniciar procesos
    proceso_minimap.start()
    proceso_frame.start()

    # Esperar a que los procesos terminen
    proceso_minimap.join()
    proceso_frame.join()

