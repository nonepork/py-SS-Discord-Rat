import cv2
import pyautogui
import numpy as np

screen_width, screen_height = pyautogui.size()
screen_size = (screen_width, screen_height)  # Change this to match your screen resolution
fps = 30
output_filename = "screen_record.mp4"

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out = cv2.VideoWriter(output_filename, fourcc, fps, screen_size)


for i in range(fps*15):
    # Capture screen content
    frame = pyautogui.screenshot()
    frame = np.array(frame)

    # Convert BGR format (used by OpenCV) to RGB format
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Write the frame to the video file
    out.write(frame)

# Release the VideoWriter and close the OpenCV windows
out.release()
cv2.destroyAllWindows()

