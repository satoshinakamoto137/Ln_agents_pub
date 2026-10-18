import button_searcher as but
import cv2
import time
import os
import ocr_functs as ocr

def search_4_current_element(view):
    results = []

    for idx, (name, asset) in enumerate([
        ("key_fill", "./assets/key_fill.png"),
        ("multi_select", "./assets/multi-select.png"),
        ("select_circle", "./assets/circle-select.png"),
        ("select_circle_fill", "./assets/circle-select_fill.png")
    ], start=1):
        found, t_f, b_r, score = detect_element_and_highlight(
            screenshot_path=view,
            element_path=asset,
            output_path=f'./assets/debug_{name}.png',
            threshold=0.8,
            debug=True
        )
        normalized_name = "select_circle" if name == "select_circle_fill" else name   #define normalized_name
        normalized_idx = 3 if name == "select_circle_fill" else idx  #fill is the same than 3 element

        #results.append((name, idx, score, found, t_f, b_r))
        results.append((normalized_name, normalized_idx, score, found, t_f, b_r))

    # Keep only detected elements
    results = [r for r in results if r[3]]
    if not results:
        print("No element detected❌")
        return 0, None, None, None

    # Pick the highest score
    best = max(results, key=lambda x: x[2])
    print(f"Best match: {best[0]} with score {best[2]:.4f}")

    # Crop the question text above the detected element
    '''
    crop_question_text_square(
        screenshot_path=view,
        t_f=best[4],
        b_r=best[5],
        square_height=60,
        square_length=400,
        output_name=f"q_text_{best[0]}.png"
    )
    '''
    return best[0], best[1], best[4], best[5]  # type index, top_left, bottom_right


def search_4_key_fill(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/key_fill.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8
    )
    return found,t_f, b_r

def search_4_multi_select(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/multi-select.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8
    )
    return found, t_f, b_r

def search_4_select_circle(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/circle-select.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8
    )
    return found, t_f, b_r

def search_4_selected_next(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/selected_next.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8,
        debug=True
    )
    return found, t_f, b_r

def search_4_ssubmit_app(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/ssub.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8,
        debug=True
    )
    return found, t_f, b_r

def search_4_sreview(view):
    found, t_f, b_r, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/srev.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8,
        debug=True
    )
    return found, t_f, b_r

def detect_element_and_highlight(screenshot_path, element_path, output_path, threshold=0.8, debug=True):
    screenshot = cv2.imread(screenshot_path)
    element = cv2.imread(element_path)

    if screenshot is None or element is None:
        raise FileNotFoundError(f"No se pudo cargar {screenshot_path} o {element_path}")

    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    element_gray = cv2.cvtColor(element, cv2.COLOR_BGR2GRAY)

    # Template matching
    result = cv2.matchTemplate(screenshot_gray, element_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    h, w = element_gray.shape
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # Extraer región encontrada
    matched_region = screenshot_gray[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

    # Calcular diferencia exacta
    if matched_region.shape == element_gray.shape:
        diff = cv2.absdiff(matched_region, element_gray)
        non_zero_count = cv2.countNonZero(diff)
        match_ratio = 1 - (non_zero_count / (w * h))
    else:
        match_ratio = 0

    # Debug info
    if debug:
        print(f"[DEBUG] Element: {os.path.basename(element_path)}")
        print(f"        Max Val (template match): {max_val:.4f}")
        print(f"        Match Ratio (pixel diff): {match_ratio:.4f}")
        debug_path = f"./debug_{os.path.basename(element_path)}"
        cv2.imwrite(debug_path, matched_region)
        print(f"        Saved matched region to: {debug_path}")

    # Decisión final
    if max_val >= threshold and match_ratio >= 0.98:
        cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 255), 3)
        cv2.imwrite(output_path, screenshot)
        return True, top_left, bottom_right, max_val
    else:
        return False, None, None, max_val
    
def search_4_any(view, elements):
    """
    Tries to detect any matching UI element in a screenshot from a list of target elements.

    Parameters:
    - view (str): Path to the screenshot image where elements will be searched.
    - elements (List[Tuple[str, str]]): A list of tuples in the format (label, element_path),
      where `label` is a name/identifier for the element, and `element_path` is the path
      to the PNG file that represents the UI element to detect.

    Returns:
    - found (bool): True if any element is found, False otherwise.
    - label (str or None): The label of the detected element. None if no match found.
    - top_left (Tuple[int, int] or None): Top-left corner of the matched region. None if not found.
    - bottom_right (Tuple[int, int] or None): Bottom-right corner of the matched region. None if not found.
    - score (float or None): Template matching score of the best match. None if no match found.
    """
    for label, element_path in elements:
        found, t_f, b_r, score = detect_element_and_highlight(
            screenshot_path=view,
            element_path=element_path,
            output_path='./assets/formulary_state.png',
            threshold=0.8,
            debug=True
        )
        if found:
            print(f"[INFO] Match found: {label} (score: {score:.4f})")
            return True, label, t_f, b_r, score

    print("[INFO] No match found for any element.")
    return False, None, None, None, None

def blue_ending_element_detection(screenshot_path):
    """
    Runs multi-element detection on the provided screenshot.
    This function is for identify the presence of the blue continuation buttons.

    Parameters:
    - screenshot_path (str): Path to the screenshot to analyze.

    Returns:
    - Tuple: (found, label, top_left, bottom_right, score)
    """
    elements_to_check = [
        ("selected_next", "./assets/selected_next.png"),
        ("s_submit_app", "./assets/ssub.png"),
        ("s_review", "./assets/srev.png")
    ]

    found, label, top_left, bottom_right, score = search_4_any(screenshot_path, elements_to_check)

    if found:
        print(f"Element '{label}' found at {top_left} with score {score:.4f}")
    else:
        print("No element matched.")

    return found, label, top_left, bottom_right, score

def additional_Q_element_detection(screenshot_path):
    """
    Runs multi-element detection on the provided screenshot.
    This function is for identify the presence of the AQ continuation buttons.

    Parameters:
    - screenshot_path (str): Path to the screenshot to analyze.

    Returns:
    - Tuple: (found, label, top_left, bottom_right, score)
    """
    elements_to_check = [
        ("A_Q_Eng", "./assets/AQ_Eng.png"),
        ("A_Q_Spa", "./assets/AQ_Spa.png")
    ]

    found, label, top_left, bottom_right, score = search_4_any(screenshot_path, elements_to_check)

    if found:
        print(f"Element '{label}' found at {top_left} with score {score:.4f}")
    else:
        print("No element matched.")

    return found, label, top_left, bottom_right, score

def cancel_palo_detection(screenshot_path):
    """
    Runs multi-element detection on the provided screenshot.
    This function is for identify the presence of the AQ continuation buttons.

    Parameters:
    - screenshot_path (str): Path to the screenshot to analyze.

    Returns:
    - Tuple: (found, label, top_left, bottom_right, score)
    """
    elements_to_check = [
        ("Follow palo", "./assets/palo.png")
    ]

    found, label, top_left, bottom_right, score = search_4_any(screenshot_path, elements_to_check)

    if found:
        print(f"Element '{label}' found at {top_left} with score {score:.4f}")
    else:
        print("No element matched.")

    return found, label, top_left, bottom_right, score

def crop_text_square_2points(screenshot_path, t_f, b_r, output_name="debug_ans_crop.png"):
    """
    Recorta un rectángulo de una imagen entre dos puntos (esquina superior izquierda y esquina inferior derecha)
    y guarda el resultado como imagen.

    Args:
        screenshot_path (str): Ruta a la imagen original.
        t_f (tuple): Coordenada (x1, y1) superior izquierda.
        b_r (tuple): Coordenada (x2, y2) inferior derecha.
        output_name (str): Nombre de archivo para guardar el crop.
    
    Returns:
        str: Ruta del archivo guardado.
    """
    print(f"[INFO] Cropping from {t_f} to {b_r}...")

    img = cv2.imread(screenshot_path)
    x1, y1 = t_f
    x2, y2 = b_r

    # Crop del área especificada
    cropped = img[y1:y2, x1:x2]

    # Guardar el resultado
    cv2.imwrite(output_name, cropped)
    print(f"[INFO] Cropped image saved to: {output_name}")

    return output_name

def crop_text_square_simple(screenshot_path, t_f, b_r, square_height, square_length, output_name="question_crop.png"):
    """
    Crops the question text area above a detected form element and saves the image.
    
    Args:
        screenshot_path (str): Path to the screenshot file.
        t_f (tuple): (x, y) top-left coordinates of the detected element.
        b_r (tuple): (x, y) bottom-right coordinates of the detected element.
        square_height (int): Height of the crop area.
        square_length (int): Width of the crop area.
        output_name (str): File name to save in ./assets/.
    """
    img = cv2.imread(screenshot_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar {screenshot_path}")

    x1, y1 = t_f
    # For question text above the element, shift upward by square_height
    y1_crop = max(0, y1 - square_height)
    x1_crop = x1
    x2_crop = min(img.shape[1], x1_crop + square_length)
    y2_crop = y1

    # Crop the area
    cropped = img[y1_crop:y2_crop, x1_crop:x2_crop]

    # Draw rectangle on a copy for debug
    debug_img = img.copy()
    cv2.rectangle(debug_img, (x1_crop, y1_crop), (x2_crop, y2_crop), (0, 255, 255), 2)

    # Save both the cropped and debug images
    cropped_path = os.path.join("./assets", output_name)
    debug_path = os.path.join("./assets", f"debug_{output_name}")
    cv2.imwrite(cropped_path, cropped)
    cv2.imwrite(debug_path, debug_img)

    print(f"[INFO] Question text cropped and saved to: {cropped_path}")
    print(f"[DEBUG] Highlighted image saved to: {debug_path}")

    return cropped_path

def crop_text_square_with_direction(screenshot_path, t_f, b_r, square_height, square_length, output_name="question_crop.png"):
    img = cv2.imread(screenshot_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar {screenshot_path}")

    x1, y1 = t_f

    # Upward crop for question text
    y1_crop = max(0, y1 - square_height)
    y2_crop = y1

    # Handle direction for square_length
    if square_length > 0:
        x1_crop = x1
        x2_crop = min(img.shape[1], x1 + square_length)
    else:
        x1_crop = max(0, x1 + square_length)  # going left
        x2_crop = x1

    # Prevent invalid crop
    if x2_crop <= x1_crop or y2_crop <= y1_crop:
        print(f"[ERROR] Invalid crop coordinates: ({x1_crop},{y1_crop}) to ({x2_crop},{y2_crop})")
        return None

    cropped = img[y1_crop:y2_crop, x1_crop:x2_crop]

    # Draw debug rectangle
    debug_img = img.copy()
    cv2.rectangle(debug_img, (x1_crop, y1_crop), (x2_crop, y2_crop), (0, 255, 255), 2)

    cropped_path = os.path.join("./assets", output_name)
    debug_path = os.path.join("./assets", f"debug_{output_name}")
    cv2.imwrite(cropped_path, cropped)
    cv2.imwrite(debug_path, debug_img)

    print(f"[INFO] Question text cropped and saved to: {cropped_path}")
    print(f"[DEBUG] Highlighted image saved to: {debug_path}")

    return cropped_path

def crop_by_element(view, element_name, element_type, t_f, b_r):
    '''
    Crop the question text area based on the detected element type. using t_f as main reference.
    '''
    if element_type == 1: # fill
        gap = (0, 0)
        t_f = (t_f[0] + gap[0], t_f[1] + gap[1])
        cropped_path = crop_text_square_with_direction(view, t_f, b_r, 37, -670, f"q_text_{element_name}.png")
    elif element_type == 2: # multi
        gap = (30, 0)  #Move a little to left side 
        t_f = (t_f[0] + gap[0], t_f[1] + gap[1])
        cropped_path = crop_text_square_with_direction(view, t_f, b_r, 50, -695, f"q_text_{element_name}.png")
    elif element_type == 3: # circle
        gap = (0, 0)
        t_f = (t_f[0] + gap[0], t_f[1] + gap[1])
        cropped_path = crop_text_square_with_direction(view, t_f, b_r, 35, 650, f"q_text_{element_name}.png")

    return cropped_path

def get_element_n_text(view):  # this function just works for one and two type questions.
    """
    Detecta el elemento actual, recorta el área de la pregunta y extrae su texto por OCR.
    
    Args:
        view (str): Ruta de la captura de pantalla.
    
    Returns:
        tuple: (element_type (int), question_text (str))
    """
    print("[INFO] Searching for current element...")
    element_name, element_type, t_f, b_r = search_4_current_element(view)

    # Verificar si no se detectó ningún elemento
    if element_type is None or t_f is None or b_r is None:
        print("[WARNING] No se detectó ningún elemento en la imagen 😢. Continuando sin procesar OCR.")
        return None, None

    print(f"[INFO] Detected type: {element_type}, Coordinates: {t_f} to {b_r}")

    cropped_path = crop_by_element(
        view,
        element_name,
        element_type,
        t_f=t_f,
        b_r=b_r,
    )
    question_text = ocr.get_text_easyocr(cropped_path, lang=["en", "es"])
    print(f"[INFO] Extracted question text: {question_text}")

    return element_type, question_text, t_f, b_r

def get_answer_from_crop(view, t_f, b_r):
    """
    corta el area de respuesta y Obtiene la respuesta de un área recortada de la imagen.
    """
    ans_crop_img = crop_text_square_2points(view, t_f, b_r)
    ans_4_cropped = ocr.get_text_easyocr(ans_crop_img, lang=["en", "es"])  # ✅ lista
    print(f"[INFO] 📜 Extracted answer text: {ans_4_cropped}")

    return ans_4_cropped

def close_q2_element(t_f, b_r, view):
    """
    Encuentra la esquina superior izquierda de un elemento tipo 2 box,
    siguiendo el borde negro desde t_f.

    Args:
        t_f (tuple): Coordenada inicial cerca del borde (x, y)
        b_r (tuple): Coordenada inferior derecha (no usada en este método)
        view (str): Ruta de la imagen
    
    Returns:
        tuple: Coordenada (x, y) de la esquina superior izquierda
    """
    print("[INFO] Starting search for top-left corner of Q2 box...")
    img = cv2.imread(view)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Binarizamos para detectar bien los bordes
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Invertimos: negro será 0, blanco será 255
    binary_inv = cv2.bitwise_not(binary)

    x, y = t_f
    height, width = binary_inv.shape

    # 💥 Paso 1: Subir mientras sea blanco
    while y > 0 and binary_inv[y, x] < 10:  # sigue subiendo si es blanco
        y -= 1
    
    # Cuando encontró negro (borde), cambia dirección 👉
    # 💥 Paso 2: Ir a la izquierda mientras sea negro
    while x > 0 and binary_inv[y, x] > 10:  # sigue moviéndose mientras es negro
        x -= 1

    # 💥 Paso 3: Sigue izquierda hasta que vuelva a blanco
    #while x > 0 and binary_inv[y, x] < 10:  # encontró el final del borde negro
        #x -= 1

    top_left = (x, y)
    print(f"[INFO] Found refined top-left corner at📌: {top_left}")

    # Debug visual (opcional y sexy 😘)
    debug_img = img.copy()
    cv2.circle(debug_img, top_left, 5, (0, 255, 0), -1)
    cv2.imwrite("./debug_top_left_found.png", debug_img)

    return top_left


#testing
'''
if __name__ == "__main__":
    #test_fill = './assets/test/test_fill.png'
    #test_circle = './assets/test/test_circle.png'
    #test_multi = './assets/test/test_multi.png'

    #current_test = test_multi
    
    #current_test = './assets/test/test_snext.png'

    #print("Searching for current element...")
    #elemt_type, question_text = get_element_n_text(current_test)
    #print(f"Element type: {elemt_type}, Question text: {question_text}")

    found, t_f, b_r = search_4_selected_next(current_test)
    if found:
        print(f"Element found at: {t_f} to {b_r}")
        crop_text_square_simple(current_test, t_f, b_r, 60, 400, "q_text_selected_next.png")
    else:
        print("Element not found.")
'''
#if __name__ == "__main__":
    #print("testing ending element detection...XD")
    #found = search_4_sreview('./assets/test/test_srev.png')
    #found = search_4_ssubmit_app('./assets/test/test_ssub.png')
    #print(found)

    #blue_ending_element_detection('./assets/test/test_next.png')


#if __name__ == "__main__":
    #print("testing close_q2_element...")
    #box_top_left = close_q2_element((2333, 297), (2373, 329), './assets/formulary_state.png')
    #print(f"Box top-left corner: {box_top_left}")

    #testing close_q2_element...
    #[INFO] Starting search for top-left corner of Q2 box...
    #[INFO] Found refined top-left corner at: (1685, 294)
    #Box top-left corner: (1685, 294)

    #crop_text_square_2points(
    #"./assets/formulary_state.png", 
    #####(2233, 297),
    #(1685, 294), 
    #(2373, 329))  # this one is the bottom-right corner

    #ans_text = get_answer_from_crop("./assets/formulary_state.png", (1685, 294), (2373, 329))
    #print(f"Extracted answer text🤓: {ans_text}")