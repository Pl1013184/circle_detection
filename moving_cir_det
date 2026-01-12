import cir_det as cir
import cv2 as cv

vid_name = "canroll.mp4"
vid= cv.VideoCapture(vid_name)
if  False:
        print("no vid")
else:
        while True:
                cap,frame=vid.read()
                if cap:
                        frame = cir.find_circ(frame,read=False)
                        cv.imshow('vid',frame)
                        cv.waitKey(1)
                else:
                        break
