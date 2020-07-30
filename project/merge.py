import cv2
import numpy as np
import analysis_box as analysis #it is my file
import NN_box_recognizer as box_rec # from Slava

if __name__ == "__main__":
    # cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture('./video/outpyy.mp4')

    ret, img = cap.read()
    while (img is not None):
        ret, img = cap.read()
        
        temp_image = img.copy()
        boxes_points = box_rec.nn_caler(temp_image, box_rec.net, box_rec.layer_names)

        if boxes_points != [] and (len(boxes_points[0]) > 3):
            if  len(boxes_points) == 1 or len(boxes_points[1]) > 3:
                boxes = []
                
                for box_points in boxes_points:
                    img, box = analysis.do_analysis_box(img, box_points)
                    boxes.append(box)
                cv2.imshow('Sizing',img)

                analysis.show_boxes(boxes)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break