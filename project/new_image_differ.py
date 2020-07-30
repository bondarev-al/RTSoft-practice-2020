

import numpy as np

import cv2

def corner_find(image):

    points = []

    font = cv2.FONT_HERSHEY_COMPLEX
    img2 = image

    h, w, c = image.shape
    hmi = h-1
    wmi = w-1
    #print (w)
    #print (h)
    img = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    # cv2.imshow('img', img)

  
    _, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY)

    #cv2.imshow('threshold', threshold)
    contours, _= cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    for cnt in contours :

        approx = cv2.approxPolyDP(cnt, 0.009 * cv2.arcLength(cnt, True), True)


        #cv2.drawContours(img2, [approx], 0, (0, 0, 255), 5) 


        n = approx.ravel() 
        i = 0

        for j in n :
            if(i % 2 == 0):
                x = n[i]
                y = n[i + 1]

            
                if x!=0 and y!=0 and x!=w and y!=h and x!=h and x!=w and x!=wmi and y!=hmi and x!=hmi and x!=wmi:
                    string = str(x) + " " + str(y)
                    #cv2.putText(img2, string, (x, y), font, 0.5, (0, 255, 0)) 
                    points.append([x, y])

            i = i + 1

            #for k in range(0, len(points)):
            #    print (points[k])
    #print (points[0])
    #print (len(points))
    if len(points) == 6:
        x1, y1 = points[0]
        x2, y2 = points[1]
        x3, y3 = points[2]
        x4, y4 = points[3]
        x5, y5 = points[4]
        x6, y6 = points[5]
        dx = x4-x5
        x7 = x3-dx
        dy = y4-y5
        y7 = y3-dy
        points.append([x7, y7])
        dx1=x1-x2
        dy1=y1-y2
        x8=x6-dx1
        y8=y6-dy1
        points.append([x8, y8])

    for p in points:
        cv2.circle(img2, tuple(p), 10, (255,0,0), -1)


    ######################################cv2.imshow('image2', img2) 
    #cv2.waitKey(0)

    return points


def histogram_color_dominator(image, k=2):
    img = image
    Z = img.reshape((-1,3))

    # convert to np.float32
    Z = np.float32(Z)

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = k # how many domination color we find (2 is ok)
    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))

    ###############################################cv2.imshow('res2',res2)
    #cv2.waitKey(0)

    return res2
"""
#img = cv2.imread("./images/rect.jpg")

#histogram_color_dominator(img, 0)
#histogram_color_dominator(img, 1)
#h = histogram_color_dominator(img, 2)
#cv2.imshow('h', h)
#cv2.waitKey(0)
#histogram_color_dominator(img, 4)
#histogram_color_dominator(img, 8)
"""







"""
img = cv2.imread("./images/fig.jpg")
not_func_points = corner_find(img)
print ("Not_func_points:\n {0}".format(not_func_points))

for p in not_func_points:
    cv2.putText(img, str(p), tuple(p), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0))
    cv2.circle(img, tuple(p), 10, (255,0,0), -1)

cv2.imshow('image', img)
cv2.waitKey(0)


#if cv2.waitKey(0) & 0xFF == ord('q'): 

#    cv2.destroyAllWindows()
"""