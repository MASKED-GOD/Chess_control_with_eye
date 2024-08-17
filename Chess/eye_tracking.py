import cv2
import mediapipe as mp
import pyautogui

# Initialize the video capture
cam = cv2.VideoCapture(0)

# Initialize the face mesh detector
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Get screen size
screen_w, screen_h = pyautogui.size()

# Start the loop
try:
    while True:
        success, frame = cam.read()
        if not success:
            break

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and find face landmarks
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks

        frame_h, frame_w, _ = frame.shape

        if landmark_points:
            landmarks = landmark_points[0].landmark
            for id, landmark in enumerate(landmarks[474:478]):
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
                if id == 1:
                    screen_x = screen_w / frame_w * x
                    screen_y = screen_h / frame_h * y
                    pyautogui.moveTo(screen_x, screen_y)

            left = [landmarks[145], landmarks[159]]
            for landmark in left:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)

            # Adjusted the click condition
            if abs(left[0].y - left[1].y) <= 0.01:
                pyautogui.click()
                pyautogui.sleep(1)

        cv2.imshow('Eye control Mouse', frame)
        
        # Check for exit key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Release resources
    cam.release()
    cv2.destroyAllWindows()
