import cv2
import mediapipe as mp
import numpy as np
import time

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5,
    refine_landmarks=True  # Required for iris landmarks
)

mp_drawing = mp.solutions.drawing_utils

# Iris Focus configuration
drawing_spec = mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=1, circle_radius=2)
connection_spec = mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=1)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()

    start = time.time()

    # flip the image horizontally
    # convert the color space from BGR to RGB
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # to improve performance
    image.flags.writeable = False

    results = face_mesh.process(image)

    # to improve performance
    image.flags.writeable = True

    # convert color space back from RGB to BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    img_h, img_w, img_c = image.shape
    face_3d = []
    face_2d = []

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):
                if idx == 33 or idx == 263 or idx == 1 or idx == 168 or idx == 61 or idx == 291 or idx == 199:
                    if idx == 168:
                        nose_2d = (lm.x * img_w, lm.y * img_h)
                        nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)

                    x, y = int(lm.x * img_w), int(lm.y * img_h)

                    # get the 2d coordinates
                    face_2d.append([x, y])

                    # get the 3d coordinates
                    face_3d.append([x, y, lm.z])

            # convert to the numpy array
            face_2d = np.array(face_2d, dtype=np.float64)
            face_3d = np.array(face_3d, dtype=np.float64)

            # camera matrix
            focal_length = img_w
            cam_matrix = np.array([[focal_length, 0, img_h / 2],
                                   [0, focal_length, img_w / 2],
                                   [0, 0, 1]])
                
            # distortion parameters
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            # solve PnP
            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

            # rotational matrix
            rmat, jac = cv2.Rodrigues(rot_vec)

            # get angles
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            # get the rotation degrees
            x = angles[0] * 360
            y = angles[1] * 360
            z = angles[2] * 360

            # display nose direction
            nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)

            p1 = (int(nose_2d[0]), int(nose_2d[1]))
            p2 = (int(nose_2d[0] + y*10), int(nose_2d[1] - x*10))

            cv2.line(image, p1, p2, (255, 0, 0), 3)

        end = time.time()
        totalTime = end - start

        # for future use case
        fps = 1 / totalTime

        # Draw iris landmarks with magenta color
        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=mp_face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=drawing_spec,
            connection_drawing_spec=connection_spec
        )

    cv2.imshow("Face Position Tracker", image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()