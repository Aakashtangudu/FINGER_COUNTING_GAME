import cv2
import mediapipe as mp
import random
import time
import pyttsx3
import tkinter as tk
from tkinter import messagebox

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize the TTS engine
engine = pyttsx3.init()

# Function to detect if a finger is open or closed
def finger_status(hand_landmarks):
    status = []
    finger_tips = [4, 8, 12, 16, 20]
    finger_pip = [3, 7, 11, 15, 19]

    # Thumb: Compare x-coordinates of tip and PIP
    if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_pip[0]].x:
        status.append(1)
    else:
        status.append(0)

    # Other fingers: Compare y-coordinates of tip and PIP
    for i in range(1, 5):
        if hand_landmarks.landmark[finger_tips[i]].y < hand_landmarks.landmark[finger_pip[i]].y:
            status.append(1)
        else:
            status.append(0)
    
    return status

# Function to speak the number of fingers to show
def speak_number(number):
    engine.say(f"Show {number} fingers")
    engine.runAndWait()

# Function to speak a congratulatory message
def speak_congratulations():
    engine.say("Congratulations! You showed the correct number of fingers every time!")
    engine.runAndWait()

# Function to speak an error message
def speak_error(message):
    engine.say(message)
    engine.runAndWait()

# Function to display the score in a new tkinter window
def display_score(score):
    root = tk.Tk()
    root.title("Game Over")
    
    # Create a messagebox with the final score
    messagebox.showinfo("Game Over", f"Your final score is: {score}")

    # End the tkinter main loop
    root.mainloop()

# Initialize variables for the game
cap = cv2.VideoCapture(0)
score = 0

with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    
    while cap.isOpened():
        target_fingers = random.randint(1, 5)
        start_time = time.time()
        speak_number(target_fingers)
        
        correct_shown = False
        
        while time.time() - start_time < 5:  # 5-second time limit for each round
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    status = finger_status(hand_landmarks)
                    open_fingers = sum(status)

                    # Display the target number and the number of open fingers on the image
                    cv2.putText(image, f"Show: {target_fingers}", (10, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(image, f"Fingers: {open_fingers}", (10, 100), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    
                    if open_fingers == target_fingers:
                        correct_shown = True
                        score += 10  # Increment score by 10 for each correct answer
                        engine.say(f"Correct, you showed {open_fingers} fingers")
                        engine.runAndWait()
                        time.sleep(1)  # Short pause before next round
                        break

            cv2.imshow('MediaPipe Hands', image)
            if cv2.waitKey(5) & 0xFF == 27:  # Exit if 'Esc' key is pressed
                cap.release()
                cv2.destroyAllWindows()
                engine.say(f"Game interrupted! Your score: {score}")
                engine.runAndWait()
                display_score(score)
                exit()

        if not correct_shown:
            speak_error(f"Game over! You failed to show {target_fingers} fingers in time.")
            break  # End the game if the player fails

    cap.release()
    cv2.destroyAllWindows()

    # Display the final score
    display_score(score)
