# Tyler Sverak 2020
# This program uses a camera mounted on a servo motor with a background subtraction
# algorithm to move the camera to watch moving detected objects
# using some code from https://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/

# import the necessary packages
from imutils.video import VideoStream
import datetime
import imutils
import time
import cv2
import RPi.GPIO as GPIO
import picamera
from picamera.array import PiRGBArray

ANGLE_MIN = 2 # smallest servo angle, 0 degrees
ANGLE_MAX = 12 # largest servo angle, 180 degrees
MIN_AREA = 500 # minimum area to define as movement
SERVO_ANGLES = [2, 4, 6, 8, 10] # use these specific angles for testing
RESOLUTION = (640, 480) # camera resolution
FORMATTED_WIDTH = 500

def getBackground(frame, angle, servo, rawCapture):
  servo.ChangeDutyCycle(SERVO_ANGLES[angle]) #size max is 12, min is 2
  time.sleep(.5)
  frame = imutils.resize(frame, width=500)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (21, 21), 0)
  avg = gray.copy().astype("float")
  rawCapture.truncate(0)
  return avg

def cleanup(servo, camera):
  # cleanup the camera and close any open windows
  time.sleep(5)
  cv2.destroyAllWindows()
  servo.stop()
  GPIO.cleanup()
  #camera.stop_recording()
  print("Closing...")

def format_frame(frame):
  # takes a frame and reformats it so we can more easy
  # detect objects in it
  frame = imutils.resize(frame, width=500)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (21, 21), 0)
  return gray
  
def difference_thresh(frame, background_frame):
  # compares two frames and returns a frame with their
  # differences highlighted, assumes both frames have been formatted
    cv2.accumulateWeighted(frame, background_frame, 0.5)
    frameDelta = cv2.absdiff(frame, cv2.convertScaleAbs(background_frame))
    thresh = cv2.threshold(frameDelta, 5, 255,
        cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    return thresh
    
def find_conteurs(thresh):
  # given the difference threshold, finds all the contours
  # and returns their bounding boxes
  print("Finding conteurs...")
  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
  cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
  rects = []
  for c in cnts:
    # if the contour is too small, ignore it
    if cv2.contourArea(c) < MIN_AREA:
      continue
    rects.append(cv2.boundingRect(c))
  return rects

def update_pos(rects):
  # given where the contours are, returns the direction
  # the camera must turn to look where the majority of objects are
  print("Updating camera position...")
  if not rects:
    return 0
  averagex = 0
  object_count = 0
  # loop over the contours
  for r in rects:
    (x, y, w, h) = r
    averagex += (x + x + w) / 2
    object_count += 1
  newx = int(averagex // object_count)
  if (newx > FORMATTED_WIDTH * 3 // 4):
    return 1
  elif (newx < FORMATTED_WIDTH // 4):
    return -1
  return 0
    
def clamp(num, small, big):
  # takes a number num and two numbers representing the upper and lower
  # bound and returns num such that it falls between the bounds
  if (num < small):
    return small
  elif (num > big):
    return big
  return num

def main():
  # setup
  print("[INFO] Booting up...")
  camera = picamera.PiCamera()
  camera.resolution = RESOLUTION
  camera.framerate = 16
  print("[INFO] warming up...")
  time.sleep(2.5)
  motionCounter = 0
  GPIO.setmode(GPIO.BOARD) #means normal numbering, other number system is one you don't know yet
  GPIO.setup(11, GPIO.OUT) #this is pin 17 in the other numbering system
  servo = GPIO.PWM(11, 50) #sets up pin 11 as output to servo and sents 50hz PWM singal
  servo.start(0)
  
  #try to get background
  background = []
  pos = 0
  #servo.ChangeDutyCycle(2) #size max is 12, min is 2
  print("Beginning loop...")
  
  with picamera.array.PiRGBArray(camera) as output:
      camera.capture(output, 'rgb')
      picture = output.array
      formatted = format_frame(picture)
      cv2.imshow("here", formatted)
  
  cleanup(servo, camera)
  return
  
if __name__ == "__main__":
  main()