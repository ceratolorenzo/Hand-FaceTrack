# HOW TO RUN:
# python3 main.py
# ERROR? `ls /dev/cu.usb*` to check the serial port is correct.

# Desktop/Projects/Un-finished/HandTrack/pytest

import cv2
import mediapipe as mp
import serial

# Mediapipe setup
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mphands = mp.solutions.hands

# Video capture
cap = cv2.VideoCapture(0)
hands = mphands.Hands()

# In case serial port malfunctions:
# $ lsof | grep usbmodem14101
# $ kill -9 PID (PID is no. after serial-mo)
arduino = serial.Serial('/dev/cu.usbmodem14101', 9600)

# Function to check if a finger is raised
def is_finger_raised(landmarks, tip_idx, lower_idx):
    if landmarks[tip_idx].y < landmarks[lower_idx].y:
        return 1
    else:
        return 0

while True:
    data, image = cap.read()
    # Flip the image
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # Process the image
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        # Draw landmarks
        mp_drawing.draw_landmarks(image, hand_landmarks, mphands.HAND_CONNECTIONS)

        # Get the list of landmarks
        landmarks = hand_landmarks.landmark

        # Initialize array for fingers (except thumbs)
        fingers = [0] * 8

        if results.multi_handedness[0].classification[0].label == "Left":
            fingers[3] = is_finger_raised(landmarks, 8, 7)
            fingers[2] = is_finger_raised(landmarks, 12, 11)
            fingers[1] = is_finger_raised(landmarks, 16, 15)
            fingers[0] = is_finger_raised(landmarks, 20, 19)
        else:
            fingers[4] = is_finger_raised(landmarks, 8, 7)
            fingers[5] = is_finger_raised(landmarks, 12, 11)
            fingers[6] = is_finger_raised(landmarks, 16, 15)
            fingers[7] = is_finger_raised(landmarks, 20, 19)

        if len(results.multi_hand_landmarks) > 1:
            hand_landmarks = results.multi_hand_landmarks[1]
            # Draw landmarks
            mp_drawing.draw_landmarks(image, hand_landmarks, mphands.HAND_CONNECTIONS)

            # Get the list of landmarks
            landmarks = hand_landmarks.landmark

            if results.multi_handedness[1].classification[0].label == "Left":
                fingers[3] = is_finger_raised(landmarks, 8, 7)
                fingers[2] = is_finger_raised(landmarks, 12, 11)
                fingers[1] = is_finger_raised(landmarks, 16, 15)
                fingers[0] = is_finger_raised(landmarks, 20, 19)
            else:
                fingers[4] = is_finger_raised(landmarks, 8, 7)
                fingers[5] = is_finger_raised(landmarks, 12, 11)
                fingers[6] = is_finger_raised(landmarks, 16, 15)
                fingers[7] = is_finger_raised(landmarks, 20, 19)
        
        # Send the 8-bit value to Arduino as a byte
        # Flip fingers array (explanation in arduino file)
        fingers.reverse()
        byte_val = sum([(fingers[i]) << i for i in range(8)])
        arduino.write(byte_val.to_bytes(1, 'little'))

        print(f"Fingers raised: {fingers}")

    cv2.imshow('Handtracker', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()