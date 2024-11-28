import psutil

def kill_procesos_por_nombre(lista_nombres):
    for nombre in lista_nombres:
        print(f"Buscando procesos con el nombre: {nombre}")
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                # Verifica si el nombre del proceso coincide
                if proc.info['name'] == nombre:
                    pid = proc.info['pid']
                    print(f"Terminando proceso: {nombre} (PID: {pid})")
                    proc.terminate()  # Intenta finalizar el proceso
                    proc.wait(timeout=3)  # Espera a que el proceso termine
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                print(f"Error al intentar terminar el proceso: {nombre}")
                pass

if __name__ == "__main__":

    lista = [
            "firefox","snap-store","anydesk",
            "evolution-alarm-notify","evolution-addressbook-factory","evolution-calendar-factory",
            "evolution-source-registry","update-notifier"
            #,"python3"
            ]

    kill_procesos_por_nombre(lista)
