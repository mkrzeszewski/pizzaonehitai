from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
from datetime import datetime
import math

SLOT_IMAGES = ["assets/img/pizza.png", "assets/img/skull.png", "assets/img/image1.png", "assets/img/image2.png", "assets/img/image3.png", "assets/img/image4.png", "assets/img/image5.png"]

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
    random.seed(datetime.now().timestamp())
    images = []
    debug = []

    previous_color = None  # Track the previous color for pointer jump
    initial_rotation = random.randint(1,360)
    #initial_rotation = 0
    angle_offset = (360) + initial_rotation
    color = white

    frame, color = draw_wheel(angle_offset, previous_color, getStringFromColor(color))
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
        
def create_slot_machine_gif(output_path, frames=60, step=5, size=(210, 210)):
    images = {img: Image.open(img).convert("RGB").resize((size[0] // 3, size[1] // 3)) for img in SLOT_IMAGES}
    img_width, img_height = next(iter(images.values())).size
    reel_width = img_width
    reel_height = img_height * 3  # 3 images per reel
    
    # Randomize images for each reel
    reels = [random.sample(SLOT_IMAGES, len(SLOT_IMAGES)) for _ in range(3)]
    
    # Create blank slot machine frame with transparency support
    slot_machine = Image.new("RGB", size, (0, 0, 0, 0))
    
    # Initialize positions for each reel with fractional offsets for smooth motion
    reel_offsets = [random.uniform(0, len(SLOT_IMAGES)) for _ in range(3)]
    stop_frames = [frames // 3 * (i + 1) for i in range(3)]  # Staggered stopping for each reel
    frames_list = []
    final_result = [None] * 3  # Store final stopped image names
    frame = slot_machine.copy()
    for frame_index in range(frames + 60):
        
        frame = slot_machine.copy()
        for i in range(3):  # 3 reels
            reel_img = Image.new("RGBA", (reel_width, reel_height), (0, 0, 0, 0))
            offset = reel_offsets[i] % 1 * img_height  # Get fractional offset for smooth movement
            base_index = int(reel_offsets[i]) % len(reels[i])
            
            for j in range(4):  # Use 4 images to smoothly transition
                img_index = (base_index + j) % len(reels[i])
                img = images[reels[i][img_index]]
                reel_img.paste(img, (0, j * img_height - int(offset)), img)
            frame.paste(reel_img, (i * reel_width, (size[1] - reel_height) // 2), reel_img)
                
        
        # Draw horizontal red line in the middle
        draw = ImageDraw.Draw(frame)
        draw.rectangle([(0, int(size[1] / 3 )), (size[0], int(size[1] / 3 * 2 ))], outline="white", fill = None, width = 5)
        #draw.line([(0, size[1] // 2), (size[0], size[1] // 2)], fill="red", width=5)
        
        
        # Move each reel down smoothly, stopping progressively
        for i in range(3):
            if frame_index <= stop_frames[i]:
                reel_offsets[i] += 0.2  # Slower smooth motion
            else:
                reel_offsets[i] = round(reel_offsets[i])
        
        if frame_index == frames + 30:
            for i in range(3):
                final_result[i] = reels[i][(int(reel_offsets[i]) + 1) % len(reels[i])]

        
        frames_list.append(frame.copy())

    for _ in range(10):  # 10 extra frames for 1 second at 100ms per frame
        frames_list.append(frame.copy())
    frames_list[0].save(output_path, save_all=True, append_images=frames_list[1:], duration=30, loop=1, transparency=0)
    for item in final_result:
        count = final_result.count(item)
        if count == 2 or count == 3:
            return item, count  # Return the value and its count if it's a duplicate (2 or 3 times)
    
    return None, 1