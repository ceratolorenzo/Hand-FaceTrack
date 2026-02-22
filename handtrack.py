# Import the libraries
import cv2
import mediapipe as mp
import math

# Mediapipe e disegno
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mphands = mp.solutions.hands

# Inizializzazione video
cap = cv2.VideoCapture(0)
hands = mphands.Hands()

ball_pos = [200, 200]
ball_radius = 20
ball_speed = 10
ball_angle = 3.5/4 * math.pi
bouncing = False

while True:
    data, image = cap.read()
    # Flip the image
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # Storing the results
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Verifica se le mani sono rilevate
    if results.multi_hand_landmarks:
        # Array per le coordinate degli indici 
        index_finger_tips = []

        # Itera per le mani rilevate
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mphands.HAND_CONNECTIONS)

            # Estrarre la punta dell'indice (8)
            index_tip = hand_landmarks.landmark[8]
            h, w, _ = image.shape
            cx, cy = int(index_tip.x * w), int(index_tip.y * h)
            index_finger_tips.append((cx, cy))
        
        # Se ci sono 2 mani
        if len(index_finger_tips) == 2:
            x1, y1 = index_finger_tips[0]
            x2, y2 = index_finger_tips[1]

            dist_to_line = abs((y2 - y1) * ball_pos[0] - (x2 - x1) * ball_pos[1] + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

            if dist_to_line <= ball_radius:
                # Line bounce
                if bouncing == False:
                    bouncing = True
                    line_angle = math.atan2(abs(y2 - y1), abs(x2 - x1))
                    ball_angle = line_angle - ball_angle
            else:
                bouncing == False

            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            min_thickness = 1
            max_thickness = 10

            line_thickness = int(min_thickness + (max_thickness - min_thickness) / (distance / 200))
            line_thickness = max(min_thickness, min(max_thickness, line_thickness))  # Assicura che sia nel range

            cv2.line(image, index_finger_tips[0], index_finger_tips[1], (0, 255, 0), line_thickness)
    
    ball_pos[0] += ball_speed * math.sin(ball_angle + math.pi/2)
    ball_pos[1] += ball_speed * math.cos(ball_angle + math.pi/2)

    # Wall bounce
    if ball_pos[0] - ball_radius <= 0 or ball_pos[0] + ball_radius >= image.shape[1]:
        ball_angle = math.pi - ball_angle
    if ball_pos[1] - ball_radius <= 0 or ball_pos[1] + ball_radius >= image.shape[0]:
        ball_angle = -ball_angle

    cv2.circle(image, (int(ball_pos[0]), int(ball_pos[1])), ball_radius, (0, 0, 255), -1)

    cv2.imshow('Handtracker', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()