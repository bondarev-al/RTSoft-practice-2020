import cv2
import numpy as np
from math import sqrt 
from pyzbar import pyzbar
import processing as pr #it is my file

def load_coefficients(path):
    """ Loads camera matrix and distortion coefficients. """
    # FILE_STORAGE_READ
    cv_file = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)

    # note we also have to specify the type to retrieve other wise we only get a
    # FileNode object back instead of a matrix
    camera_matrix = cv_file.getNode("K").mat()
    dist_matrix = cv_file.getNode("D").mat()

    cv_file.release()
    return [camera_matrix, dist_matrix] 

image_points = np.array([
    (16, 392), 
    (213, 84), 
    (524, 459), 
    (500, 107)
], dtype="double")

model_points = np.array([
    (0.0, 0.0, 0.0),    
    (42, 0.0, 0.0), 
    (0.0, 0.0, 28), 
    (42, 0.0, 28)
])

camera_matrix, dist_matrix = load_coefficients('camera1.yml')
ret, rotation_vector, translation_vector = cv2.solvePnP(model_points, image_points, camera_matrix, dist_matrix)

rotM = cv2.Rodrigues(rotation_vector)[0]
camMat = np.asarray(camera_matrix)
iRot = np.linalg.inv(rotM)
iCam = np.linalg.inv(camMat)

def get_coord_top(point, point_bot):
    un_point = cv2.undistortPoints(np.array(point).astype(np.float32), camera_matrix, dist_matrix, P = camera_matrix)
    un_point = un_point.ravel().tolist()
    uvPoint = np.matrix([un_point[0], un_point[1], 1]).T
    tempMat = np.matmul(np.matmul(iRot, iCam), uvPoint)
    tempMat2 = np.matmul(iRot, translation_vector)
    s = (point_bot[0] + tempMat2[0, 0]) / tempMat[0, 0]
    wcPoint = np.matmul(iRot, (np.matmul(s * iCam, uvPoint) - translation_vector))
    wcPoint[0] = point_bot[0]
    wcPoint[2] = point_bot[2]
    point3d = wcPoint.T.tolist()[0]
    return point3d

def get_coord(point, level = 0):
    un_point = cv2.undistortPoints(np.array(point).astype(np.float32), camera_matrix, dist_matrix, P = camera_matrix)
    un_point = un_point.ravel().tolist()
    uvPoint = np.matrix([un_point[0], un_point[1], 1]).T
    tempMat = np.matmul(np.matmul(iRot, iCam), uvPoint)
    tempMat2 = np.matmul(iRot, translation_vector)
    s = (level + tempMat2[1, 0]) / tempMat[1, 0]
    wcPoint = np.matmul(iRot, (np.matmul(s * iCam, uvPoint) - translation_vector))
    wcPoint[1] = level
    point3d = wcPoint.T.tolist()[0]
    return point3d

def sort_cornel(cornels):
    if len(cornels) < 4:
        return
    top = [[], [], [], []]
    bot = [[], [], [], []]
    bound_point = [650, 0]
    near_bound_point = [650, 0]
    for point in cornels:
        if point[0] < bound_point[0]:
            near_bound_point = bound_point
            bound_point = point
        elif point[0] < near_bound_point[0]:
            near_bound_point = point
    if bound_point[1] > near_bound_point[1]:
        bot[0] = bound_point        
        top[0] = near_bound_point
    else:
        bot[0] = near_bound_point     
        top[0] = bound_point    
    cornels.remove(bound_point)
    cornels.remove(near_bound_point)

    bound_point = cornels[0]
    for point in cornels:
        if point[1] > bound_point[1]:
            bound_point = point
    bot[1] = bound_point
    cornels.remove(bound_point)

    if len(cornels) == 1:
        top[1] = cornels[0]
        top_and_bot = {"top": top, "bot": bot}
        return top_and_bot

    bound_point = [0, 0]
    near_bound_point = [0, 0]
    for point in cornels:
        if point[0] > bound_point[0]:
            near_bound_point = bound_point
            bound_point = point
        elif point[0] > near_bound_point[0]:
            near_bound_point = point
    if len(cornels) == 4:
        if bound_point[1] > near_bound_point[1]:
            bot[2] = bound_point        
            top[2] = near_bound_point
        else:
            bot[2] = near_bound_point     
            top[2] = bound_point  
        cornels.remove(bound_point)
        cornels.remove(near_bound_point) 
        if cornels[0][1] > cornels[1][1]:
            top[1] = cornels[0]
            top[3] = cornels[1]
        else:
            top[1] = cornels[1]
            top[3] = cornels[0]
        top_and_bot = {"top": top, "bot": bot}
        return top_and_bot
    if len(cornels) == 3:
        cornels.remove(bound_point)
        cornels.remove(near_bound_point) 
        if (near_bound_point[0] - bot[1][0]) > bot[1][0] * 0.05:
            if bound_point[1] > near_bound_point[1]:
                bot[2] = bound_point
                top[2] = near_bound_point
            else:
                bot[2] = near_bound_point
                top[2] = bound_point
            top[1] = cornels[0]
        else:
            if bound_point[1] > near_bound_point[1]:
                top[1] = bound_point
                top[2] = near_bound_point
            else:
                top[1] = near_bound_point
                top[2] = bound_point
            top[3] = cornels[0]
        top_and_bot = {"top": top, "bot": bot}
        return top_and_bot

def dist_betw_points_bot(point1, point2):
    coord1 = get_coord(point1)
    coord2 = get_coord(point2)
    return sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[2] - coord2[2]) ** 2)

def dist_betw_points_bot_top(point_bot, point_top):
    coord1 = get_coord(point_bot)
    coord2 = get_coord_top(point_top, coord1)
    return coord2[1] - coord1[1]

# cap = cv2.VideoCapture(0)
# ret, frame = cap.read()

def check_QR_code(im_src, points_of_edge):
    # im_src = cv2.imread("./QR-codes/photos/image11.png")
    # cv2.imshow('Sizing',im_src)
    
    pts_src = np.array(points_of_edge)
    scale = dist_betw_points_bot(points_of_edge[0], points_of_edge[1]) / dist_betw_points_bot_top(points_of_edge[0], points_of_edge[3])

    h = 400
    w = int(h * scale)
    im_dst = np.ones((h, w,1),np.uint8)*255
    pts_dst = np.array([ [0, h],[w, h],[w, 0],[0, 0] ])
    h, status = cv2.findHomography(pts_src, pts_dst)
    im_out = cv2.warpPerspective(im_src, h, (im_dst.shape[1],im_dst.shape[0]))

    # cv2.imshow('before', im_out)

    b, g, r = cv2.split(im_out)
    equ = cv2.equalizeHist(b)
    # cv2.imshow('after_eq1', equ)

    for i in range(100, 255, 1):
        test = im_out.copy()
        test[test > i] = 255
        test[test < 130] = 1
        b, g, r = cv2.split(test)
        equ_t = cv2.equalizeHist(b)
        barcodes = pyzbar.decode(equ_t)
        if barcodes != []:
            barcodeData = barcodes[0].data.decode("utf-8")
            return "QR code detected. Data: {}".format(barcodeData)
    return "QR code not detected"

def anal_box(Image, cornels):
    top_and_bot = sort_cornel(cornels)
    coord_top = [[], [], [], []]
    coord_bot = [[], [], [], []]
    coord_bot[0] = get_coord(top_and_bot["bot"][0])
    coord_top[0] = get_coord_top(top_and_bot["top"][0], coord_bot[0])
    coord_bot[1] = get_coord(top_and_bot["bot"][1])
    h = coord_top[0][1] - coord_bot[1][0]
    w = 

    print(coord_bot)
    print(coord_top)
    # points_of_edge = [top_and_bot["bot"][0], top_and_bot["bot"][1], top_and_bot["top"][1], top_and_bot["top"][0]]
    # print(check_QR_code(Image, points_of_edge))

    return top_and_bot

if __name__ == "__main__":
    im_src = cv2.imread("./QR-codes/photos/image3.png")
    cv2.imshow('Sizing',im_src)
    # points_of_edge = [ [243, 335], [313, 331], [320, 237], [247, 235] ] # for old image
    # points_of_edge = [ [210, 363], [286, 363], [290, 269], [208, 262] ] #image0 small
    # points_of_edge = [ [174, 264], [233, 252], [234, 161], [172, 165] ] #image1 small
    # points_of_edge = [ [269, 144], [318, 153], [322, 71], [272, 62]   ] #image2 small
    points_of_edge = [ [401, 224], [458, 227], [472, 142], [412, 130] ] #image3 small
    # points_of_edge = [ [421, 255], [424, 200], [315, 201], [314, 257] ] #image4 small
    # points_of_edge = [ [377, 195], [475, 199], [481, 146], [387, 146]  ] #image5 small
    # points_of_edge = [ [349, 313], [412, 296], [350, 229], [295, 245] ] #image6 small
    # points_of_edge = [ [258, 345], [317, 317], [247, 249], [188, 273] ] #image7 small
    # points_of_edge = [ [213, 189], [273, 189], [275, 134], [221, 138] ] #image8 small
    # points_of_edge = [ [117, 452], [353, 462], [367, 44], [128, 44] ] #test small
    # points_of_edge = [ [500, 503], [618, 519], [627, 347], [499, 329] ] #image0 bigQ
    # points_of_edge = [ [448, 251], [546, 256], [548, 106], [447, 99] ] #image1 bigQ
    # points_of_edge = [ [799, 306], [893, 303], [926, 156], [825, 153] ] #image2 bigQ
    # points_of_edge = [ [588, 353], [679, 385], [692, 234], [598, 193] ] #image3 bigQ
    # points_of_edge = [ [663, 501], [780, 498], [808, 331], [682, 329] ] #image4 bigQ
    # points_of_edge = [ [427, 266], [527, 285], [592, 195], [504, 179] ] #image5 bigQ  # don't work
    # points_of_edge = [ [563, 405], [631, 469], [805, 394], [732, 339] ] #image6 bigQ    # don't work
    # points_of_edge = [ [532, 141], [607, 166], [699, 104], [628, 85] ] #image7 bigQ  # don't work
    # points_of_edge = [ [622, 355], [621, 438], [813, 427], [823, 342]  ] #image8 bigQ # don't work
    # points_of_edge = [ [372, 429] , [382, 518], [594, 506], [594, 424] ] #image9 bigQ # don't work
    # points_of_edge = [ [372, 429] , [382, 518], [594, 506], [594, 424] ] #image10 bigQ  # =9
    # points_of_edge = [ [525, 271] , [694, 286], [698, 209], [526, 197] ] #image11 bigQ
    # points_of_edge = [ [525, 271] , [694, 286], [698, 209], [526, 197] ] #image11 bigQ
    
    # print(check_QR_code(im_src, points_of_edge))

    # cornels = [ [174, 264], [163, 219], [222, 128], [162, 139], [233, 252], [234, 161], [172, 165] ] # image1 small
    # cornels = [ [174, 264], [163, 219], [162, 139], [233, 252], [234, 161], [172, 165] ] # image1_test small
    cornels = [ [401, 224], [458, 227], [416, 108], [473, 112], [472, 142], [412, 130] ] #image3 small
    # cornels = [ [472, 142], [412, 130],  [458, 227], [401, 224] ] #image3_alm test small
    print(anal_box(im_src, cornels))

    # cv2.imshow('after', im_out)
    # cv2.imshow('after_eq2', equ)

    while (True):
        # ret, frame = cap.read()
        # cv2.imshow('Sizing',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
