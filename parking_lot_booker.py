from datetime import datetime
import sqlite3
import cv2
import cv2
import numpy as np
import pickle
import matplotlib.path as mplPath

class Parking:
    conn = None
    cursor = None
    def __init__(self, db_path):
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(db_path)
                self.cursor = self.conn.cursor()
            except:
                self.conn = None
                self.cursor = None
        
        self.width = 60
        self.height = 80
        
        try:
            with open('parking_list.dat','rb') as f:
                self.posList=pickle.load(f)
        except:
            self.posList = []

    def __del__(self):
        if self.conn is not None:
            self.cursor.close()
            self.conn.close()
            self.conn = None
            self.cursor = None
            
    def mouse_click(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            #print(x,y)
            self.posList.append([(x,y),(x+self.width,y),(x+(2*self.width),y+self.height),((x+self.width),y+self.height)])
        if event == cv2.EVENT_RBUTTONDOWN:
            #print(x,y)
            for i,pos in enumerate(self.posList): 
                path = mplPath.Path(pos)
                inside = path.contains_point((x,y))
                if inside:
                    self.posList.pop(i)
                    break   
                
        with open('parking_list.dat','wb') as f:
            pickle.dump(self.posList,f)


    def make_db(self):
        #print("Database created and Successfully Connected to SQLite")
        create = "CREATE TABLE IF NOT EXISTS Parking (spot INTEGER NOT NULL PRIMARY KEY, booked TIMESTAMP);"
        select = "SELECT * FROM Parking;"
        self.cursor.execute(create)
        self.cursor.execute(select)
        record = self.cursor.fetchall()
        #print("Database includes: ", record)

    #Useful for testing
    def update_parking(self,i):
        #print(f"Updating index {i} with new date")
        insert = "INSERT OR REPLACE INTO Parking(spot,booked) VALUES(?,?)"
        data_tuple = (i, datetime.now())
        #print(data_tuple)
        self.cursor.execute(insert,data_tuple)
        self.conn.commit()
        select="SELECT booked FROM Parking WHERE spot == ?;"
        self.cursor.execute(select,(i,))
        record = self.cursor.fetchone()
        #print("Database now includes: ", record[0] )
        

    #Checks if last time is within 30 mins
    def check_parking_time(self,i):
        #print(f"Check index {i} within 30 minutes of now")
        select = "SELECT booked FROM Parking WHERE spot == ?;"
        self.cursor.execute(select,(i,))
        record = self.cursor.fetchone()
        if record:
            #print("Database includes: ", record[0])
            d1 = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S.%f")
            d2 = datetime.now()

            # difference between dates in timedelta
            delta = (d2 - d1).total_seconds() / 60.0
            return delta >= 30
        return False

    def check_parking_space(self,imgDilate,img):
        parked = 0
        n = len(self.posList)
        
        for i,pos in enumerate(self.posList):
            x,y = pos[0]
            lines = np.array([pos], np.int32)
            mask = np.zeros(imgDilate.shape[:2], np.uint8)
            cv2.fillPoly(mask,[lines],color=(255, 255, 255))
            masked = cv2.bitwise_and(imgDilate, mask)
            #cv2.imshow(str(x*y),masked)
            #imgCrop = masked[y:y+self.height,x:x+(2*self.width)]
            imgCrop = cv2.polylines(masked,[lines],True,color=(255, 255, 255))
            #cv2.imshow(str(x*y),imgCrop)
            count = cv2.countNonZero(imgCrop)
            area = cv2.contourArea(lines)
            #print(area)
            #print(count)
            if count < area/6:
                color = (0,255,0)
                thickness = 5
            else:
                if self.check_parking_time(i):
                    color = (255, 85, 0)
                    thickness = 2
                else:
                    color = (0,0,255)
                    thickness = 2
                parked += 1
            #self.update_parking(i)
            
            img_poly = cv2.polylines(img,[lines],True,color,thickness)
            cv2.putText(img_poly,str(count),(x,y+5),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale = 1,color=(255,0,255),lineType = cv2.LINE_4)
        cv2.putText(img,f"{parked}/{n}",(50,50),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale = 1,color=(255,0,255),lineType = cv2.LINE_4)


def main():
    print('Started')
    database = 'parking_lot_booker.db'
    parking = Parking(database)
    parking.make_db()
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    if parking:
        cap = cv2.VideoCapture('parking_lot.mp4')
            
        while True:
            if cap.get(cv2.CAP_PROP_POS_FRAMES)==cap.get(cv2.CAP_PROP_FRAME_COUNT):
                cap.set(cv2.CAP_PROP_POS_FRAMES,0)
            success,img = cap.read()
            imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            imgBlur = cv2.GaussianBlur(imgGray,(3,3),1)
            imgThreshhold = cv2.adaptiveThreshold(imgBlur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,25,16)
            imgMedian = cv2.medianBlur(imgThreshhold,5)
            kernel = np.ones((3,3),np.uint8)
            imgDilate = cv2.dilate(imgMedian,kernel,iterations=1)
            parking.check_parking_space(imgDilate,img)
            cv2.imshow('Image',img)
            #cv2.imshow('ImageBlur',imgBlur)
            #cv2.imshow('ImageThresh',imgThreshhold)
            #cv2.imshow('ImageMedian',imgMedian)
            #cv2.imshow('ImageDilate',imgDilate)
            cv2.setMouseCallback('Image',parking.mouse_click)
            cv2.waitKey(10)
    parking.__del__()

if __name__ == '__main__':
    main()
   