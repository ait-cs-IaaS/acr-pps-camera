from flask import Flask, Response
import cv2
import time
import datetime

# Had to do the following too:
#   `sudo apt-get update && sudo apt-get install ffmpeg libsm6 libxext6  -y`

# Define App
app = Flask(__name__)
ip_addr = '192.168.10.240'
port = 5000

# List of MP4 file paths
mp4_files = ['vid/door_closed.mp4', 'vid/door_open.mp4']
current_mp4 = mp4_files[0]

open_sesame = False
counter = 0

camera_freeze = False
last_frame = None

def generate_frames():
    global counter
    while True:
        video_path = current_mp4

        video_capture = cv2.VideoCapture(video_path) 
        
        while video_path == current_mp4:    
            success, frame = video_capture.read()
            if not success:
                # Restart the video when it ends
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
        
             # Add timestamp to the frame
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

            if not camera_freeze:
                # Convert frame to JPEG image
                ret, jpeg = cv2.imencode('.jpg', frame)
                frame_bytes = jpeg.tobytes()
                last_frame = frame_bytes
            
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # This determines how long the opening video plays for
            if open_sesame:
                counter = counter + 1
                if counter >= 50:
                    switch_feed()
            time.sleep(0.05)

@app.route('/switch')
def switch_feed():
    global current_mp4
    global open_sesame
    global counter
    
    if open_sesame == True:
        counter = 0
        open_sesame = False
        current_mp4 = mp4_files[0]
    else:
        open_sesame = True
        current_mp4 = mp4_files[1]
    
    # if current_mp4 == mp4_files[0]:
    #     current_mp4 = mp4_files[1]
    # else:
    #     current_mp4 = mp4_files[0]
    return 'Feed Change Requested'

# Freeze camera feed
@app.route('/frz')
def toggle_freeze():
    global camera_freeze
    if camera_freeze == True:
        camera_freeze = False
        return 'Camera Un-Frozen'
    else:
        camera_freeze = True
        return 'Camera Frozen'
    
    

@app.route('/feed')
def stream_gif():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host = ip_addr, port = port)