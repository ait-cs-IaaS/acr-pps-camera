from flask import Flask, Response, jsonify, render_template, request
import cv2
import threading
import time
import datetime
import hashlib
import yaml
import logging

app = Flask(__name__)

default_vid = "video_extra/door.mp4"  
tmp_vid = None
lock = threading.Lock()
text_message = "pending ..."

with open("name_mapping.yml", "r") as file:
    name_mapping = yaml.safe_load(file)

def generate_frames():
    global tmp_vid
    global text_message

    while True:
        with lock:
            video_source = tmp_vid if tmp_vid else default_vid

        cap = cv2.VideoCapture(video_source)

        if video_source != default_vid:
            tmp_vid = None
        else:
            text_message = "pending ..."

        # Get the video's native frame rate
        fps = cap.get(cv2.CAP_PROP_FPS) or 30  
        frame_delay = 1 / fps

        while True:

            success, frame = cap.read()

            if not success:
                break

            # Add timestamp to the frame
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (40, 50), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1,)

            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()

            # Stream the frame as an HTTP multipart response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            time.sleep(frame_delay)

        cap.release()

@app.route('/feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/text_feed')
def text_feed():
    return jsonify({"message": text_message})

@app.route('/')
def hmi():
    return render_template('index.html')

@app.route('/video/<direction>/<video_id>', methods=['POST'])
def change_feed(direction, video_id):
    global tmp_vid
    global default_vid
    global text_message

    if direction == "extra":
        default_vid = f"video_{ direction }/{ video_id }.mp4"    
    else:
        with lock:
            tmp_vid = f"video_{ direction }/{ video_id }.mp4"
        
        # Get access log info 
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        employee_name = name_mapping.get(video_id, "Unknown")
        state = f"{ ('entering' if direction == 'in' else 'leaving').upper() }"

        hash_object = hashlib.sha256(employee_name.encode())
        hash_hex = hash_object.hexdigest()
        employee_id = f"{ (hash_hex[:8]).upper() if employee_name != 'Unknown' else '---' }"

        # Write to logfile
        with open("access.log", "a") as file:
            file.write(f"{ timestamp } [ACCESS-INFO] - Employee { employee_id }, { employee_name } { state }\n")

        # Choose image
        image_file = f"static/{ video_id }.jpg"
        
        # Format access log on frontend
        text_message = f"""
            <table>
                <tr>
                    <td><stron>ID:</strong></td>
                    <td>{ employee_id }</td>
                </tr>
                <tr>
                    <td><stron>Name:</strong></td>
                    <td>{ employee_name }</td>
                </tr>
                <tr>
                    <td><stron>Timestamp:</strong></td>
                    <td>{ timestamp }</td>
                </tr>
                <tr>
                    <td><stron>State:</strong></td>
                    <td>{ state }</td>
                </tr>
                <tr>
                    <td colspan=2>
                        <img src="{ image_file }"/>
                    </td>
                </tr>
            </table>
            """

    return "Temporary feed started, will return to default when done."

if __name__ == '__main__':
    app.run()
