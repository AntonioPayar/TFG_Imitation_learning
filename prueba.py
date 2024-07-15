import subprocess
from pynput import keyboard

class MovimientoTeclas():
    def move_mouse(self, x, y):
        subprocess.run(['xdotool', 'mousemove_relative', '--', str(x), str(y)])

    def on_press(self, key):
        try:
            if key == keyboard.Key.up:
                print("Arriba")
            elif key == keyboard.Key.down:
                print("Abajo")
            elif key == keyboard.Key.left:
                print("Izquierda")
                self.move_mouse(-500, 0)  # Mover a la izquierda
            elif key == keyboard.Key.right:
                print("Derecha")
                self.move_mouse(500, 0)  # Mover a la derecha
            elif key.char == 'q':
                print("Finalizando programa...")
                return False  # Esto detendrá el listener
        except AttributeError:
            pass

    def on_release(self, key):
        print("levantado")
        pass

def get_mouse_movement():
    movimientos = MovimientoTeclas()
    # Start listening to the keyboard events
    with keyboard.Listener(on_press=movimientos.on_press, on_release=movimientos.on_release) as listener:
        listener.join()

if __name__ == '__main__':
    get_mouse_movement()
