import pytesseract
import cv2
import numpy as np
import easyocr

def get_text(cropped_image_path, lang="eng"):
    img = cv2.imread(cropped_image_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar {cropped_image_path}")

    # 1. Escalar la imagen para que Tesseract vea mejor
    scale_factor = 2.0
    img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

    # 2. Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Mejorar contraste y binarizar
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY, 15, 10)

    # 4. Configuración de Tesseract
    config = "--psm 7 -c tessedit_char_whitelist='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ?!*:;.,()'"

    # 5. OCR
    text = pytesseract.image_to_string(gray, lang=lang, config=config)

    # 6. Limpieza
    text = text.strip().replace("\n", " ")
    print(f"[OCR] Extracted text: {text}")

    return text

def get_text_easyocr(image_path, lang='en'):
    # 🧠 Asegurar que lang sea lista válida para EasyOCR
    if isinstance(lang, str):
        lang_list = lang.split('+')
    elif isinstance(lang, list):
        lang_list = lang
    else:
        raise ValueError("Invalid language format. Use string 'en+es' or list ['en', 'es'].")

    # 🈳 EasyOCR no acepta algunos códigos como "eng", acepta "en"
    lang_map = {
        'eng': 'en',
        'spa': 'es'
    }
    lang_list = [lang_map.get(l, l) for l in lang_list]

    reader = easyocr.Reader(lang_list)
    result = reader.readtext(image_path)

    if not result:
        print("[EASY-OCR] No text detected 😢")
        return ""

    # 🎯 Imprimir todos los textos encontrados con confianza
    for (bbox, text, prob) in result:
        print(f"[EASY-OCR] Detected: '{text}' with confidence: {prob:.2f}")

    # 🧵 Concatenar todo el texto detectado
    full_text = ' '.join([text for (_, text, _) in result])
    print(f"[INFO] 📜 Extracted answer text: {full_text}")
    
    return full_text.strip()


