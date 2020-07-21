import cv2
import numpy as np
import analysis_box as anal #it is my file

if __name__ == "__main__":
    scale = 640 / 42
    COLOR = (0, 0, 255)

    def onMouse(event, x, y, flags, param):
        if( event != cv2.EVENT_LBUTTONDOWN ):
            return;
        point = anal.get_coord([x,y])
        cv2.circle(table, (int(point[0] * scale), int(point[2] * scale)), 8, COLOR, -1)
        cv2.imshow('Table',table)

    # print(iRot)
    # print(translation_vector)
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cv2.imshow('Sizing',frame)
    cv2.setMouseCallback('Sizing', onMouse)

    # cornels = [ [174, 264], [163, 219], [222, 128], [162, 139], [233, 252], [234, 161], [172, 165] ] # image1 small
    # cornels = [ [174, 264], [163, 219], [162, 139], [233, 252], [234, 161], [172, 165] ] # image1_test small
    cornels = [ [401, 224], [458, 227], [416, 108], [473, 112], [472, 142], [412, 130] ] #image3 small
    # cornels = [ [472, 142], [412, 130],  [458, 227], [401, 224] ] #image3_alm test small
    anal.anal_box(frame, cornels)

    # print(get_coord_top([355, 103], get_coord([351, 153])))

    table = cv2.imread('table.png')
    cv2.imshow('Table',table)

    while (True):
        ret, frame = cap.read()
        cv2.imshow('Sizing',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

