import cv2
import numpy as np
import random
import time
import os
import mouse_control as mouse

def detect_element_and_highlight(screenshot_path, element_path, output_path):
    # Load both images
    screenshot = cv2.imread(screenshot_path)
    element = cv2.imread(element_path)
    
    # Convert both images to grayscale for better matching
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    element_gray = cv2.cvtColor(element, cv2.COLOR_BGR2GRAY)

    # Find the element in the screenshot using template matching
    result = cv2.matchTemplate(screenshot_gray, element_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Get the dimensions of the element
    h, w = element_gray.shape

    # Get the coordinates of the best match
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # Draw a yellow rectangle around the detected element
    cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 255), 3)  # (B, G, R) for yellow

    # Save the result image
    cv2.imwrite(output_path, screenshot)

    # Return the coordinates for further use
    return top_left, bottom_right

def detect_all_elements_and_highlight(   #used to detect multiple elements in a screenshot
    screenshot_path, 
    element_path, 
    output_path, 
    threshold=0.88,  # Adjust for strictness (higher = fewer false positives)
    rectangle_color=(0, 255, 255),  # Yellow
    rectangle_thickness=3
):
    # Load images
    screenshot = cv2.imread(screenshot_path)
    element = cv2.imread(element_path)
    
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    element_gray = cv2.cvtColor(element, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot_gray, element_gray, cv2.TM_CCOEFF_NORMED)
    # Get all locations above threshold
    locations = np.where(result >= threshold)
    h, w = element_gray.shape

    rectangles = []
    for pt in zip(*locations[::-1]):  # Switch columns and rows
        x1, y1 = int(pt[0]), int(pt[1])
        x2, y2 = int(pt[0] + w), int(pt[1] + h)
        top_left = (x1, y1)
        bottom_right = (x2, y2)
        rectangles.append((top_left, bottom_right))
        cv2.rectangle(screenshot, top_left, bottom_right, rectangle_color, rectangle_thickness)
    
    cv2.imwrite(output_path, screenshot)
    print(f"Found {len(rectangles)} matches! Highlighted in {output_path}")
    return rectangles

def get_topmost_rectangle(rectangles):
    """
    Returns the rectangle tuple that is highest on the screen (smallest y1).
    Each rectangle is ((x1, y1), (x2, y2))
    """
    if not rectangles:
        return None
    # Sort by y1 (the top-left y coordinate)
    topmost = min(rectangles, key=lambda rect: rect[0][1])
    return topmost

def middle_rectangle_point(rectangle_coordinates):
    """
    Given rectangle coordinates as ((x1, y1), (x2, y2)),
    returns the middle point as (xm, ym).
    """
    (x1, y1), (x2, y2) = rectangle_coordinates
    xm = (x1 + x2) // 2  # integer division for a clean pixel coordinate
    ym = (y1 + y2) // 2
    return (xm, ym)

def noisy_coords_simetric(coords, gap='gaussian', limit=5):
    """
    Adds a small random noise to (x, y) coords, making actions less predictable.
    - gap: 'gaussian' or 'lognormal'
    - limit: max absolute value of noise (+/-)
    """
    x, y = coords
    
    if gap == 'gaussian':
        dx = int(max(-limit, min(limit, random.gauss(0, 2))))
        dy = int(max(-limit, min(limit, random.gauss(0, 2))))
    elif gap == 'lognormal':
        dx = int(max(-limit, min(limit, random.lognormvariate(0, 1) - 1)))
        dy = int(max(-limit, min(limit, random.lognormvariate(0, 1) - 1)))
    else:
        dx, dy = 0, 0  # No noise if invalid option
    
    # Clamp to desired range
    dx = max(-limit, min(limit, dx))
    dy = max(-limit, min(limit, dy))
    
    new_x = x + dx
    new_y = y + dy
    return (new_x, new_y)

def noisy_coords(coords, gap='gaussian', limit=(5, 2)):
    """
    Adds small random noise to (x, y) coords, making actions less predictable.
    - gap: 'gaussian' or 'lognormal'
    - limit: tuple (limit_x, limit_y), max absolute value of noise for X and Y
    """
    x, y = coords
    limit_x, limit_y = limit  # unpack limits

    if gap == 'gaussian':
        dx = int(max(-limit_x, min(limit_x, random.gauss(0, 2))))
        dy = int(max(-limit_y, min(limit_y, random.gauss(0, 2))))
    elif gap == 'lognormal':
        dx = int(max(-limit_x, min(limit_x, random.lognormvariate(0, 1) - 1)))
        dy = int(max(-limit_y, min(limit_y, random.lognormvariate(0, 1) - 1)))
    else:
        dx, dy = 0, 0  # No noise if invalid option
    
    new_x = x + dx
    new_y = y + dy
    return (new_x, new_y)

def find_and_move_to_element_simple(
    mouse,
    screenshot_path,
    element_path,
    output_path,
    extra_gap=True
):
    coords = detect_element_and_highlight(screenshot_path, element_path, output_path)
    print("Coordinates found (rectangle corners):", coords)

    middle_point = middle_rectangle_point(coords)
    print("Middle point:", middle_point)

    print("Original:", middle_point)
    noisy_coords_gaussian = noisy_coords(middle_point, gap='gaussian')
    print("Noisy (gaussian):", noisy_coords_gaussian)
    noisy_coords_lognormal = noisy_coords(middle_point, gap='lognormal')
    print("Noisy (lognormal):", noisy_coords_lognormal)

    gaussian_x = noisy_coords_gaussian[0]
    gaussian_y = noisy_coords_gaussian[1]

    if extra_gap:
        extra_x = 0
        extra_y = 4          # a extra gap to reach the button better
        final_x = gaussian_x + extra_x
        final_y = gaussian_y + extra_y

    print("Waiting 15 seconds before moving the mouse... 😏")
    time.sleep(15)

    mouse.go_to_position(
        final_x, final_y,
        steps=None,
        tolerance=2,
        time_limit=5,
        smart_pixel=True,
        final_step=True,
        delay_model='gaussian',
        step_count_model='gaussian',
        small_mistake_prob=5,
        noise_timing='gaussian',
        hesitation_prob=5
    )

    x_pos, y_pos = mouse.get_cursor_position()
    print(f"🖱️ Current cursor position: {x_pos}, {y_pos}")

def detect_elements_and_select_upper(view_path, target_element_path, output_path):

    rectangles = detect_all_elements_and_highlight(
        view_path,
        target_element_path,
        output_path,
        threshold=0.88  # Tweak this as needed!
    )
    print("Rectangle coordinates:", rectangles)

    top_rect = get_topmost_rectangle(rectangles)
    print("Topmost rectangle:", top_rect)


    middle_point = middle_rectangle_point(top_rect)
    print("Middle point:", middle_point)

    print("Original:", middle_point)
    noisy_coords_gaussian = noisy_coords(middle_point, gap='gaussian')
    print("Noisy (gaussian):", noisy_coords_gaussian)
    noisy_coords_lognormal = noisy_coords(middle_point, gap='lognormal')
    print("Noisy (lognormal):", noisy_coords_lognormal)

    gaussian_x = noisy_coords_gaussian[0]
    gaussian_y = noisy_coords_gaussian[1]

    print("Waiting 10 seconds before moving the mouse... 😏")
    time.sleep(10)

    mouse.go_to_position(
            gaussian_x, gaussian_y,
            steps=None,
            tolerance=2,
            time_limit=5,
            smart_pixel=True,
            final_step=True,
            delay_model='gaussian',
            step_count_model='gaussian',
            small_mistake_prob=5,
            noise_timing='gaussian',
            hesitation_prob=5
        )

    x_pos, y_pos = mouse.get_cursor_position()
    print(f"🖱️ Current cursor position: {x_pos}, {y_pos}")


# Example usage:
#find_and_move_to_element_simple("main_ss.png", "button_ea.png", "screenshot_result.png", mouse)
#detect_element_and_highlight("3aply.png", "small_ap.png", "screenshot_result_a.png")
'''
rectangles = detect_all_elements_and_highlight(
    "test4.png",
    "small_ap.png",
    "screenshot_multi_result4.png",
    threshold=0.88  # Tweak this as needed!
)
print("Rectangle coordinates:", rectangles)

top_rect = get_topmost_rectangle(rectangles)
print("Topmost rectangle:", top_rect)


middle_point = middle_rectangle_point(top_rect)
print("Middle point:", middle_point)

print("Original:", middle_point)
noisy_coords_gaussian = noisy_coords(middle_point, gap='gaussian')
print("Noisy (gaussian):", noisy_coords_gaussian)
noisy_coords_lognormal = noisy_coords(middle_point, gap='lognormal')
print("Noisy (lognormal):", noisy_coords_lognormal)

gaussian_x = noisy_coords_gaussian[0]
gaussian_y = noisy_coords_gaussian[1]

print("Waiting 10 seconds before moving the mouse... 😏")
time.sleep(10)

mouse.go_to_position(
        gaussian_x, gaussian_y,
        steps=None,
        tolerance=2,
        time_limit=5,
        smart_pixel=True,
        final_step=True,
        delay_model='gaussian',
        step_count_model='gaussian',
        small_mistake_prob=5,
        noise_timing='gaussian',
        hesitation_prob=5
    )

x_pos, y_pos = mouse.get_cursor_position()
print(f"🖱️ Current cursor position: {x_pos}, {y_pos}")



# Example of how to use the function:
screenshot_path = "main_ss.png"
element_path = "button_ea.png"
output_path = "screenshot_result.png"

coords = detect_element_and_highlight(screenshot_path, element_path, output_path)
print("Coordinates found (rectangle corners):", coords)

middle_point = middle_rectangle_point(coords)
print("Middle point:", middle_point)

print("Original:", middle_point)
noisy_coords_gaussian = noisy_coords(middle_point, gap='gaussian')
print("Noisy (gaussian):", noisy_coords_gaussian)
noisy_coords_lognormal = noisy_coords(middle_point, gap='lognormal')
print("Noisy (lognormal):", noisy_coords_lognormal)

gaussian_x = noisy_coords_gaussian[0]
gaussian_y = noisy_coords_gaussian[1]

time.sleep(15)  # Wait for 15 seconds before moving the mouse

mouse.go_to_position(
    gaussian_x, gaussian_y,
    steps=None,            # Let it choose with gaussian by default
    tolerance=2,
    time_limit=5,
    smart_pixel=True,
    final_step=True,
    delay_model='gaussian',
    step_count_model='gaussian',  # 'lognormal' if you want more variance
    small_mistake_prob=5,         # 5% chance to "miss" like a human
    noise_timing='gaussian',
    hesitation_prob=5  )           # 5% chance to "pause and think" 
    
x_pos, y_pos = mouse.get_cursor_position()
print(f"🖱️ Current cursor position: {x_pos}, {y_pos}")

'''