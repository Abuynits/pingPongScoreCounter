import numpy as np
import cv2

# Create the circle
colour = (0, 255, 0)
lineWidth = 3  # -1 will result in filled circle
radius = 30
point = (0, 0)


# function for detecting left mouse click
def click(event, x, y, flags, param):
    global point
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Pressed", x, y)
        point = (x, y)


# event handler
cv2.namedWindow("Frame")  # must match the imshow 1st argument
cv2.setMouseCallback("Frame", click)

cap = cv2.VideoCapture(0)

# Loop for video stream
while (True):

    stream = cv2.waitKey(1)  # Load video every 1ms and to detect user entered key

    # Read from videoCapture stream and display
    ret, frame = cap.read()
    cv2.circle(frame, point, radius, colour, lineWidth)  # circle properties as arguments
    frame = cv2.resize(frame, (0, 0), fx=0.99, fy=.99)  # this fx,fy value will be explained in post
    cv2.imshow("Frame", frame)

    if stream & 0XFF == ord('q'):  # If statement to stop loop,Letter 'q' is the escape key
        break  # get out of loop

cap.release()
cv2.destroyAllWindows()