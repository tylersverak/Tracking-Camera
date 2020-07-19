import RPi.GPIO as GPIO
from time import sleep
#setup- need power and ground from servo to go to board and input signal to pin 11
#red- power, brown- ground, orange- input
 
GPIO.setmode(GPIO.BOARD) #means normal numbering, other number system is one you don't know yet
GPIO.setup(11, GPIO.OUT) #this is pin 17 in the other numbering system
 
servo = GPIO.PWM(11, 50) #sets up pin 11 as output to servo and sents 50hz PWM singal
servo.start(0)

pos = 2
while (pos < 8):
  servo.ChangeDutyCycle(pos) #size max is 12, min is 2
  print("Pos is " + str(pos))
  sleep(.3)
  
  pos += 3
  pos = 2 + pos % 11

servo.stop()
GPIO.cleanup()