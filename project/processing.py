import cv2
import numpy as np

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
    (210, 79), 
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

def get_coord(point):
    un_point = cv2.undistortPoints(np.array(point).astype(np.float32), camera_matrix, dist_matrix, P = camera_matrix)
    un_point = un_point.ravel().tolist()
    uvPoint = np.matrix([un_point[0], un_point[1], 1]).T
    tempMat = np.matmul(np.matmul(iRot, iCam), uvPoint)
    tempMat2 = np.matmul(iRot, translation_vector)
    s = (0 + tempMat2[1, 0]) / tempMat[1, 0]
    wcPoint = np.matmul(iRot, (np.matmul(s * iCam, uvPoint) - translation_vector))
    wcPoint[1] = 0
    point3d = wcPoint.T.tolist()[0]
    return point3d

scale = 640 / 42
COLOR = (0, 0, 255)

def onMouse(event, x, y, flags, param):
    if( event != cv2.EVENT_LBUTTONDOWN ):
        return;
    point = get_coord([x,y])
    cv2.circle(table, (int(point[0] * scale), int(point[2] * scale)), 8, COLOR, -1)
    cv2.imshow('Table',table)

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cv2.imshow('Sizing',frame)
cv2.setMouseCallback('Sizing', onMouse)

table = cv2.imread('table.png')
cv2.imshow('Table',table)

while (True):
    ret, frame = cap.read()
    cv2.imshow('Sizing',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

