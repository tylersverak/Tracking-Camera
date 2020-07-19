#https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/

from picamera.array import PiRGBArray
from picamera import PiCamera
import warnings
import datetime
import imutils
import time
import cv2
import RPi.GPIO as GPIO

MIN_MOTION_FRAMES = 8
CAMERA_WRAP_TIME = 2.5
DELTA_THRESH = 5
RESOLUTION = [640, 480]
FPS = 16
MIN_AREA = 5000

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = tuple(RESOLUTION)
camera.framerate = FPS
rawCapture = PiRGBArray(camera, size=(RESOLUTION[0], RESOLUTION[1]))

#intialize servo
GPIO.setmode(GPIO.BOARD) #means normal numbering, other number system is one you don't know yet
GPIO.setup(11, GPIO.OUT) #this is pin 17 in the other numbering system
pos = 2
servo = GPIO.PWM(11, 50) #sets up pin 11 as output to servo and sents 50hz PWM singal
servo.start(0)

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(2) #time for camera to warm up
avg = None
lastUploaded = datetime.datetime.now()
timer = 0

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image and initialize
    # the timestamp and occupied/unoccupied text
    frame = f.array
    timestamp = datetime.datetime.now()
    text = "Unoccupied"
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    # if the average frame is None, initialize it
    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        rawCapture.truncate(0)
        continue
    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    
    # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    thresh = cv2.threshold(frameDelta, DELTA_THRESH, 255,
        cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < MIN_AREA:
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"
    # draw the text and timestamp on the frame
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
        0.35, (0, 0, 255), 1)
    # display the security feed
    cv2.imshow("Security Feed", frame)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break
    #truncate
    rawCapture.truncate()
    rawCapture.seek(0)
    timer += 1
    
cv2.destroyAllWindows()
servo.stop()
GPIO.cleanup()
print("Mishon Compree!")
