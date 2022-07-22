import sqlite3
from sqlite3 import Error
import cv2
import cv2
import numpy as np
import pickle

width=60
height=80

try:
    with open('parking_list','rb') as f:
        posList=pickle.load(f)
except:
    posList=[]
def mouse_click(event,x,y,flags,param):
    if event ==cv2.EVENT_LBUTTONDOWN:
        print(x,y)
        posList.append((x,y))
    if event ==cv2.EVENT_RBUTTONDOWN:
        print(x,y)
        for i,pos in enumerate(posList):    
            x1,y1=pos
            print(x1<x<x1+width)
            # Rework for parallelogram
            if x1 < x < x1+width:
                posList.pop(i)
                break
    with open('parking_list','wb') as f:
        pickle.dump(posList,f)
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def check_parking_space(imgDilate,img):
    for pos in posList:
        x,y=pos
        # Figure parallel crop
        imgCrop=imgDilate[y:y+height,x:x+(2*width)]
        #cv2.imshow(str(x*y),imgCrop)
        count=cv2.countNonZero(imgCrop)
        print(count)
        if count<900:
            color=(0,255,0)
            thickness=5
        else:
            color=(0,0,255)
            thickness=2
        lines = np.array([pos,[x+width,y],[x+(2*width),y+height],[x+width,y+height]], np.int32)
        img_poly=cv2.polylines(img,[lines],True,color,thickness)
        cv2.putText(img_poly,str(count),(x,y+5),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale = 1,color=(0,255,25),lineType = cv2.LINE_4)


def main():
    database = 'parking_lot_booker.db'

    # create a database connection
    conn = create_connection(database)
    with conn:
        print('Started')
        # Create a VideoCapture object and read from input file
        # If the input is the camera, pass 0 instead of the video file name
        cap = cv2.VideoCapture('parking_lot.mp4')
        
        while True:
            if cap.get(cv2.CAP_PROP_POS_FRAMES)==cap.get(cv2.CAP_PROP_FRAME_COUNT):
                cap.set(cv2.CAP_PROP_POS_FRAMES,0)
            success,img = cap.read()
            #img = cv2.resize(img,(1282,752), interpolation = cv2.INTER_AREA)
            imgGray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            imgBlur= cv2.GaussianBlur(imgGray,(3,3),1)
            imgThreshhold=cv2.adaptiveThreshold(imgBlur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,25,16)
            imgMedian=cv2.medianBlur(imgThreshhold,5)
            kernel=np.ones((3,3),np.uint8)
            imgDilate=cv2.dilate(imgMedian,kernel,iterations=1)
            check_parking_space(imgDilate,img)
            #for pos in posList:
                #x,y=pos
                #lines = np.array([pos,[x+width,y],[x+(2*width),y+height],[x+width,y+height]], np.int32)
                #img_poly=cv2.polylines(img,[lines],True,(0,0,255),2)
                
            cv2.imshow('Image',img)
            #cv2.imshow('ImageBlur',imgBlur)
            #cv2.imshow('ImageThresh',imgThreshhold)
            #cv2.imshow('ImageMedian',imgMedian)
            #cv2.imshow('ImageDilate',imgDilate)
            cv2.setMouseCallback('Image',mouse_click)
            cv2.waitKey(10)

if __name__ == '__main__':
    main()
   