# import the necessary packages
from imutils import contours
import numpy as np
import math 
import cv2
import imutils
import os
import csv


def get_X(coor):
    coords = []
    first = coor[0][1]
    question = [coor[0][0]]
    for a in range(1, len(coor)):
        if abs(first - coor[a][1]) <= 15:
            question.append(coor[a][0])
        else:
            coords.append(question)
            first = coor[a][1]
            question = [coor[a][0]]
    coords.append(question)
    #print coords
    return coords
        
def get_Y(coor):
    coords = []
    first = coor[0][1]
    question = [coor[0][1]]
    for a in range(1, len(coor)):
        if abs(first - coor[a][1]) <= 15:
            question.append(coor[a][1])
        else:
            coords.append(question)
            first = coor[a][1]
            question = [coor[a][1]]
    coords.append(question)
    #print coords
    return coords
    

ANSWER_KEY = {1:  1, 2:  2, 3:  0, 4:  0, 5: 3, 6:  0, 7: 2, 8:  2, 9:  0, 10: 2, 11: 0,
                   12: 1, 13: 2, 14: 2, 15: 1, 16: 0, 17: 3, 18: 1, 19: 2, 20: 1, 21: 3, 22: 2,
                   23: 3, 24: 1, 25: 3, 26: 2, 27: 3, 28: 3, 29: 1, 30: 2, 31: 1, 32: 1, 33: 3,
                   34: 2, 35: 1, 36: 2, 37: 1, 38: 2, 39: 2, 40: 0, 41: 1, 42: 1, 43: 2, 44: 2,
                   45: 1}
              
path = "test/"
dirs = os.listdir( path )
wrong_papers = 0
wrong_questions = []
# This would print all the files and directories
with open('submit.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)    
    writer.writerow(("FileName","Mark"))
    for f in dirs:
        img = cv2.imread(path+f)
        #resize the image
        # convert the image to grayscale, blur it, and find edges
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        (h, w) = img.shape[:2]
        center = (w / 2, h / 2)
        
        circles = cv2.HoughCircles(img,cv2.cv.CV_HOUGH_GRADIENT,1,300,
                                    param1=50,param2=10,minRadius=40,maxRadius=50)
        #print center
        c=[]                         
        for x,y,r in circles[0]:
            if (y> 1500):
                c.append([x,y,r])
                                    
        #print circles[0][0] # first circle
        x1=c[0][0]
        x2=c[1][0]
        y1=c[0][1]
        y2=c[1][1]
        '''c = np.uint16(np.around(circles))
        for i in c[0,:]:
            # draw the outer circle
            cv2.circlef(img,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
        cv2.imwrite('detected circles.png',img)
        #cv2.waitKey(0)'''
        if x2 > x1:
            theta=math.atan2((y2-y1),(x2-x1))
        else:
            theta=math.atan2((y1-y2),(x1-x2))
            
        theta=theta*(180/math.pi)
        #print theta
        # rotate the image by theta degrees
        M = cv2.getRotationMatrix2D(center, theta, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h))
        
        circles = cv2.HoughCircles(rotated,cv2.cv.CV_HOUGH_GRADIENT,1,300,
                                    param1=50,param2=10,minRadius=40,maxRadius=50)
        #print center
        xc = 1000
        yc = 0               
        for x,y,r in circles[0]:
            if (y> 1500):
                if x < xc: 
                    #cv2.circle(rotated, (x, y), r, 0, -1)
                    xc = int(x)
                    yc = int(y)
        
        
        #cv2.imwrite("rotated.png", rotated)
        cropped=rotated[yc - 780: yc - 150, xc - 20:xc + 840]
        cropped = imutils.resize(cropped)
        #cv2.imwrite("cropped.png", cropped)
        cropped = cv2.GaussianBlur(cropped, (5, 5), 0)
        crop=cropped.copy()
        wc,hc=crop.shape[:2]
        #crop into 3 images
        crop1=cropped[0:wc,0:180]
        crop2=cropped[0:wc,320:500]
        crop3=cropped[0:wc,660:hc]
        #cv2.imwrite("cropped1.png", crop1)
        #cv2.imwrite("cropped2.png", crop2)
        #cv2.imwrite("cropped3.png", crop3)
        listcrop=[crop1,crop2,crop3]
        
        correct=0
        col = 0
        answers = []
        for r in listcrop:
            thresh = cv2.adaptiveThreshold(r, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY_INV, 11, 2)                                        
            cv2.imwrite("thresh.png", thresh)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if imutils.is_cv2() else cnts[1]
            questionCnts = []
            for c in cnts:
                (x, y, w, h) = cv2.boundingRect(c)
                ar = w / float(h)
                if w >= 19 and h >= 19 and ar >= 0.8 and ar <= 1.3:
                    questionCnts.append(c)
                    
            questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]
            coor=[]
            for n in questionCnts:
                (x, y, w, h) = cv2.boundingRect(n)
                coor.append([x,y])
            
            X= get_X(coor)  
            Y= get_Y(coor)        
            index=0
            i = 0
            while i < len(questionCnts):
                
                cnts = contours.sort_contours(questionCnts[i:i +len(Y[index])])[0]
                i += len(Y[index])
                bubbled = None
                more_than_one = False
                if len(Y[index]) != 4:
                  diff=4-len(Y[index])
                  X[index].sort()
                  if (X[index][0] < 40):
                      x = X[index][0]
                      y = Y[index][0]
                      for a in range(0,4):
                          mask = np.zeros(thresh.shape, dtype="uint8")
                          cv2.circle(mask, (x + 11, y + 11), 12, 255, -1)
                          x += 40
                          
                          mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                          total = cv2.countNonZero(mask)
                          if bubbled is not None and abs(total - bubbled[0] < 35) and total > 250 and bubbled[0] > 250:
                              more_than_one = True
                              break
                          if bubbled is None or total > bubbled[0]:
                              bubbled = (total, a)
                  elif (X[index][0] > 40) and (X[index][0] < 80):
                      x = X[index][0]-40
                      y = Y[index][0]
                      
                      for a in range(0,4):
                          mask = np.zeros(thresh.shape, dtype="uint8")
                          cv2.circle(mask, (x + 11, y + 11), 12, 255, -1)
                          x += 40
                          
                          mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                          total = cv2.countNonZero(mask)
                          if bubbled is not None and abs(total - bubbled[0] < 35) and total > 250 and bubbled[0] > 250:
                              more_than_one = True
                              break
                          if bubbled is None or total > bubbled[0]:
                              bubbled = (total, a)    
                              
                
                              
                  elif (X[index][0] > 80) and (X[index][0] < 120):
                      x = X[index][0]-80
                      y = Y[index][0]
                      
                      for a in range(0,4):
                          mask = np.zeros(thresh.shape, dtype="uint8")
                          cv2.circle(mask, (x + 11, y + 11), 12, 255, -1)
                          x += 40
                          
                          mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                          total = cv2.countNonZero(mask)
                          if bubbled is not None and abs(total - bubbled[0] < 35) and total > 250 and bubbled[0] > 250:
                              more_than_one = True
                              break
                          if bubbled is None or total > bubbled[0]:
                              bubbled = (total, a)  
                 #only the last contour is detected     
                  else :
                      x = X[index][0]-120
                      y = Y[index][0]
                      
                      for a in range(0,4):
                          mask = np.zeros(thresh.shape, dtype="uint8")
                          cv2.circle(mask, (x + 11, y + 11), 12, 255, -1)
                          x += 40
                          
                          mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                          total = cv2.countNonZero(mask)
                          if bubbled is not None and abs(total - bubbled[0] < 35) and total > 250 and bubbled[0] > 250:
                              more_than_one = True
                              break
                          if bubbled is None or total > bubbled[0]:
                              bubbled = (total, a)    
                  
                else:
                    # loop over the sorted contours
                    for (j, c) in enumerate(cnts):
                        # construct a mask that reveals only the current
                        # "bubble" for the question
                        mask = np.zeros(thresh.shape, dtype="uint8")
                        cv2.drawContours(mask, [c], -1, 255, -1)
                        mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                        total = cv2.countNonZero(mask)
                        if bubbled is not None and abs(total - bubbled[0] < 35) and total > 250 and bubbled[0] > 250:
                              more_than_one = True
                              break
                        if bubbled is None or total > bubbled[0]:
                            bubbled = (total, j)
                # initialize the contour color and the index of the
                # *correct* answer
                color = (0, 0, 255)
                k = ANSWER_KEY[index+1 + col*15]
                #answers.append([index+1 + col*15, bubbled[1]])
                if bubbled != None and k == bubbled[1] and not more_than_one:
                    color = (0, 255, 0)
                    if bubbled[0] > 195:
                        correct += 1
            
                index +=1
            col += 1
        #print f ,correct
        #print answers
        #print correct
        writer.writerow((f,correct))
'''if correct != data[f]:
        wrong_papers += 1
        wrong_questions.append([f, correct, data[f]])
print wrong_questions
print wrong_papers'''
