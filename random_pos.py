import random
import pyautogui  # Necesario para obtener el tamaño de la pantalla

def random_coord_in_center_rect(scale=2/3):
    """
    Devuelve una coordenada aleatoria (x, y) dentro de un rectángulo central
    que ocupa `scale` del ancho y alto total de la pantalla.
    Por defecto: 2/3 del área total.
    """
    screen_width, screen_height = pyautogui.size()

    # Calcular tamaño del rectángulo interno
    rect_width = int(screen_width * scale)
    rect_height = int(screen_height * scale)

    # Calcular el offset para centrar el rectángulo
    offset_x = (screen_width - rect_width) // 2
    offset_y = (screen_height - rect_height) // 2

    # Generar coordenadas aleatorias dentro del rectángulo central
    x = random.randint(offset_x, offset_x + rect_width)
    y = random.randint(offset_y, offset_y + rect_height)

    return x, y

# Ejemplo de uso:
#if __name__ == "__main__":
    #for i in range(5):
        #x, y = random_coord_in_center_rect()
        #print(f"🎯 Random point {i+1}: ({x}, {y})")
