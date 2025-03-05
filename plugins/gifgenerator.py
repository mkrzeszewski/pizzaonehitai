from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
from datetime import datetime
import math
import imageio
import time
import cv2
from concurrent.futures import ThreadPoolExecutor

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
        
def create_slot_machine_gif(output_path, frames=60, step=5, size=(180, 180)):
    t_total = time.time()
    
    # 1. Preprocess images with OpenCV
    t1 = time.time()
    slot_size = (size[0] // 3, size[1] // 3)
    images = {}
    for path in SLOT_IMAGES:
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        img = cv2.resize(img, slot_size)
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        images[path] = img
    print(f"Image loading: {time.time()-t1:.3f}s")

    # 2. Precompute reel sequences
    t1 = time.time()
    img_h = slot_size[1]
    reels = [random.sample(SLOT_IMAGES, len(SLOT_IMAGES)) for _ in range(3)]
    reel_offsets = [random.uniform(0, len(SLOT_IMAGES)) for _ in range(3)]
    stop_frames = [frames // 3 * (i + 1) for i in range(3)]

    # 3. Create base frame
    base_frame = np.zeros((size[1], size[0], 4), dtype=np.uint8)
    
    # 4. Precompute coordinates
    reel_y = (size[1] - 3*img_h) // 2
    positions = [(i*slot_size[0], reel_y) for i in range(3)]
    middle_rect = [(0, size[1]//3), (size[0], 2*size[1]//3)]

    # 5. Main animation loop
    frames_list = []
    final_result = [None]*3
    
    for frame_idx in range(frames + 60):
        current_frame = base_frame.copy()
        
        # Compose reels
        for i in range(3):
            # Calculate vertical offset
            offset = reel_offsets[i] % 1 * img_h
            base_idx = int(reel_offsets[i]) % len(reels[i])
            
            # Composite 4 images with alpha blending
            reel_buffer = np.zeros((3*img_h, slot_size[0], 4), dtype=np.uint8)
            for j in range(4):
                img_idx = (base_idx + j) % len(reels[i])
                alpha = images[reels[i][img_idx]][:, :, 3:].astype(float)/255.0
                y_pos = j*img_h - int(offset)
                
                if y_pos + img_h <= 0 or y_pos >= 3*img_h:
                    continue
                
                # Alpha blending
                y_start = max(y_pos, 0)
                y_end = min(y_pos + img_h, 3*img_h)
                buffer_slice = reel_buffer[y_start:y_end]
                img_slice = images[reels[i][img_idx]][y_start-y_pos:y_end-y_pos]
                
                buffer_slice[:, :, :3] = buffer_slice[:, :, :3]*(1 - alpha[y_start-y_pos:y_end-y_pos]) + \
                                       img_slice[:, :, :3]*alpha[y_start-y_pos:y_end-y_pos]
                buffer_slice[:, :, 3] = np.maximum(buffer_slice[:, :, 3], img_slice[:, :, 3])

            # Composite reel to frame
            x, y = positions[i]
            frame_slice = current_frame[y:y+3*img_h, x:x+slot_size[0]]
            alpha = reel_buffer[:, :, 3:].astype(float)/255.0
            frame_slice[:, :, :3] = frame_slice[:, :, :3]*(1 - alpha) + reel_buffer[:, :, :3]*alpha
            frame_slice[:, :, 3] = np.maximum(frame_slice[:, :, 3], reel_buffer[:, :, 3])

        # Draw middle rectangle
        cv2.rectangle(current_frame, 
                     (0, middle_rect[0][1]), 
                     (size[0], middle_rect[1][1]), 
                     color=(200, 200, 200, 255), 
                     thickness=5)

        # Update reel positions
        for i in range(3):
            if frame_idx <= stop_frames[i]:
                reel_offsets[i] += 0.2
            else:
                reel_offsets[i] = round(reel_offsets[i])

        # Final result detection
        if frame_idx == frames + 30:
            for i in range(3):
                final_result[i] = reels[i][(int(reel_offsets[i]) + 1) % len(reels[i])]

        # Convert to RGB and store
        frames_list.append(cv2.cvtColor(current_frame, cv2.COLOR_BGRA2RGB))

    # Add final frames
    last_frame = frames_list[-1]
    frames_list.extend([last_frame]*10)

    # 6. Optimized encoding
    def optimize_frame(frame):
        img = Image.fromarray(frame)
        # First convert to palette mode with adaptive colors
        img = img.convert('P', palette=Image.ADAPTIVE, colors=128)
        # Then quantize to optimize the palette
        return img.quantize(method=Image.FASTOCTREE)

    t1 = time.time()
    
    # Convert all frames in parallel
    with ThreadPoolExecutor() as executor:
        optimized_frames = list(executor.map(optimize_frame, frames_list))

    # Save with optimized settings
    optimized_frames[0].save(
        output_path,
        save_all=True,
        append_images=optimized_frames[1:],
        duration=30,
        loop=0,
        optimize=True,
        disposal=2,
        compress_level=1
    )

    print(f"Saving time: {time.time()-t1:.3f}s")

    # Result calculation
    for item in final_result:
        count = final_result.count(item)
        if count >= 2:
            return item, count
    return None, 1