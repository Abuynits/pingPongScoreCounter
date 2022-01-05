import cv2


class Line:
    def __init__(self, pointA, pointB):
        self.pointA = pointA
        self.pointB = pointB

    def drawLine(self, frame):
        cv2.line(frame, (int(self.pointA.x), (self.pointA.y)), (int(self.pointB.x), (self.pointB.y)), (204, 204, 0), 3)
