import cv2
import datetime
import time

class VideoStreamHandler:
    def __init__(self, mp4_files, screen_width=1920, screen_height=1080):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.mp4_files = mp4_files
        self.current_video_path = None
        self.video_capture = None
        self.breach_mode = False
        self.last_frame = None
        self.counter = 0

    def get_video_path(self, current_mp4, breach_mode):
        # Determines the correct video path to use
        return self.mp4_files[4] if breach_mode else current_mp4

    def init_video_capture(self, video_path):
        # Initializes the video capture if not already initialized or if the video path changes
        if self.video_capture is None or self.current_video_path != video_path:
            if self.video_capture is not None:
                self.video_capture.release()

            self.video_capture = cv2.VideoCapture(video_path)
            if not self.video_capture.isOpened():
                raise ValueError(f"Error opening video stream or file: {video_path}")

            self.current_video_path = video_path

    def process_frame(self, frame):
        # Resize and add timestamp
        frame = cv2.resize(frame, (self.screen_width, self.screen_height))
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

        ret, jpeg = cv2.imencode(".jpg", frame)
        if ret:
            self.last_frame = jpeg.tobytes()

def generate_frames(self, current_mp4, camera_freeze, open_sesame, switch_feed):
    global stop_stream

    try:
        while True:
            # Initialize video capture
            video_path = self.get_video_path(current_mp4, self.breach_mode)
            self.init_video_capture(video_path)

            while True:
                # Check if the stream should be stopped
                if stop_stream:
                    print("[INFO] Stopping stream as requested.")
                    return  # Stop the generator, exit the function gracefully

                # Read a new frame from the video capture
                success, frame = self.video_capture.read()

                # Restart video if at the end
                if not success:
                    self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                # Only process if not camera frozen
                if not camera_freeze:
                    self.process_frame(frame)

                # Yield the frame for streaming
                if self.last_frame is not None:
                    try:
                        yield (b"--frame\r\n"
                               b"Content-Type: image/jpeg\r\n\r\n" + self.last_frame + b"\r\n")
                    except (BrokenPipeError, GeneratorExit):
                        print("[INFO] Client disconnected. Stopping video stream.")
                        return  # Stop the generator gracefully

                # Handle video switching after a certain count
                if not self.breach_mode:
                    if open_sesame:
                        self.counter += 1
                        if self.counter >= 500:
                            switch_feed()

                # Sleep to control frame rate
                time.sleep(0.03)

    except (GeneratorExit, BrokenPipeError):
        print("[INFO] Generator or pipe broken. Cleaning up resources.")
    finally:
        if self.video_capture is not None:
            self.video_capture.release()
            print("[INFO] Released video capture.")