import cv2
import time
import math
import mediapipe as mp

mpPose = mp.solutions.pose
mpDraw = mp.solutions.drawing_utils
pose = mpPose.Pose()
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
yellow = (0, 255, 255)

def calculate_angle(point1, point2, point3):
    a = math.dist(point1, point2)
    b = math.dist(point2, point3)
    c = math.dist(point1, point3)

    cosC = (a**2 + b**2 - c**2) / (2 * a * b)
    angleC = math.degrees(math.acos(cosC))

    return round(angleC, 2)

def draw_landmark_points(img, landmarks):
    for id, lm in enumerate(landmarks):
        h, w, c = img.shape
        cx, cy = int(lm.x * w), int(lm.y * h)

        if id in [11, 23, 25, 27]:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0))
            cv2.putText(img, str(id), (cx - 10, cy - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            if id == 11:
                point_11 = (cx, cy)
            elif id == 23:
                point_23 = (cx, cy)
            elif id == 25:
                point_25 = (cx, cy)
            elif id == 27:
                point_27 = (cx, cy)

    return point_11, point_23, point_25, point_27, cx, cy

def validate_initial_position(angle_23, angle_25):
    if (120 <= angle_23 <= 150 and 70 <= angle_25 <= 100):
        return True
    else:
        return False

def validate_initial_sit_up(angle_25, initial_position_verified):
    if (70 <= angle_25 <= 100) and initial_position_verified:
        return True
    else:
        return False

def draw_correct_position(img):
    cv2.putText(img, "Posisi Benar", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, green, 2)

def draw_wrong_position(img):
    cv2.putText(img, "Posisi Salah", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, red, 2)

def draw_remaining_time(img, remaining_time):
    cv2.putText(img, "Remaining Time: {:.2f}".format(remaining_time), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, yellow, 2)

def draw_count_sit_up(img, situp_count):
    cv2.putText(img, "Sit up: " + str(situp_count // 2), (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, yellow, 2)