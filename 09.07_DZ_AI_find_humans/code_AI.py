import cv2
import numpy as np

print("Input name of video or camera/0")
cap = cv2.VideoCapture(input())
net = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')
ret, frame = cap.read()
color = [0, 255, 0]
W = frame.shape[1]
H = frame.shape[0]

while(cap.isOpened()):
    blob = cv2.dnn.blobFromImage(frame, 
                             scalefactor=1/255.0,
                             size=(416,416), 
                             swapRB=True)
    boxes = []
    confidences = []
    net.setInput(blob)
    result = net.forward(net.getUnconnectedOutLayersNames())
    for output in result:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            if classID == 0:
                confidence = scores[0]
                if confidence > 0.7:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.4, 0.4)
    text = 'num of humans = ' + str(len(idxs))
    cv2.putText(frame, text, (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    ret, frame = cap.read()

