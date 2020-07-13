# Tracking-Camera
Using a servo motor and the raspberry pi camera, I attempted to create a program that allows the camera to move and track movement using a background subtraction algorithm.

Summary
I was inspired by Adrian Rosebrock's article on using motion detection with opencv on the raspberry pi for a conveint sercurity camera.
His program uses background frames to compare them to the camera video stream, first by detecting the difference in frames via image subtraction, then determining whether those differences were above or below a certain threshold (to avoid slight changes in lighting to affect object detection) and then drawing borders around the areas that went above the threshold. This approach requires clear background pictures to compare against and fails when the lighting changes significantly. If object(s) are detected, bounding boxes are drawn on the frame and if the average x coordinate is significantly in the far left or right of the frame, the camera will rotate to one of five predetermined angles to continue tracking that object.

Shortcomings and Possible Improvements
Ultimately I was unable to get the program to function properly. This program uses some opencv libraries that I don't believe are entirely stable and upon researching the issue, it seems like other people have gotten similar errors each with solutions they can't explain, like unplugging their mouse or running the code locally instead of through an SSH connection. 
