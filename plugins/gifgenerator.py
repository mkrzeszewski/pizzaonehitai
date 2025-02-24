from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
from datetime import datetime
random.seed(datetime.now().timestamp())
import math

# Constants
num_fields = 19  # Number of sectors
width, height = 400, 400  # Image size
radius = 150  # Radius of the wheel
pointer_base_offset = 20  # Distance of pointer base above the wheel
frames = 120  # Number of frames for smooth animation
startFrames = 40
endFrames = 120
center = (width // 2, height // 2)  # Center of the wheel

# Colors
blue = (1, 66, 99)
red = (151, 42, 39)
white = (255, 255, 255)
yellow = (255, 190, 20)
green = (0, 99, 0)
step = 0
# Function to draw the wheel
def draw_wheel(angle_offset=0, previous_color=None, debug=""):
    # Create a blank transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 400, 400], fill=(0, 0, 0))
    
    top_color = white
    try:
        font = ImageFont.truetype("arial.ttf", 20)  # Customize your font path and size
    except IOError:
        font = ImageFont.load_default()
    draw.text((0,0), debug, font=font, fill="white")
    
    
    # Calculate the angle of the "top" position of the wheel based on the offset
    top_angle = (angle_offset + 90) % 360  # Pointer is usually at the top, i.e., 90 degrees from 0
    point_x, point_y = 200, 150
    dx = point_x - center[0]
    dy = point_y - center[1]
    point_angle = math.degrees(math.atan2(dy, dx))  # Convert radians to degrees
    point_angle = (point_angle + 360) % 360  # Normalize angle to [0, 360)
    top_color = white
    # Draw the alternating sectors (black and red)
    for i in range(num_fields):
        # Calculate the angle for the triangle (sector of the wheel)
        angle_start = (i * 360 / num_fields + angle_offset) % 360
        angle_end = ((i + 1) * 360 / num_fields + angle_offset) % 360

        # Create the points for the triangle (sector)
        points = [
            center,  # The center of the wheel
            (center[0] + radius * np.cos(np.radians(angle_start)),
             center[1] + radius * np.sin(np.radians(angle_start))),
            (center[0] + radius * np.cos(np.radians(angle_end)),
             center[1] + radius * np.sin(np.radians(angle_end)))
        ]
        # Determine the color (alternating black and red)
        color = blue if i % 2 == 0 else red
        if i in [0]:
            color = green
        # Check if the point_angle is within this sector's range
        if angle_start < angle_end:
            if angle_start <= point_angle < angle_end:
                top_color = color  # Mark this sector with yellow
        else:  # The sector wraps around 0 degrees
            if angle_start <= point_angle or point_angle < angle_end:
                top_color = color  # Mark this sector with yellow

        draw.polygon(points, fill=color)

    pointer_jump = 0
    global step
    if previous_color != top_color:
        step = 0
    pointer_jump = step
    if step < 10:
        step += 1
    # Define the points of the downward triangle pointer (inverted horizontally)
    pointer_points = [((width/2),(height/2) - radius + 20 + pointer_jump), 
                      ((width/2) + 10, (height/2) - radius - 10), 
                      ((width/2) - 10, (height/2) - radius - 10)]
    
    # Draw the pointer triangle (white)
    draw.polygon(pointer_points, fill=white)

    return img, top_color  # Return the color of the current field


# Function to generate the GIF

def getStringFromColor(color):
    return ""
    if(color == white):
        return "White"
    else:
        if color == blue:
            return "Blue"
        elif color == green:
            return "Green"
        elif color == red:
            return "Red"
        
def generate_spinning_wheel_with_pointer(filename="assets/gif/ruleta.gif"):
    images = []
    debug = []

    previous_color = None  # Track the previous color for pointer jump
    #initial_rotation = random.randint(1,360)
    initial_rotation = 0
    angle_offset = (360) + initial_rotation
    color = white

    frame, color = draw_wheel(angle_offset, previous_color, getStringFromColor(color))

    debug.append(frame)
    debug.append(frame)
    debug.append(frame)
    debug[0].save("debug.gif", save_all=True, append_images=debug[1:], duration=40, loop=1)
    for i in range(startFrames):
        dynamicOffset = int(frames - i*2)
        angle_offset = (360 * i) / dynamicOffset + initial_rotation
        frame, color = draw_wheel(angle_offset, color, getStringFromColor(color))
        images.append(frame)

    for i in range(frames):
        dynamicOffset = int(frames - (startFrames*2))
        angle_offset = (360 * i) / dynamicOffset + initial_rotation
        frame, color = draw_wheel(angle_offset, color, getStringFromColor(color))
        images.append(frame)

    for i in range (endFrames):
        dynamicOffset = int(frames - (startFrames*2) + (i * 3))
        angle_offset = (360 * i) / dynamicOffset + initial_rotation
        frame, color = draw_wheel(angle_offset, color, getStringFromColor(color))
        images.append(frame)

    for i in range(80):
        frame, color = draw_wheel(angle_offset,  color, getStringFromColor(color))
        images.append(frame)
        
    images[0].save(filename, save_all=True, append_images=images[1:], duration=40, loop=1)
    if(color == white):
        return None
    else:
        if color == blue:
            return "Blue"
        elif color == green:
            return "Green"
        elif color == red:
            return "Red"