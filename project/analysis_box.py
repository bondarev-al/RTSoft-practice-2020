import cv2
import numpy as np
from math import sqrt, acos, pi 
from pyzbar import pyzbar
import json
import paho.mqtt.client as mqtt
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

#Slava
# image_points = np.array([
#     (133, 186), 
#     (541, 191), 
#     (4, 287), 
#     (635, 299)
# ], dtype="double")

model_points = np.array([
    (0.0, 0.0, 0.0),    
    (42, 0.0, 0.0), 
    (0.0, 0.0, 28), 
    (42, 0.0, 28)
])

# camera_matrix, dist_matrix = load_coefficients('camera1.yml')
camera_matrix, dist_matrix = load_coefficients('./images/calibration.yml')
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
    
    # print(points_of_edge)

    h = 400
    w = int(h * scale)
    im_dst = np.ones((h, w, 1),np.uint8)*255
    pts_dst = np.array([ [0, h],[w, h],[w, 0],[0, 0] ])
    h, status = cv2.findHomography(pts_src, pts_dst)
    im_out = cv2.warpPerspective(im_src, h, (im_dst.shape[1],im_dst.shape[0]))

    # cv2.imshow('before', im_out)

    b, g, r = cv2.split(im_out)
    equ = cv2.equalizeHist(b)
    # cv2.imshow('after_eq1', equ)

    for i in range(100, 255, 3):
        test = im_out.copy()
        test[test > i] = 255
        test[test < 130] = 1
        b, g, r = cv2.split(test)
        equ_t = cv2.equalizeHist(b)
        barcodes = pyzbar.decode(equ_t)
        if barcodes != []:
            barcodeData = barcodes[0].data.decode("utf-8")
            return True, barcodeData
            # barcodeData = barcodes[0].data.decode("utf-8")
            # return "QR code detected. Data: {}".format(barcodeData)
    # return "QR code not detected"
    return False, ""

client = mqtt.Client()
client.connect("localhost", 1883)
scale_v = 10
truck_h = 0.5
truck_obj = [{"id": "trucks_1", "position":  [42.0 / scale_v / 2, 0.25,  - 28.0 / scale_v / 2], "euler": [0, 0,  0],  "shape":[42.0 / scale_v, truck_h,  28.0 / scale_v], "color": [66, 255, 249]}] 
data = {}
boxes = []
data["boxes"] = boxes
data["trucks"] = truck_obj
data_out_boxes = json.dumps(data)
client.publish("scene", data_out_boxes, qos=0, retain=False)

def show_box(cent, angle, shape):
    boxes = [{"id": "box_1", "position":  cent, "euler": [0, angle,  0],  "shape": shape, "color": [66, 0, 249]}]
    data["boxes"] = boxes
    data["trucks"] = truck_obj
    data_out_boxes = json.dumps(data)
    client.publish("scene", data_out_boxes, qos=0, retain=False)

def show_boxes(boxes):
    temp_boxes = []
    i = 3
    for box in boxes:
        box_obj = {}
        box_obj["id"] = "box_" + str(i)
        box_obj["position"] = box[0]
        box_obj["euler"] = [0, box[1],  0]
        box_obj["shape"] = box[2]
        box_obj["color"] = [255, 0, 0]
        temp_boxes.append(box_obj) 
        i += 1
    # print(temp_boxes)
    data["boxes"] = temp_boxes
    data["trucks"] = truck_obj
    data_out_boxes = json.dumps(data)
    # print("output: ", data_out_boxes)
    client.publish("scene", data_out_boxes, qos=0, retain=False)

def do_analysis_box(Image, cornels):
    temp_cornels = list(cornels)
    top_and_bot = sort_cornel(temp_cornels)
    coord_top = [[], [], [], []]
    coord_bot = [[], [], [], []]
    coord_bot[0] = get_coord(top_and_bot["bot"][0])
    coord_top[0] = get_coord_top(top_and_bot["top"][0], coord_bot[0])
    coord_bot[1] = get_coord(top_and_bot["bot"][1])
    h = coord_top[0][1] - coord_bot[1][1]
    w = sqrt((coord_bot[0][0] - coord_bot[1][0]) ** 2 + (coord_bot[0][2] - coord_bot[1][2]) ** 2)
    temp_cent = [0, 0, 0]
    temp_cent[0] = (coord_bot[0][0] + coord_bot[1][0]) / 2
    temp_cent[1] = coord_top[0][1] / 2
    temp_cent[2] = (coord_bot[0][2] + coord_bot[1][2]) / 2
    offset_cent = [0, 0, 0]
    if top_and_bot["bot"][2] != []:
        coord_bot[2] = get_coord(top_and_bot["bot"][2])
        d = sqrt((coord_bot[1][0] - coord_bot[2][0]) ** 2 + (coord_bot[1][2] - coord_bot[2][2]) ** 2)
        offset_cent[0] = (coord_bot[2][0] - coord_bot[1][0]) / 2
        offset_cent[2] = (coord_bot[2][2] - coord_bot[1][2]) / 2
    elif top_and_bot["top"][3] != []:
        coord_top[3] =  get_coord(top_and_bot["top"][3], coord_top[0][1])
        d = sqrt((coord_top[0][0] - coord_top[3][0]) ** 2 + (coord_top[0][2] - coord_top[3][2]) ** 2)
        offset_cent[0] = (coord_top[3][0] - coord_top[0][0]) / 2
        offset_cent[2] = (coord_top[3][2] - coord_top[0][2]) / 2
    else:
        d = w
        offset_cent[0] = d / 2
    temp_cent[0] += offset_cent[0]
    temp_cent[2] += offset_cent[2]
    cent = temp_cent
    temp_cent = [cent[0], 0, cent[2]]
    temp_v = [- d / 2, 0, - w / 2]
    temp_v1 = [coord_bot[0][0] - temp_cent[0], 0, coord_bot[0][2] - temp_cent[2]]
    prod_v = temp_v[0] * temp_v1[0] + temp_v[2] * temp_v1[2]
    mod_v = sqrt(temp_v[0] ** 2 + temp_v[2] ** 2)
    mod_v1 = sqrt(temp_v1[0] ** 2 + temp_v1[2] ** 2)
    angle = acos(prod_v / mod_v / mod_v1) * 180 / pi
    shape = [d / scale_v, h / scale_v, w /scale_v]
    cent[0] /= scale_v
    cent[1] = cent[1] / scale_v + truck_h
    cent[2] /= - scale_v
    # show_box(cent, angle, shape)
    # print([cent, angle, shape])
    # return [cent, angle, shape]
    
    find_QR = False
    points_of_edge = [top_and_bot["bot"][0], top_and_bot["bot"][1], top_and_bot["top"][1], top_and_bot["top"][0]]
    find_QR, data = check_QR_code(Image, points_of_edge)
    qr_res = "QR Data: "
    if find_QR:
        qr_res = str(data)
    else:
        if top_and_bot["bot"][2] != []:
            points_of_edge = [top_and_bot["bot"][1], top_and_bot["bot"][2], top_and_bot["top"][2], top_and_bot["top"][1]]
            find_QR, data = check_QR_code(Image, points_of_edge)
            if find_QR:
                qr_res += str(data)
            elif top_and_bot["top"][3] != []:
                points_of_edge = [top_and_bot["top"][0], top_and_bot["top"][1], top_and_bot["top"][2], top_and_bot["top"][3]]
                find_QR, data = check_QR_code(Image, points_of_edge)
                if find_QR:
                    qr_res = str(data)
        elif top_and_bot["top"][3] != []:
            points_of_edge = [top_and_bot["top"][0], top_and_bot["top"][1], top_and_bot["top"][2], top_and_bot["top"][3]]
            find_QR, data = check_QR_code(Image, points_of_edge)
            if find_QR:
                qr_res = str(data)
    text = 'Size(mm): {} x {} x {}'.format(int(w * 10), int(d * 10), int(h *10))

    if top_and_bot["top"][2] != []:
        org = (top_and_bot["top"][2][0] + 5, top_and_bot["top"][2][1])
        org_qr = (top_and_bot["top"][2][0] + 5, top_and_bot["top"][2][1] + 20)
        org_l = (top_and_bot["top"][2][0] + 5, top_and_bot["top"][2][1] + 25)
    else:
        org = (top_and_bot["top"][1][0] + 5, top_and_bot["top"][1][1])
        org_qr = (top_and_bot["top"][1][0] + 5, top_and_bot["top"][1][1] + 20)
        org_l = (top_and_bot["top"][1][0] + 5, top_and_bot["top"][1][1] + 25)

    color = (0, 0, 0)
    # cv2.rectangle(Image, org_l, (org_l[0] + 190, org_l[1] - 40), (0, 255, 0), -1)
    output = Image.copy()
    cv2.rectangle(Image, org_l, (org_l[0] + 190, org_l[1] - 40), (0, 255, 0), -1)
    cv2.addWeighted(Image, 0.5, output, 1 - .5, 0, output)

    cv2.putText(output, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.45, color)
    cv2.putText(output, qr_res, org_qr, cv2.FONT_HERSHEY_SIMPLEX, 0.45, color)
    for cornel in cornels:
        cv2.circle(output, (cornel[0], cornel[1]), 5, (0,0,255), -1)
    cv2.imshow('Sizing',output)    
    return output, [cent, angle, shape]

    # points_of_edge = [top_and_bot["bot"][0], top_and_bot["bot"][1], top_and_bot["top"][1], top_and_bot["top"][0]]
    # print(check_QR_code(Image, points_of_edge))


if __name__ == "__main__":
    im_src = cv2.imread("./QR-codes/photos/image0.png")
    cv2.imshow('Sizing',im_src)
    # points_of_edge = [ [243, 335], [313, 331], [320, 237], [247, 235] ] # for old image
    # points_of_edge = [ [210, 363], [286, 363], [290, 269], [208, 262] ] #image0 small
    # points_of_edge = [ [174, 264], [233, 252], [234, 161], [172, 165] ] #image1 small
    # points_of_edge = [ [269, 144], [318, 153], [322, 71], [272, 62]   ] #image2 small
    # points_of_edge = [ [401, 224], [458, 227], [472, 142], [412, 130] ] #image3 small
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

    # cornels = [ [210, 363], [286, 363], [296, 221], [290, 269], [208, 262], [227, 218]] # image0 small
    # cornels = [ [174, 264], [163, 219], [222, 128], [162, 139], [233, 252], [234, 161], [172, 165] ] # image1 small
    # cornels = [ [174, 264], [163, 219], [162, 139], [233, 252], [234, 161], [172, 165] ] # image1_test small
    # cornels = [ [401, 224], [458, 227], [416, 108], [473, 112], [472, 142], [412, 130] ] #image3 small
    # cornels = [ [349, 313], [412, 296], [350, 229], [295, 245], [352,369], [413, 346], [296, 289]] # image6 small
    # cornels = [ [472, 142], [412, 130],  [458, 227], [401, 224] ] #image3_alm test small
    # print(do_analysis_box(im_src, cornels))

    # boxes_points_ = box_rec.nn_caler(img)
    # boxes_points = [[ [349, 313], [412, 296], [350, 229], [295, 245], [352,369], [413, 346], [296, 289]]]
    boxes_points = [ [[380, 288], [355, 250], [365, 134], [390, 168], [426, 121], [456, 153], [442, 278]],
                     [[188, 285], [157,255], [149, 204], [243, 171], [275, 193], [284, 252], [171, 231]]
                    ]
    boxes = []
    # # print(boxes)
    for box_points in boxes_points:
        # print(box)
        im_src, box = do_analysis_box(im_src, box_points)
        boxes.append(box)
    cv2.imshow('Sizing',im_src)
    # do_analysis_box(im_src, boxes_points[0])
    # show_box(boxes[0][0], boxes[0][1], boxes[0][2])
    # print(boxes)
    show_boxes(boxes)

    # cv2.imshow('after', im_out)
    # cv2.imshow('after_eq2', equ)

    while (True):
        # ret, frame = cap.read()
        # cv2.imshow('Sizing',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
