from pynput import mouse
import time
import threading

class MouseMoveDetector(threading.Thread):
    def __init__(self):
        super().__init__()
        self.current_position = (0, 0)
        self.total_displacement = (0, 0)
        self.lock = threading.Lock()
        self.listener = mouse.Listener(on_move=self.on_move)

    def on_move(self, x, y):
        with self.lock:
            # Calcular el desplazamiento
            dx = x - self.current_position[0]
            dy = y - self.current_position[1]
            # Actualizar la posición actual y el desplazamiento total
            self.current_position = (x, y)
            self.total_displacement = (self.total_displacement[0] + dx, self.total_displacement[1] + dy)

    def run(self):
        self.listener.start()
        self.listener.join()

    def capture_displacement(self, interval=1):
        time.sleep(interval)  # Espera durante el intervalo especificado
        movimiento = [None,None]
        with self.lock:
            dx, dy = self.total_displacement
            movimiento = [int(dx),int(dy)]
            # Resetear el desplazamiento para el próximo intervalo
            self.total_displacement = (0, 0)
        self.listener.stop()  # Detener el listener después de capturar el desplazamiento
        print(movimiento)
        return movimiento

# Ejemplo de uso
if __name__ == "__main__":
    detector = MouseMoveDetector()
    detector.start()
    detector.capture_displacement()
