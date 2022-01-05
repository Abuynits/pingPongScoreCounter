import math


class PixelPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distanceTo(self, center_x, center_y):
        return math.sqrt((center_x - self.x) * (center_x - self.x) + (center_y - self.y) * (center_y - self.y))

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y
    def __str__(self):
        print(str(self.get_x) +","+ str(self.get_y()) )
