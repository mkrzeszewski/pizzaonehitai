from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
from datetime import datetime
random.seed(datetime.now().timestamp())

# Constants
num_fields = 21  # Number of sectors
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

# Function to draw the wheel
def draw_wheel(angle_offset=0, pointer_angle=0, previous_color=None, debug=""):
    # Create a blank transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 400, 400], fill=(0, 0, 0))
    draw.rectangle([0, 0, 400, 400], fill=(0, 0, 0, 0))
    
    top_color = white
    try:
        font = ImageFont.truetype("arial.ttf", 20)  # Customize your font path and size
    except IOError:
        font = ImageFont.load_default()
    draw.text((0,0), debug, font=font, fill="white")
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

        #check if it goes through 0 angle
        if (angle_start < angle_end and angle_start <= 0 < angle_end) or (angle_start > angle_end and (angle_start <= 0 or angle_end > 0)):
            top_color = color

        draw.polygon(points, fill=color)

    pointer_jump = 0

    # Define the points of the downward triangle pointer (inverted horizontally)
    pointer_points = [ ((width/2),(height/2) - radius + 10 + pointer_jump), 
                      ((width/2) + 10, (height/2) - radius - 10), 
                      ((width/2) - 10, (height/2) - radius - 10) ]

    # Draw the pointer triangle (white)
    draw.polygon(pointer_points, fill=white)

    pointer_position = (pointer_angle + angle_offset) % 360
    return img, top_color  # Return the color of the current field

# Function to generate the GIF
def generate_spinning_wheel_with_pointer(filename="assets/gif/ruleta.gif"):
    images = []
    previous_color = None  # Track the previous color for pointer jump
    initial_rotation = random.randint(1,360)
    angle_offset = (360) + initial_rotation
    pointer_angle = (360)  # Pointer moves along with the wheel
    color = white
    for i in range(startFrames):
        dynamicOffset = int(frames - i*2)
        angle_offset = (360 * i) / dynamicOffset + initial_rotation
        frame, previous_color = draw_wheel(angle_offset, pointer_angle, previous_color)
        images.append(frame)

    for i in range(frames):
        dynamicOffset = int(frames - (startFrames*2))
        angle_offset = (360 * i) / dynamicOffset + initial_rotation
        frame, previous_color = draw_wheel(angle_offset, pointer_angle, previous_color)
        images.append(frame)

    for i in range (endFrames):
        dynamicOffset = int(frames - (startFrames*2) + i*4)
        angle_offset = (360 * i) / dynamicOffset + initial_rotation
        frame, color = draw_wheel(angle_offset, pointer_angle, previous_color)
        images.append(frame)

    for i in range(80):
        frame, previous_color = draw_wheel(angle_offset, pointer_angle, previous_color)
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
    

