import subprocess
from pynput import keyboard

class MovimientoTeclas:
    def move_mouse(self, x, y):
        subprocess.run(['xdotool', 'mousemove_relative', '--', str(x), str(y)])

    def on_press(self, key):
        try:
            if key == keyboard.Key.up:
                pass  # Puedes agregar una acción aquí
            elif key == keyboard.Key.down:
                subprocess.run(['xdotool', 'key', 'v']) 
            elif key == keyboard.Key.left:
                self.move_mouse(-500, 0)  # Mover a la izquierda
            elif key == keyboard.Key.right:
                self.move_mouse(500, 0)  # Mover a la derecha
            elif key == keyboard.Key.esc:  # Usar "ESC" para salir
                print("Finalizando programa...")
                return False  # Detiene el Listener
        except AttributeError:
            pass

    def on_release(self, key):
        pass


def teclas_direccion_movimiento_pantalla():
    movimientos = MovimientoTeclas()
    # Start listening to the keyboard events
    with keyboard.Listener(on_press=movimientos.on_press, on_release=movimientos.on_release) as listener:
        listener.join()


if __name__ == '__main__':
    print("Movimiento teclas activado...")
    teclas_direccion_movimiento_pantalla()