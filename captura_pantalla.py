import mss
import mss.tools
from PIL import Image

def captura_pantalla():
    """
    Toma una captura de pantalla y la muestra usando PIL.
    """
    # Crear una instancia de mss
    with mss.mss() as sct:
        # Obtener las dimensiones de la pantalla principal
        monitor = sct.monitors[1]

        # Capturar la pantalla
        captura = sct.grab(monitor)

        # Convertir la captura a un objeto Image de PIL
        img = Image.frombytes('RGB', captura.size, captura.rgb)

        # Recortar 10 cm de la parte superior
        width, height = img.size
        img = img.crop((0, 280, width, height))

        # Mostrar la imagen
        img.show()

# Ejemplo de uso
captura_pantalla()
