import button_searcher as but
import cv2
import time
import os


def search_4_current_element(view):
    results = []

    for idx, (name, asset) in enumerate([
        ("key_fill", "./assets/key_fill.png"),
        ("multi_select", "./assets/multi-select.png"),
        ("select_circle", "./assets/circle-select.png")
    ], start=1):
        found, _, _, score = detect_element_and_highlight(
            screenshot_path=view,
            element_path=asset,
            output_path=f'./assets/debug_{name}.png',
            threshold=0.8,
            debug=True
        )
        results.append((name, idx, score, found))

    # Elegir el que tenga el score más alto y que esté encontrado
    results = [r for r in results if r[3]]  # solo encontrados
    if not results:
        print("No element detected")
        return 0

    best = max(results, key=lambda x: x[2])  # por score
    print(f"Best match: {best[0]} with score {best[2]:.4f}")

    return best[1]  # retorna el número (1, 2 o 3)


def search_4_key_fill(view):
    found, _, _, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/key_fill.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8
    )
    return found

def search_4_multi_select(view):
    found, _, _, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/multi-select.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8
    )
    return found

def search_4_select_circle(view):
    found, _, _, score = detect_element_and_highlight(
        screenshot_path=view,
        element_path='./assets/circle-select.png',
        output_path='./assets/formulary_state.png',
        threshold=0.8
    )
    return found


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


#testing

if __name__ == "__main__":
    test_fill = './assets/test/test_fill.png'
    test_circle = './assets/test/test_circle.png'
    test_multi = './assets/test/test_multi.png'


    print("Searching for current element...")
    result = search_4_current_element(test_circle)
    print(f"Result: {result}") 



