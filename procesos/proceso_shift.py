from Xlib.ext import xtest
from Xlib import X, display
import time

# Función para presionar teclas 'W' y 'Shift_L' usando Xlib
def press_keys_xlib():
    # Conectar al servidor X
    d = display.Display()
    root = d.screen().root

    # Obtener el código de tecla para 'W'
    keycode_w = d.keysym_to_keycode(ord('W'))  # 'W' may need to be uppercase

    # Código de tecla para Shift izquierda (Shift_L)
    keycode_shift_l = 50  # Este número puede variar según el layout del teclado

    try:
        print("Presionando teclas Shift + W. Pulsa Ctrl+C para detener.")
        while True:  # Bucle principal
            # Simular presión de teclas 'W' y 'Shift_L'
            xtest.fake_input(d, X.KeyPress, keycode_w)
            xtest.fake_input(d, X.KeyPress, keycode_shift_l)
            d.sync()
            time.sleep(0.1)  # Pequeño tiempo de espera para evitar uso excesivo de CPU
    except KeyboardInterrupt:
        print("Finalizando...")
    finally:
        # Soltar las teclas 'W' y 'Shift_L' al interrumpir el script
        xtest.fake_input(d, X.KeyRelease, keycode_w)
        xtest.fake_input(d, X.KeyRelease, keycode_shift_l)
        d.sync()

if __name__ == '__main__':
    print("Movimiento Shift activado...")
    press_keys_xlib()
