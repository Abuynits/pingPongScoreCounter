import cv2
import numpy as np

from Line import Line
from PixelPoint import PixelPoint

np.seterr(over='ignore')
cap = cv2.VideoCapture(0)  # the first cam in your system
showEdits = False
doOnce = False
tolerance = 10
resizeX = 200
resizeY = 100
original_x = 0
original_y = 0
aveLoopVal = 1
redo = True
constantlyUpdate = True
font = cv2.FONT_HERSHEY_SIMPLEX
pixelList = []
homeRGB = (0, 0, 0)
testRGB = (0, 0, 0)
home_b = (homeRGB[0])
home_g = (homeRGB[1])
home_r = (homeRGB[2])
point = (-1, -1)
newPoint = (-1, -1)
editsToDo = 0
currentTester = "HV tester"
refuseDistance = 1000000
setTableBounds = True
tableBoundClick = False
addLines = True
currentTableListLocation = 0

averageCenter = (-1, -1)
lastAverageCenter = (-1, -1)
tableBounds = [PixelPoint(-100, -100), PixelPoint(-100, -100), PixelPoint(-100, -100), PixelPoint(-100, -100)]
lineList = []
bounds = [-1, -1, -1, -1]
distanceScan = 100


# TODO: need to find way to reject point if far enough from the enter - if it is an outlier

def lookForTableBounds(frame):
    global currentTableListLocation, tableBounds, tableBoundClick
    if tableBoundClick:
        x = point[0]
        y = point[1]
        # TODO: possible bug with the table bound location
        tableBounds[currentTableListLocation] = PixelPoint(x, y)
        currentTableListLocation += 1
        if currentTableListLocation == 4:
            currentTableListLocation = 0
        tableBoundClick = False
        # for loc in tableBounds:
        #     print(str(loc.x) + ","+ str(loc.y))
    cv2.circle(frame, (int(newPoint[0]), int(newPoint[1])), 5, (255, 255, 0), 2)


def printDebug(b, r, g):
    print("found: " + str(b) + " and " + str(r) + " and " + str(g))
    print("original: " + str(homeRGB))
    print("-------------")
    print(r - tolerance)
    print(home_r)
    print(r + tolerance)
    print("-------------")
    print(g - tolerance)
    print(home_g)
    print(g + tolerance)
    print("-------------")
    print(b - tolerance)
    print(home_b)
    print(b + tolerance)


def getXRescale(xLoc):
    multBy = original_y / resizeX
    return xLoc * multBy


def getYRescale(yLoc):
    multBy = original_x / resizeY
    return yLoc * multBy


def findCenterPixels(pixelList, frame):
    global averageCenter, lastAverageCenter
    xSum = 0
    ySum = 0
    # print(pixelList)
    for point in pixelList:
        xSum = xSum + int(point.x)
        ySum = ySum + int(point.y)
    lenList = len(pixelList)
    if not (lenList == 0):
        xSum = xSum / lenList
        ySum = ySum / lenList
        # print(xSum)
        # print(ySum)
        # need to rescale to Original x - originalX to
        #
    rescaledX = getXRescale(ySum)
    rescaledY = getYRescale(xSum)
    lastAverageCenter = averageCenter
    averageCenter = (rescaledX, rescaledY)
    cv2.putText(frame, str("averageLoc " + str(int(rescaledX)) + " ," + str(int(rescaledY))), (50, 125), font, 1,
                (0, 0, 255), 1,
                cv2.LINE_AA, False)

    # calculation of the averages - need to find the average, and then for each get the distance to the center point


def perfromRGBEdits(b, r, g):
    if ((r - tolerance) < home_r & home_r < (r + tolerance)) & (
            (g - tolerance) < home_g & home_g < (g + tolerance)) & (
            (b - tolerance) < home_b & home_b < (b + tolerance)):
        #  print(str(home_b) + " and " + str(home_g) + " and " + str(home_r))
        #  printDebug(b,r,g)
        return True
    return False


def rgb_to_hsv(r, g, b):
    # R, G, B values are divided by 255
    # to change the range from 0..255 to 0..1:
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    # h, s, v = hue, saturation, value
    cmax = max(r, g, b)  # maximum of r, g, b
    cmin = min(r, g, b)  # minimum of r, g, b
    diff = cmax - cmin  # diff of cmax and cmin.

    # if cmax and cmax are equal then h = 0
    if cmax == cmin:
        h = 0

    # if cmax equal r then compute h
    elif cmax == r:
        h = (60 * ((g - b) / diff) + 360) % 360

    # if cmax equal g then compute h
    elif cmax == g:
        h = (60 * ((b - r) / diff) + 120) % 360

    # if cmax equal b then compute h
    elif cmax == b:
        h = (60 * ((r - g) / diff) + 240) % 360

    # if cmax equal zero
    if cmax == 0:
        s = 0
    else:
        s = (diff / cmax) * 100

    # compute v
    v = cmax * 100
    return h, s, v


def performHEdits(b, r, g):
    (current_h, current_s, current_v) = rgb_to_hsv(r, g, b)
    (home_h, home_s, hove_v) = rgb_to_hsv(home_r, home_g, home_b)
    if int(current_h) - tolerance < int(home_h) & int(home_h) < int(current_h) + tolerance:
        if int(current_s) - tolerance < int(home_s) & int(home_s) < int(current_s) + tolerance:
            return True
    return False


def performHdits(b, r, g):
    (current_h, current_s, current_v) = rgb_to_hsv(r, g, b)
    (home_h, home_s, hove_v) = rgb_to_hsv(home_r, home_g, home_b)
    if int(current_h) - tolerance < int(home_h) & int(home_h) < int(current_h) + tolerance:
        return True
    return False


def performCenterCalculation(pixelList, frame):
    findCenterPixels(pixelList, frame)
    removeOutliers()
    findCenterPixels(pixelList, frame)
    cv2.rectangle(frame, (int(averageCenter[0] - 5), int(averageCenter[1] - 5)),
                  (int(averageCenter[0] + 5), int(averageCenter[1] + 5)),
                  (0, 255, 255), 2)
    pixelList.clear()


# TODO: replace removeOutliers with a tracking method that will look where the ball is and search the predicted area
def removeOutliers():
    for loc in pixelList:
        if loc.distanceTo(averageCenter[0], averageCenter[1]) > refuseDistance:
            pixelList.remove(loc)


def getSearchBounds(frame):
    if lastAverageCenter[0] == 0:
        return 0, 0, len(frame[0]), len(frame)
    else:
        leftXBound = max(averageCenter[0] - distanceScan, 0)
        leftYBound = max(averageCenter[1] - distanceScan, 0)
        rightXBound = min(averageCenter[0] + distanceScan, original_y)
        rightYBound = min(averageCenter[1] + distanceScan, original_x)

        return leftXBound, leftYBound, rightXBound, rightYBound


def perfromEdits(frame, bounds):
    global homeRGB, tolerance, home_b, home_g, home_r
    home_b = (homeRGB[0])
    home_g = (homeRGB[1])
    home_r = (homeRGB[2])

    # TODO: make forloop less monkey

    # for x in range(int(bounds[0]), int(bounds[2])):
    #    for y in range(int(bounds[1]), int(bounds[3])):
    # control the rest of the image as much as possible
    # want a top view - pretty sure tha tyou will see it
    # maybe try the sound - top view camera and then the mic - need to tell difference betwee nhitting the ground and hitting the paddl -
    # top view and sound k nearest neighbor to detect sound - step1 - start to try to get a sense of the sound forms
    # - high frequerncy sound in a narrow range of freqency- detect spikes in the band depending how do work - need to know beginning of the point
    for x in range(len(frame)):
        for y in range(len(frame[0])):
            (b, g, r) = frame[x][y]
            # perfromRGBEdits(b, r, g)
            if editsToDo == 0:
                test = performHEdits(b, r, g)
            elif editsToDo == 1:
                test = performHdits(b, r, g)
            else:
                test = perfromRGBEdits(b, r, g)
            if test:
                p = PixelPoint(x, y)
                frame[x][y] = (255, 0, 0)
                pixelList.append(p)

            # else:
            #     frame[x][y] = (255, 255, 255)

    # for point in pixelList:
    #     print(str(point.get_x()) + ", "+ str(point.get_y()))
    # print(pixelList)


def click(event, x, y, flags, param):
    global point, newPoint, doOnce, tableBoundClick
    if event == cv2.EVENT_LBUTTONDOWN:
        tableBoundClick = True
        print("Pressed", x, y)
        point = (x, y)
        doOnce = True
    newPoint = (x, y)


def findBounds(frame):
    cv2.namedWindow("Frame")  # must match the imshow 1st argument
    cv2.setMouseCallback("Frame", click)
    # cv2.imshow("frame", frame)

    cv2.namedWindow("Frame")  # must match the imshow 1st argument
    cv2.setMouseCallback("Frame", click)


def getAverageHomeColor(frame):
    (b, g, r) = (0, 0, 0)
    count = 0
    for x in range(point[0] - aveLoopVal, point[0] + aveLoopVal):
        for y in range(point[1] - aveLoopVal, point[1] + aveLoopVal):
            print("looping over: " + str(x) + ", " + str(y))
            b = b + (frame[y][x])[0]
            g = g + (frame[y][x])[1]
            r = r + (frame[y][x])[2]
            count += 1
    return b / count, g / count, r / count


def getHomeColor(frame):
    global redo, testRGB
    testRGB = frame[newPoint[1]][newPoint[0]]
    if point[0] != -1 & point[1] != -1:
        global homeRGB
        global showEdits
        global doOnce
        # TODO: create home rbg center
        homeRGB = getAverageHomeColor(frame)
        homeRGB = frame[point[1], point[0]]
        showEdits = True
        redo = False
    # print(showEdits)


def getDetectionColor(frame):
    global doOnce, homeRGB, testRGB
    testRGB = frame[newPoint[1]][newPoint[0]]
    if constantlyUpdate:
        if doOnce:
            homeRGB = frame[point[1]][point[0]]
            print(frame[point[1]][point[0]])
            doOnce = False
    else:
        homeRGB = frame[point[1]][point[0]]
        # print(frame[point[1]][point[0]])


def showStringAndRectangles(frame):
    test_b = (testRGB[0])
    test_g = (testRGB[1])
    test_r = (testRGB[2])
    cv2.rectangle(frame, (point[0] - 5, point[1] + 5), (point[0] + 5, point[1] - 5), (0, 0, 255), 2)
    cv2.rectangle(frame, (newPoint[0] - 5, newPoint[1] + 5), (newPoint[0] + 5, newPoint[1] - 5), (0, 255, 0), 2)
    cv2.rectangle(frame, (0, 0), (25, 25), (int(home_b), int(home_g), int(home_r)), -1)
    cv2.rectangle(frame, (25, 0), (50, 25), (int(test_b), int(test_g), int(test_r)), -1)
    cv2.putText(frame, str(newPoint[0]) + "," + str(newPoint[1]), (newPoint[0], newPoint[1] - 50), font, .5,
                (0, 0, 255), 1,
                cv2.LINE_AA, False)
    var = str('BGR: ' + str(home_b) + ',' + str(home_g) + ',' + str(home_b))
    newVar = str('BGR: ' + str(test_b) + ',' + str(test_g) + ',' + str(test_r))
    cv2.putText(frame, var, (50, 50), font, 1, (0, 0, 255), 1,
                cv2.LINE_AA, False)
    cv2.putText(frame, newVar, (newPoint[0], newPoint[1] - 20), font, .5, (0, 0, 255), 1,
                cv2.LINE_AA, False)
    cv2.putText(frame, str("constatly update: " + str(constantlyUpdate)), (50, 100), font, 1, (0, 0, 255), 1,
                cv2.LINE_AA, False)
    cv2.putText(frame, str(currentTester), (50, 150), font, 1, (0, 0, 255), 1,
                cv2.LINE_AA, False)


def maketableBoundries():
    # if(treatMouseClockAsSet)
    pass


def displayTableBounds(frame):
    global tableBounds
    for loc in range(len(tableBounds)):
        point = tableBounds[loc]
        if loc == 0:
            color = (223, 158, 114)
        elif loc == 1:
            color = (121, 223, 114)
        elif loc == 2:
            color = (114, 114, 223)
        else:
            color = (223, 158, 114)
        cv2.circle(frame, (int(point.x), int(point.y)), 5, color, 2)


def initTableBounds():
    global addLines
    #                 (2)x
    #                    |
    #    (0)x---------(1)x--------(3)x
    # need to do manually

    if addLines:
        pointsDefined = True
        for point in tableBounds:
            if point.get_y() < 0 | point.get_x() < 0:
                pointsDefined = False
        if (pointsDefined):
            print("adding lines")
            # TODO: add to line list and define the locations of the line
            lineList.append(Line(tableBounds[0], tableBounds[1]))
            lineList.append(Line(tableBounds[1], tableBounds[3]))
            lineList.append(Line(tableBounds[1], tableBounds[2]))
        addLines = False


def displayTableLines(frame):
    for line in lineList:
        line.drawLine(frame)


def runMainLogic():
    global point, homeRGB, doOnce, showEdits, tolerance, redo, constantlyUpdate, original_x, original_y, editsToDo, currentTester, setTableBounds, addLines, bounds
    while True:
        ret, frame = cap.read()
        original_x = len(frame)
        original_y = len(frame[0])
        getDetectionColor(frame)
        # print("test rgb: "+ str(frame[0][0]))
        findBounds(frame)
        if cv2.waitKey(1) & 0xFF == ord('='):
            tolerance += 5
        if cv2.waitKey(1) & 0xFF == ord('-'):
            tolerance -= 5
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.waitKey(1) & 0xFF == ord('s'):
            showEdits = True
        if cv2.waitKey(1) & 0xFF == ord('n'):
            showEdits = False
            redo = False
        if cv2.waitKey(1) & 0xFF == ord('r'):
            if setTableBounds:
                setTableBounds = False
            else:
                setTableBounds = True
                print("switch to True")
        if cv2.waitKey(1) & 0xFF == ord('c'):
            if constantlyUpdate:
                print("constatnly update now false")
                constantlyUpdate = False
            else:
                print('constatly update now true')
                constantlyUpdate = True
        if cv2.waitKey(1) & 0xFF == ord('t'):
            editsToDo += 1
            if editsToDo == 3:
                editsToDo = 0
            elif editsToDo == 1:
                currentTester = "H tester"
            elif editsToDo == 0:
                currentTester = "HE tester"
            else:
                currentTester = "RGB tester"
        if not setTableBounds:
            if showEdits:
                bounds = getSearchBounds(frame)
                frame = cv2.resize(frame, (resizeX, resizeY), fx=.99, fy=.99)
                perfromEdits(frame, bounds)
                # performCenterCalculation(pixelList, frame)
                frame = cv2.resize(frame, (original_y, original_x), fx=.99, fy=.99)
                performCenterCalculation(pixelList, frame)
            if (not showEdits) & redo:
                # frame = cv2.resize(frame, (original_y, original_x), fx=.99, fy=.99)
                getHomeColor(frame)
            showStringAndRectangles(frame)
            initTableBounds()
        else:
            addLines = True
            lookForTableBounds(frame)
        if bounds[0] > 0:
            cv2.rectangle(frame, (int(bounds[0]), int(bounds[1])), (int(bounds[2]), int(bounds[3])), (255, 0, 255), 2,
                          1)
        displayTableLines(frame)
        displayTableBounds(frame)
        cv2.imshow('Frame', frame)


def main():
    runMainLogic()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
