from flask import Flask, Response
import cv2
import cv2 as cv
import numpy as np
import threading
import cir
import time
from threading import Thread
app = Flask(__name__)
global videio
global bholdr
bholdr=np.zeros((1440,640*3,3),dtype=np.uint8)
lock=threading.Lock()
videio = cv2.VideoCapture(-1)

videio.set(cv.CAP_PROP_FRAME_WIDTH,640)
videio.set(cv.CAP_PROP_FRAME_HEIGHT,1440)
while videio.read()[0]==False:
   pass
print(videio.get(cv.CAP_PROP_FPS))
def gen_frm():
    global raw
    global bholdr
    i=0
    while True:
        lock.acquire()
        x,raw=videio.read()
        if not x:
            lock.release()
            continue
 #       if i%50==0:
           # print(type(raw.copy()),type(raw))
        i+=1
#        print(raw)
#        print(raw.shape,raw.dtype)
        if raw is None:
            lock.release()
            continue
       # bholdr=np.zeros((720,1280,3),dtype=np.uint8)
       # print(bholdr)
        bholdr=np.append(bholdr,raw)
        bholdr=np.delete(bholdr,range(raw.size))
#        print(bholdr)
        bholdr=bholdr.reshape(1440,640*3,3)
#        print(bholdr)
#        cv.imshow('test',bholdr)
        lock.release()
#        time.sleep(5)
t=Thread(target=gen_frm,daemon=True)
raw=None

t.start()
while raw is None:
  pass

def gen_vid():
  global raw
  global bholdr
 # print(type(bholdr[1]))
  while True:
       lock.acquire()
       if bholdr is None:
            continue
       raw1=np.asarray(bholdr[:160,:480]).copy()
      # print('thinking')
 # print(type(raw1))
 #      print(type(bholdr[1]))
       raw1=cv.resize(raw1,(640,480)) 
       lock.release()
      # print('thought')
       x, img_data = cv2.imencode('.jpg', raw1)
       raw_bytes = img_data.tobytes()
       yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + raw_bytes + b'\r\n')


def gen_proc_vid():
  global raw
  while True:
      lock.acquire()
      if raw is None:
           continue
      og= bholdr[:160,:480].copy()
      raw1 = cv2.Canny(bholdr[:160,:480].copy(),100,200)
      lock.release()
     # raw1=cv.adaptiveThreshold(raw1,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)
     # lines = cv.HoughLinesP(raw1,rho=1,theta=np.pi/180,threshold=100 ,minLineLength=100,maxLineGap=12)
      lines = cv. HoughLines(raw1,1,np.pi/180,150, None,0,0)
      circles=cir.det(raw1).copy()
      
      
      raw1= cv.cvtColor(raw1, cv.COLOR_GRAY2BGR)
      imag = raw1
      frame = og
      if lines is None:
          x, img_data = cv2.imencode('.jpg', og)
          raw_bytes = img_data.tobytes()
          yield (b'--frame\r\n'
          b'Content-Type: image/jpeg\r\n\r\n' + raw_bytes +b'\r\n')
          continue  
      parallel=[]
      thresh=20
      athresh=10
      for i in lines:
           rho,theta = i[0]
           for  l in lines:
               if (l[0][0]-rho>thresh) and l[0][1]-theta<(athresh*np.pi/180):
                   parallel.append([(rho,l[0][0]),theta])
      rho=0
      rhol=0
      rhor=0
      theta=0
      if len(parallel)==0:
          x, img_data = cv2.imencode('.jpg', og)
          raw_bytes = img_data.tobytes()
          yield (b'--frame\r\n'
          b'Content-Type: image/jpeg\r\n\r\n' + raw_bytes +b'\r\n')
          continue
      for par in parallel:
          rho1,rho2 = par[0]
          rho += (rho1+rho2)/2
          theta+=par[1]
      theta*=1/len(parallel)
      rho*=1/len(parallel)
      a = np.cos(theta) 
      b = np.sin(theta)
      x0 = a*rho
      y0 = b*rho
      x1 = int(x0 + 1000*(-b))
      y1 = int(y0 + 1000*(a))
      x2 = int(x0 - 1000*(-b))
      y2 = int(y0 - 1000*(a))
      cv.line(og,(x1,y1),(x2,y2),(255,0,0),5)
#      
      for par in parallel:
          rho1,rho2=par[0]
          rhol+=max(par[0])
          rhol+=min(par[0])
      rhol*=1/len(parallel)
      rhor*=1/len(parallel)
      a = np.cos(theta)
      b = np.sin(theta)
      x0 = a*rhol
      y0 = b*rhol
      x1 = int(x0 + 1000*(-b))
      y1 = int(y0 + 1000*(a))
      x2 = int(x0 - 1000*(-b))
      y2 = int(y0 - 1000*(a))
      cv.line(og,(x1,y1),(x2,y2),(0,255,0),5)
      a = np.cos(theta)
      b = np.sin(theta)
      x0 = a*rhor
      y0 = b*rhor
      x1 = int(x0 + 1000*(-b))
      y1 = int(y0 + 1000*(a))
      x2 = int(x0 - 1000*(-b))
      y2 = int(y0 - 1000*(a))
      cv.line(og,(x1,y1),(x2,y2),(0,0,255),5)
#      break
#      raw2=cv.addWeighted(frame,0.7,imag,0.3,0)
      raw2=og 
      
      x, img_data = cv2.imencode('.jpg', raw2)
      raw_bytes = img_data.tobytes()
     # l.release()
      yield (b'--frame\r\n'
      b'Content-Type: image/jpeg\r\n\r\n' + raw_bytes + b'\r\n')

@app.route('/video')
def video():
    return  Response(gen_vid(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/proc_vid')
def proc_vid():
    return Response(gen_proc_vid(), mimetype='multipart/x-mixed-replace;boundary =frame')
    #gen_proc_vid()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
