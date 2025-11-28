import cv2
import mediapipe as mp
import numpy as np

# Initialize the MediaPipe Pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Angle calculation function
def calculate_angle(a, b, c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

    return np.degrees(angle)

# Start the camera
cap = cv2.VideoCapture(0)

while cap.isOpened():

    ret, frame = cap.read()
    if not ret:
        break

    # Convert BGR to RGB and feed it to the MediaPipe model
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        # Extract the keypoints
        landmarks = results.pose_landmarks.landmark

        # Shoulder and head points 
        shoulder_left = [int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * frame.shape[1]),
                         int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame.shape[0])]
        
        shoulder_right = [int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * frame.shape[1]),
                          int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame.shape[0])]
        
        head_top = [int(landmarks[mp_pose.PoseLandmark.NOSE].x * frame.shape[1]),
                    int((landmarks[mp_pose.PoseLandmark.NOSE].y - 0.1) * frame.shape[0])]  

        # The average of the shoulders was taken
        shoulder_mid = [(shoulder_left[0] + shoulder_right[0]) // 2,
                        (shoulder_left[1] + shoulder_right[1]) // 2]

        # Hip and leg points
        hip_left = [int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].x * frame.shape[1]),
                    int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].y * frame.shape[0])]
        
        hip_right = [int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x * frame.shape[1]),
                     int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y * frame.shape[0])]
        
        ankle_left = [int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x * frame.shape[1]),
                      int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y * frame.shape[0])]
        
        ankle_right = [int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x * frame.shape[1]),
                       int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y * frame.shape[0])]

        # Angle between the shoulders and the head 
        head_angle = calculate_angle(shoulder_left, shoulder_mid, head_top)

        # Hip and leg angle 
        hip_mid = [(hip_left[0] + hip_right[0]) // 2,
                   (hip_left[1] + hip_right[1]) // 2]
        
        leg_angle_left = calculate_angle(hip_mid, hip_left, ankle_left)

        leg_angle_right = calculate_angle(hip_mid, hip_right, ankle_right)

        leg_angle = (leg_angle_left + leg_angle_right) / 2  # The average was calculated

        

        # The status has been determined
        if (head_angle > 88 and head_angle<94) and  (leg_angle < 93 and leg_angle >87):
            posture_status = "Good Posture"
            color = (0, 255, 0)  # green

        else:
            posture_status = "Bad Posture"
            color = (0, 0, 255)  # red

        # The angles were displayed on the screen
        cv2.putText(frame, f"Head Angle: {int(head_angle)}", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        cv2.putText(frame, f"Leg Angle: {int(leg_angle)}", (50, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        cv2.putText(frame, posture_status, (50, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Let’s add lines that display the angles
        cv2.line(frame, tuple(shoulder_mid), tuple(head_top), (255, 0, 0), 3)  # Head angle line
        cv2.line(frame, tuple(hip_mid), tuple(hip_left), (0, 255, 0), 3)  # Hip line 
        cv2.line(frame, tuple(hip_left), tuple(ankle_left), (0, 255, 0), 3)  # Left leg line
        cv2.line(frame, tuple(hip_right), tuple(ankle_right), (0, 255, 0), 3)  # Right leg line

        # Let’s mark the points that indicate the angle
        cv2.circle(frame, tuple(shoulder_mid), 5, (255, 0, 0), -1)  # Head angle point
        cv2.circle(frame, tuple(head_top), 5, (255, 0, 0), -1)  
        cv2.circle(frame, tuple(hip_mid), 5, (0, 255, 0), -1)  # Hip point
        cv2.circle(frame, tuple(ankle_left), 5, (0, 255, 0), -1)
        cv2.circle(frame, tuple(ankle_right), 5, (0, 255, 0), -1)

        # Pose drawing
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Display on the screen
    cv2.imshow("Posture Detection", frame)

    
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()



