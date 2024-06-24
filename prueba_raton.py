import threading
from pynput import mouse, keyboard

class MouseMoveDetector(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.mouse_listener = mouse.Listener(on_move=self.on_move)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.current_key = None

    def on_move(self, x, y):
        print(f"Movimiento detectado en: ({x}, {y})")
        if self.current_key:
            print(f"Tecla presionada: {self.current_key}")
        self.running = False
        self.mouse_listener.stop()  # Detener el listener del ratón
        self.keyboard_listener.stop()  # Detener el listener del teclado

    def on_press(self, key):
        try:
            if key.char in ['w', 'a', 's', 'd']:
                self.current_key = key.char
        except AttributeError:
            pass

    def run(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()
        while self.running:
            pass  # Mantener el hilo vivo mientras `self.running` sea True

while True:
    # Crear y empezar el hilo
    detector = MouseMoveDetector()
    detector.start()

    # Esperar a que el hilo termine
    detector.join()

