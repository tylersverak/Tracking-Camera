# taken from article, modified to no longer be able to work on video files given

# import the necessary packages
from imutils.video import VideoStream
import datetime
import imutils
import time
import cv2
import RPi.GPIO as GPIO

ANGLE_MIN = 2 #smallest servo angle, 0 degrees
ANGLE_MAX = 12 #largest servo angle, 180 degrees

print("[INFO] Booting up...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
firstFrames = []
min_area = 500 #minimum area to define as movement

GPIO.setmode(GPIO.BOARD) #means normal numbering, other number system is one you don't know yet
GPIO.setup(11, GPIO.OUT) #this is pin 17 in the other numbering system
 
servo = GPIO.PWM(11, 50) #sets up pin 11 as output to servo and sents 50hz PWM singal
servo.start(0)

#intialize background for all camera angles
for i in range(5):
  servo.ChangeDutyCycle(ANGLE_MIN + i * 2) 
  time.sleep(1)
  frame = vs.read()
  if frame is None:
    break
  frame = imutils.resize(frame, width=500)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (21, 21), 0)
  firstFrames.append(gray)
print("All " + str(len(firstFrames)) + " background frames have been intialized.")

#start at middle angle
pos = 0 #0 to 5
servo.ChangeDutyCycle(ANGLE_MIN + pos * 2)
time.sleep(1)

# loop over the frames of the video
while True:
  # grab the current frame and initialize the occupied/unoccupied
  # text
  frame = vs.read()
  text = "Unoccupied"
  # if the frame could not be grabbed, then we have reached the end
  # of the video
  if frame is None:
    break
  # resize the frame, convert it to grayscale, and blur it
  frame = imutils.resize(frame, width=500)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (21, 21), 0)
  tempFrame = firstFrames[pos]
  print(type(tempFrame))
  frameDelta = cv2.absdiff(tempFrame, gray)
  thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
  # dilate the thresholded image to fill in holes, then find contours
  # on thresholded image
  thresh = cv2.dilate(thresh, None, iterations=2)
  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  averagex = 0
  object_count = 0
  # loop over the contours
  for c in cnts:
    # if the contour is too small, ignore it
    if cv2.contourArea(c) < min_area:
      continue
    # compute the bounding box for the contour, draw it on the frame,
    # and update the text
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    text = "Occupied"
    averagex += (x + x + w) / 2
    object_count += 1
   # draw the text and timestamp on the frame
  if (object_count > 0):
      newx = int(averagex // object_count)
      cv2.rectangle(frame, (newx - 10, 30), (newx + 10, 130), (200, 56, 82), 2)
  cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
  cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
  # show the frame and record if the user presses a key
  cv2.imshow("Security Feed", frame)
  # cv2.imshow("Thresh", thresh) #net difference, but filtered to either black or white based on how much there is
  # cv2.imshow("Frame Delta", frameDelta) #show net difference
  key = cv2.waitKey(1) & 0xFF
  # if the `q` key is pressed, break from the lop
  if key == ord("q"):
    break
# cleanup the camera and close any open windows
#vs.release #deconstructor calls this anyway, doesnt work for some reason
cv2.destroyAllWindows()
servo.stop()
GPIO.cleanup()
print("Mishon Compree!")