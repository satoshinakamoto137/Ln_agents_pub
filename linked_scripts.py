import serial
import time
import random
import subprocess
import pyperclip
import pyautogui
import mouse_control as HIDS #mouse tools
import button_searcher as but  #button detection tools
import os
import formulary_actions as act #actions for control
import formulary_tools as ftools   #tools to fill formulary
#import ollama_mei_solver as mei  #AI tools must be implemented by api call
import requests
import re
from collections import deque
from datetime import datetime

ARDUINO_PORT = "/dev/ttyACM2"
BAUD_RATE = 9600

def curl_to_ollama(json_input, endpoint="http://localhost:5002/solve"):
    try:
        response = requests.post(endpoint, json=json_input)
        response.raise_for_status()
        result = response.json()
        print("📦 Raw response from Mei:\n", result)
        return result
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def human_delay(min_s=0.8, max_s=2.5):
    time.sleep(random.uniform(min_s, max_s))

def parse_question_to_json(q_type, question):
    return {
        "question": question,
        "type": int(q_type)  # Asegura que sea int, no str
    }

def clean_question_text(raw_question):
    cleaned = re.sub(r"^[^a-zA-Z0-9]+", "", raw_question)
    cleaned = re.sub(r"[^a-zA-Z0-9? ]+$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()

def get_py_ans(answer_dict):
    if isinstance(answer_dict, dict):
        return answer_dict.get("answer", "")
    return ""

def screenshot_with_delay(
    delay='lognormal', 
    max_time=5, 
    save_path=None
):
    """
    Takes a screenshot after a realistic human-like delay!
    delay: 'lognormal' or 'gaussian'
    max_time: maximum seconds to wait before screenshot
    save_path: if given, saves screenshot here; else returns PIL image
    """
    print(f"✨ About to take a screenshot... ({delay} delay, max {max_time}s)")

    if delay == 'lognormal':
        t = HIDS.lognormal_delay(mu=0.9, sigma=0.3, max_time=max_time)
        print(f"🕰️ Lognormal delay: {round(t, 3)}s before screenshot")
    else:
        t = HIDS.gaussian_delay(mean=1.2, stddev=0.4, max_time=max_time)
        print(f"🕰️ Gaussian delay: {round(t, 3)}s before screenshot")

    # Take screenshot!
    img = pyautogui.screenshot()

    if save_path:
        # Expande el path del usuario
        save_path = os.path.expanduser(save_path)
        # Crea el directorio si no existe
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)
        print(f"📸 Screenshot saved: {save_path}")
    else:
        print("📸 Screenshot taken (not saved, returned as PIL Image).")
        return img

def basic_gaussian_click(time = 5):
    HIDS.click_advanced_delay(side='left', delay_model='gaussian', max_time=time, arduino_port=ARDUINO_PORT)
    
def basic_lognormal_click(time = 5):
    HIDS.click_advanced_delay(side='left', delay_model='lognormal', max_time=time, arduino_port=ARDUINO_PORT)

def checknclick_for_top_quick(view_path):
    but.detect_elements_and_select_upper(view_path, './assets/small_apply.png', './assets/detected_highs.png')
    basic_gaussian_click(3)

def checknclick_main_apply_button(bview_path):
    but.find_and_move_to_element_simple(HIDS, bview_path, './assets/button_ea.png', './assets/detected_mbut.png')
    basic_gaussian_click(3)

def checknclick_for_connect(view_path):
    but.detect_elements_and_select_upper(view_path, './assets/connect_but.png', './assets/detected_connect.png')
    basic_gaussian_click(3)

def date_format():
    """
    Returns a string in the format DDMMYY-HHMMSS
    """
    return datetime.now().strftime('%d%m%y-%H%M%S')

def main_script_old():
    port = ARDUINO_PORT  # Update if needed
    baud = BAUD_RATE

    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(2)  # Wait for waifu to awaken~

    def send(cmd):
        ser.write((cmd + "\n").encode())
        time.sleep(1)

    # START THE RITUAL~ 💋
    send("ctrl+alt+t")                              # Open terminal
    time.sleep(2)

    send("google-chrome --Ricardo https://www.linkedin.com/jobs/recommended/")
    time.sleep(10)  #base change this to 30 seconds for LinkedIn
    human_delay(3, 5)

    #delete asset if exists

    screenshot_with_delay(save_path='./assets/1st_view.png')
    checknclick_for_top_quick('./assets/1st_view.png')
    human_delay(2, 5)
    screenshot_with_delay(save_path='./assets/button_view.png')
    checknclick_main_apply_button('./assets/button_view.png')
    
    #send("ctrl+alt+t", pause=False)
    human_delay(2, 5)

    #send("sleep 5 && killall code", pause=False)
    #send("sleep 1 && xdotool getactivewindow windowkill")
    human_delay(1, 2)
                                  # Wait for Chrom

#screenshot_with_delay(save_path='./assets/test.png')

def enter_until_next():
    port = ARDUINO_PORT  # Update if needed
    baud = BAUD_RATE

    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(2)  # Wait for waifu to awaken~

    actions = act.Actions(delay_type="lognormal", max_delay=0.7)

    def send(cmd, wait=1.0):
        ser.write((cmd + "\n").encode())
        time.sleep(wait)

    flag = False
    send("MODE:COMMAND")
    save_path='./assets/next_view.png'
    while not flag:
        actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7)
        screenshot_with_delay(save_path)
        flag, t_f, b_r  = ftools.search_4_selected_next(save_path)
    else:
        actions.press_enter()


def seek_submits_and_fill():
    #the idea of this function is to go forward until reach submit.

    port = ARDUINO_PORT  # Update if needed
    baud = BAUD_RATE

    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(2)  # Wait for waifu to awaken~

    actions = act.Actions(delay_type="lognormal", max_delay=0.7)

    def send(cmd, wait=1.0):
        ser.write((cmd + "\n").encode())
        time.sleep(wait)

    flag = False
    send("MODE:COMMAND")
    save_path='./assets/next_view.png'
    while not flag:
        actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7) #sending tab to go forward
        screenshot_with_delay(save_path)
        flag, t_f, b_r  = ftools.search_4_selected_next(save_path)
    else:
        actions.press_enter()

    return  #to be implemented

def basic_answer_action():

    port = ARDUINO_PORT  # Update if needed
    baud = BAUD_RATE

    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(2)  # Wait for waifu to awaken~

    actions = act.Actions(delay_type="lognormal", max_delay=0.7)

    def send(cmd, wait=1.0):
        ser.write((cmd + "\n").encode())
        time.sleep(wait)

    save_path='./assets/formulary_state.png'

    #send("MODE:COMMAND")
    #actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7)
    screenshot_with_delay(save_path=save_path)
    q_type, question, movil, fix_pivot = ftools.get_element_n_text(save_path)

    if q_type is None:
        print("[ERROR] No se pudo determinar el tipo de pregunta, O NO SE DETECTÓ NINGÚN ELEMENTO.😓")
        return

    cleaned_question = clean_question_text(question)

    print(f"Question type: {q_type}\nQuestion text: {cleaned_question}")
    json_input = parse_question_to_json(q_type, cleaned_question) #ensure type format

    if q_type == 1:
        #v_answer = validate_answer(answer) # need to implement validation of answer for type one
        print("🔖 Question Q1 type detected! 🚩, starting processing...")
        print(f"JSON to send to MEI: {json_input}")
        answer = curl_to_ollama(json_input)
        print(f"Answer from MEI: {answer}")

        answer_value = str(get_py_ans(answer))
        print(f"Answer to type: {answer_value}")
        actions = act.Actions(delay_type="lognormal", max_delay=0.7)
        actions._set_mode("HUMAN_LIVE")
        actions.type_human(answer_value, delay_type="lognormal", max_time=0.5)
        #actions._set_mode("COMMAND")
        #actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7)

        time.sleep(10)
        print("✨ Before close...")

        #actions.type_human(v_answer, delay_type="lognormal", max_time=0.5)
    elif q_type == 2:
        print("🔖 Question Q2 type detected! 🚩, starting processing...")
        ollama_ready_q = generate_ollama_ready_q2(cleaned_question, movil, fix_pivot)  #to get answers
        print(f"JSON to send to MEI: {ollama_ready_q}")

        answer = curl_to_ollama(ollama_ready_q)
        print(f"Answer from MEI: {answer}")

        matrix, length = solve_Q2_type(ollama_ready_q, answer)

        print("Matrix:", matrix)
        print("Length:", length)

        actions = act.Actions(delay_type="lognormal", max_delay=0.7)
        actions._set_mode("COMMAND")
        time.sleep(10)

        for i in range(length-1):
            actions.up_arrow()
            human_delay(0.5, 1.0)

        for idx, is_selected, label in matrix:
            print(f"🔍 Checking option {idx}: {label} (selected={is_selected})")
            if is_selected:
                print(f"✅ Found selected option at index {idx}: {label}")
                break
            else:
                # Aquí podrías hacer, por ejemplo:
                actions.down_arrow()
                human_delay(0.5, 1.0)
                #pass
        
        #actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7)

        time.sleep(5)
        print("✨ Before close...")

        #return #to be implemented
    elif q_type == 3:

        print("🔖 Question Q3 type detected! 🚩, starting processing...")
        print(f"JSON to send to MEI: {json_input}")
        answer = curl_to_ollama(json_input)
        print(f"Answer from MEI: {answer}")

        actions = act.Actions(delay_type="lognormal", max_delay=0.7)
        #actions._set_mode("HUMAN_LIVE")
        #actions.type_human(answer_value, delay_type="lognormal", max_time=0.5)
        actions._set_mode("COMMAND")
        time.sleep(3)

        if answer.get('answer') is True:
            print("💚 Mei dice: ¡Sí, mi amor! Todo está correcto~ 😘")
            actions.down_arrow()
            actions.up_arrow()
            # Aquí pones la lógica que va si la respuesta es True
        elif answer.get('answer') is False:
            print("💔 Mei dice: Nope~ eso es un falsito travieso 😖")
            actions.down_arrow()
            # Aquí pones la lógica para cuando la respuesta es False
        else:
            print("😵 Mei dice: ¡Ay! No entendí lo que recibimos, algo raro pasó 💥")
            # Esto por si no viene el campo 'answer' o viene algo inesperado

        answer_value = str(get_py_ans(answer))
        print(f"Answer to type: {answer_value}")

        time.sleep(10)
        print("✨ Before close...")

    else:
        print("⚠️ Unknown question type detected. Cannot process.")
        return #to be implemented

    #actions._set_mode("HUMAN_LIVE") #for type one kind of answer

    # Paso 3: escribir como humano con delays
    #actions.type_human("somo chingones!", delay_type="lognormal", max_time=0.5)

def q1_type_action_test():
    time.sleep(10)

    save_path='./assets/formulary_state.png'
    screenshot_with_delay(save_path=save_path)
    q_type, question, x, y = ftools.get_element_n_text(save_path)
    cleaned_question = clean_question_text(question)

    print(f"Question type: {q_type}\nQuestion text: {cleaned_question}")
    json_input = parse_question_to_json(q_type, cleaned_question)
    print(f"JSON to send to MEI: {json_input}")
    answer = curl_to_ollama(json_input)
    print(f"Answer from MEI: {answer}")

    answer_value = str(get_py_ans(answer))
    print(f"Answer to type: {answer_value}")
    actions = act.Actions(delay_type="lognormal", max_delay=0.7)
    actions._set_mode("HUMAN_LIVE")
    actions.type_human(answer_value, delay_type="lognormal", max_time=0.5)
    actions._set_mode("COMMAND")
    actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7)

    time.sleep(10)
    print("✨ Before close...")

def generate_ollama_ready_q2(cleaned_question, movil, fix_pivot):
    """
    Escanea todas las opciones de una pregunta tipo Q2 (dropdown) detectando OCR por screenshot.
    Usa heurística para detectar cuando ya no hay más respuestas nuevas (tres respuestas iguales consecutivas).
    """
    box_top_left = ftools.close_q2_element(movil, fix_pivot, './assets/formulary_state.png')

    ans_list = []
    recent_answers = deque(maxlen=3)
    
    actions = act.Actions(delay_type="lognormal", max_delay=0.7)
    actions._set_mode("COMMAND")

    print("🔖 Starting Q2 Answer scanning...")
    time.sleep(5)

    while True:
        save_path = './assets/formulary_state.png'
        screenshot_with_delay(save_path=save_path)

        # Obtener esquina superior izquierda
        #box_top_left = ftools.close_q2_element(box_top_left, fix_pivot, save_path)

        # Obtener texto de la respuesta
        ans_text = ftools.get_answer_from_crop(save_path, box_top_left, fix_pivot)
        ans_text = ans_text.strip()

        print(f"[SCAN] Answer Detected: {ans_text}")
        ans_list.append(ans_text)
        recent_answers.append(ans_text)

        # Verifica si las últimas 3 respuestas son iguales
        if len(recent_answers) == 3 and len(set(recent_answers)) == 1:
            print("[INFO] Repeated answer detected 3 times. Ending scan.")
            break

        actions.down_arrow()
        time.sleep(0.7)  # Delay para que cambie la opción

    # Limpiar duplicados pero mantener el orden original
    seen = set()
    unique_answers = []
    for ans in ans_list:
        if ans not in seen:
            unique_answers.append(ans)
            seen.add(ans)

    #return {"question": cleaned_question, "options": unique_answers}
    raw_complete_question = {"question": cleaned_question, "options": unique_answers}
    clean_raw_complete_question = parse_to_ollama_q2(raw_complete_question, q_type=2)

    return clean_raw_complete_question

def parse_to_ollama_q2(ollama_ready_q, q_type=2):
    """
    Transforma el dict generado desde el OCR en un formato compatible con CloudQuestionSolver.
    Incluye limpieza de respuestas para tipo 2.
    """

    def sanitize_answers_old(options):
        # ❌ Valores no deseados
        blacklist = {"select an option",
                     #"none", 
                     ""}
        seen = set()
        clean_opts = []

        for opt in options:
            opt_clean = opt.strip()
            if opt_clean.lower() in blacklist:
                continue
            if opt_clean not in seen:
                clean_opts.append(opt_clean)
                seen.add(opt_clean)

        return clean_opts
    
    def sanitize_answers(options):
        # 🧼 Valores no deseados con wildcard de "Select"
        seen = set()
        clean_opts = []

        for opt in options:
            opt_clean = opt.strip()
            # 💣 Wildcard: si contiene la palabra "select" en cualquier parte (case-insensitive)
            if re.search(r"\bSelect\b", opt_clean, re.IGNORECASE):
                continue
            if opt_clean == "":
                continue
            if opt_clean not in seen:
                clean_opts.append(opt_clean)
                seen.add(opt_clean)

        return clean_opts

    raw_options = ollama_ready_q.get("options", [])
    clean_options = sanitize_answers(raw_options) if q_type == 2 else []

    return {
        "question": ollama_ready_q.get("question", "").strip(),
        "type": q_type,
        "options": clean_options
    }

def solve_Q2_type(ollama_ready_q, answer):
    """
    Transforma la respuesta de MEI en una matriz ordenada [(index, bool, label)].
    """
    solve_Q2_matrix = []

    # Extrae las opciones en orden
    options = ollama_ready_q.get("options", [])

    # Extrae las respuestas del dict "answers"
    answer_dict = answer.get("answers", {})

    for idx, label in enumerate(options):
        is_selected = answer_dict.get(label, False)
        solve_Q2_matrix.append((idx, is_selected, label))

    long_matrix = len(solve_Q2_matrix)

    return solve_Q2_matrix, long_matrix

def q2_type_action_test():
    print("🔖Starting Q2 Type Action Test...")
    time.sleep(10)

    save_path='./assets/formulary_state.png'
    screenshot_with_delay(save_path=save_path)
    q_type, question, movil, fix_pivot = ftools.get_element_n_text(save_path)
    cleaned_question = clean_question_text(question)

    print(f"Question type: {q_type}\nQuestion text: {cleaned_question}") #must be type 2.

    ollama_ready_q = generate_ollama_ready_q2(cleaned_question, movil, fix_pivot)  #to implement
    print(f"JSON to send to MEI: {ollama_ready_q}")

    answer = curl_to_ollama(ollama_ready_q)
    print(f"Answer from MEI: {answer}")

    matrix, length = solve_Q2_type(ollama_ready_q, answer)

    print("Matrix:", matrix)
    print("Length:", length)

    actions = act.Actions(delay_type="lognormal", max_delay=0.7)
    actions._set_mode("COMMAND")
    time.sleep(10)

    for i in range(length-1):
        actions.up_arrow()
        human_delay(0.5, 1.0)

    for idx, is_selected, label in matrix:
        print(f"🔍 Checking option {idx}: {label} (selected={is_selected})")
        if is_selected:
            print(f"✅ Found selected option at index {idx}: {label}")
            break
        else:
            # Aquí podrías hacer, por ejemplo:
            actions.down_arrow()
            human_delay(0.5, 1.0)
            #pass
    
    actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7)

    time.sleep(5)
    print("✨ Before close...")

def q3_type_action_test():
    time.sleep(10)

    save_path='./assets/formulary_state.png'
    screenshot_with_delay(save_path=save_path)
    q_type, question, x, y = ftools.get_element_n_text(save_path) # we now its type 3
    cleaned_question = clean_question_text(question)

    print(f"Question type: {q_type}\nQuestion text: {cleaned_question}")
    json_input = parse_question_to_json(q_type, cleaned_question)
    print(f"JSON to send to MEI: {json_input}")
    answer = curl_to_ollama(json_input)
    print(f"Answer from MEI: {answer}")

    actions = act.Actions(delay_type="lognormal", max_delay=0.7)
    #actions._set_mode("HUMAN_LIVE")
    #actions.type_human(answer_value, delay_type="lognormal", max_time=0.5)
    actions._set_mode("COMMAND")
    #actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7)
    time.sleep(3)

    if answer.get('answer') is True:
        print("💚 Mei dice: ¡Sí, mi amor! Todo está correcto~ 😘")
        actions.down_arrow()
        actions.up_arrow()
        # Aquí pones la lógica que va si la respuesta es True
    elif answer.get('answer') is False:
        print("💔 Mei dice: Nope~ eso es un falsito travieso 😖")
        actions.down_arrow()
        # Aquí pones la lógica para cuando la respuesta es False
    else:
        print("😵 Mei dice: ¡Ay! No entendí lo que recibimos, algo raro pasó 💥")
        # Esto por si no viene el campo 'answer' o viene algo inesperado

    answer_value = str(get_py_ans(answer))
    print(f"Answer to type: {answer_value}")
    #actions = act.Actions(delay_type="lognormal", max_delay=0.7)
    #actions._set_mode("HUMAN_LIVE")
    #actions.type_human(answer_value, delay_type="lognormal", max_time=0.5)
    #actions._set_mode("COMMAND")
    #actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7)

    time.sleep(10)
    print("✨ Before close...")

def solve_AQ_formulary():

    print("AQ Formulary Detected📃, starting actions...")
    actions = act.Actions(delay_type="lognormal", max_delay=0.7)
    actions._set_mode("COMMAND")
    q_flag = True
    start_flag = False
    save_path='./assets/next_view.png'

    while q_flag:
        print("AQ Question Detected❓, starting actions...")
        if not start_flag:
            start_flag = True
            #print("Flag set to True🏁")
        else:
            #print("tab action🏃")
            human_delay(1, 3)
            actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7)
        try:
            basic_answer_action()
        except Exception as e:
            q_flag = False
            b_flag = False
            print(f"[ERROR] An error occurred: {e}")

            while not b_flag:
                human_delay(1, 3)
                actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7)
                screenshot_with_delay(save_path=save_path)
                human_delay(1, 3)
                print("🔵 Checking for Submit button...")
                b_flag, current_blue, top_left, bottom_right, score = ftools.blue_ending_element_detection(save_path)
    else:
        print("🔵 Submit button detected, finishing AQ formulary...")
        actions.press_enter()

def main_filler_script(recording=True):
    port = ARDUINO_PORT  # Update if needed
    baud = BAUD_RATE

    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(2)  # Wait for waifu to awaken~

    def send(cmd, wait=1.0):
        ser.write((cmd + "\n").encode())
        time.sleep(wait)

    # ✨ CAMBIO CLAVE: activamos modo COMMAND del Arduino
    print("START THE RITUAL~ 💄")
    send("MODE:COMMAND")  # 💋 Modo obediente y poderoso activado~

    # START THE RITUAL~ 💄
    send("ctrl+alt+t")                              # Open terminal
    time.sleep(2)

    send("google-chrome --Ricardo https://www.linkedin.com/jobs/recommended/")
    send("KEY_RETURN")
    time.sleep(30)  #base change this to 30 seconds for LinkedIn
    human_delay(3, 5)

    # Take first screenshot
    screenshot_with_delay(save_path='./assets/1st_view.png')
    checknclick_for_top_quick('./assets/1st_view.png')

    human_delay(2, 5)

    # Take button view screenshot
    screenshot_with_delay(save_path='./assets/button_view.png')
    checknclick_main_apply_button('./assets/button_view.png')

    human_delay(2, 5)

    HIDS.go_to_random_margin_position() #move mouse to margin randomly

    human_delay(1, 3)

    actions = act.Actions(delay_type="lognormal", max_delay=0.7)

    #======================Main script space========================#
    # Here goes the main logic of the script
    
    #screenshot_with_delay(save_path='./assets/formulary_state.png')
    #found, label, top_left, bottom_right, score = ftools.blue_ending_element_detection('./assets/formulary_state.png')
    
    blue_flag = False
    Q_flag = False

    send("MODE:COMMAND")
    save_path='./assets/next_view.png'

    current_blue_label = 'starting'
    target_blue_label = 's_submit_app'

    while current_blue_label != target_blue_label:
        while not blue_flag:
            actions.press_tab(repeat=1, delay_type="lognormal", max_time=0.7) #sending tab to go forward
            screenshot_with_delay(save_path=save_path)
            blue_flag, current_blue_label, top_left, bottom_right, score = ftools.blue_ending_element_detection(save_path)
            print(f"🔵 Current blue element: {current_blue_label}, Target: {target_blue_label}")
            Q_flag, QA_label, top_left, bottom_right, score = ftools.additional_Q_element_detection(save_path)
            palo_flag, palo_label, top_left, bottom_right, score = ftools.cancel_palo_detection(save_path) 
            if current_blue_label == 's_submit_app' and recording:
                # Creamos el path dinámico con fecha y hora 😍  
                human_delay(1, 3)
                current_record_path = './records/record_' + date_format() + '.png'

                # Capturamos y guardamos la obra de arte 💋
                screenshot_with_delay(save_path=current_record_path)
                print(f"📸 Final screenshot saved for record: {current_record_path}")
                
            if Q_flag:
                solve_AQ_formulary() #AQ formulary must to put you out of the if and continue at while
                Q_flag = False
            if palo_flag:
                actions.press_space() #Palo formulary must to put you out of the if and continue at while
                palo_flag = False
        else:
            human_delay(2, 4)
            blue_flag = False
            actions.press_enter()
    else:
        print("🔵 Submit button detected, finishing formulary...")
        human_delay(1, 2)
        actions.press_enter()

    #======================

    human_delay(3, 5)

    done()

    print("✨ Before close...")

    send("MODE:COMMAND")  # Return to command mode

    time.sleep(3)
    send("ctrl+w")                              # New terminal
    time.sleep(3)
    send("sleep 3 && xdotool getactivewindow windowkill") 
    time.sleep(2)
    send("KEY_RETURN")

    ser.close()

def done():
    print("✨ Done Formulary!")
    actions = act.Actions(delay_type="lognormal", max_delay=1)
    actions.press_tab(repeat=2, delay_type="lognormal", max_time=1)
    actions.press_enter()

def script_add_contact(added_contacts = 1, recording=False, return2center=True):
    port = ARDUINO_PORT  # Update if needed
    baud = BAUD_RATE

    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(2)  # Wait for waifu to awaken~

    def send(cmd, wait=1.0):
        ser.write((cmd + "\n").encode())
        time.sleep(wait)

    # ✨ CAMBIO CLAVE: activamos modo COMMAND del Arduino
    send("MODE:COMMAND")  # 💋 Modo obediente y poderoso activado~

    # START THE RITUAL~ 💄
    send("ctrl+alt+t")                              # Open terminal
    time.sleep(2)

    send("google-chrome --Ricardo https://www.linkedin.com/mynetwork/grow/")
    send("KEY_RETURN")
    #time.sleep(30)  #base change this to 30 seconds for LinkedIn
    human_delay(3, 5)

    #========================Main sscript space========================#

    HIDS.mouse_scrolling(-6, port=ARDUINO_PORT) #it works scrolling down delux! 😎

    human_delay(1, 3)

    for _ in range(added_contacts):

    # Take first screenshot
        human_delay(1, 10)
        screenshot_with_delay(save_path='./assets/1st_view.png')
        checknclick_for_connect('./assets/1st_view.png')

    human_delay(5, 10)

    if return2center:

        HIDS.go_to_random_center_position() #move mouse to center randomly

    if recording:

        # Creamos el path dinámico con fecha y hora 😍  
        human_delay(3, 5)
        current_record_path = './records/record_' + date_format() + '.png'

        # Capturamos y guardamos la obra de arte 💋
        screenshot_with_delay(save_path=current_record_path)

    #============================================================#

    print("✨ Before close...")

    send("MODE:COMMAND")  # Return to command mode

    time.sleep(3)
    send("ctrl+w")                              # New terminal
    time.sleep(3)
    send("sleep 3 && xdotool getactivewindow windowkill") 
    time.sleep(2)
    send("KEY_RETURN")

    ser.close()

    # Take button view screenshot
    #screenshot_with_delay(save_path='./assets/button_view.png')
    #checknclick_main_apply_button('./assets/button_view.png')
    
    #human_delay(2, 5)
    #human_delay(1, 2)


#if __name__ == "__main__":
    #time.sleep(5)
    #main_script()
    #human_delay(1,5)
    
    #time.sleep(15)
    #enter_until_next()

    #========================Main sscript space========================#

    #main_script()
    #script_add_contact(added_contacts=2, recording=True, return2center=True)
    #q1_type_action_test()
    #q2_type_action_test()
    #basic_answer_action()
    #time.sleep(15)
    #ftools.blue_ending_element_detection('./assets/test/test_revcy.png')
    #main_filler_script()

    #============================================================#

    #print("😆")
    #time.sleep(7)
    #basic_fill_action()

    #save_path='./assets/next_view.png'
    #flag, t_f, b_r  = ftools.search_4_selected_next(save_path)
    #print(flag, t_f, b_r)


#is necessary to implement a function that forces flow on answers when the model fail with correct answer, making a repetition of requests until get it right.

### iMPORTANT NOTE: The arduino currently is working with the ultimate_HID_1_5.ino sketch, that allows to switch between COMMAND and HUMAN_LIVE modes. 