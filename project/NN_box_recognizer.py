import cv2
import numpy as np
import glob

from new_image_differ import histogram_color_dominator as hcd
from new_image_differ import corner_find as cf

def box_recognizer(image, net, classes, output_layers, required_confidence, rect_scale):
	img = image

	#rect_scale = 1.1

	height, width, channels = img.shape

	# Detecting objects
	blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

	net.setInput(blob)
	outs = net.forward(output_layers)

	# Showing informations on the screen
	class_ids = []
	confidences = []
	boxes = []
	BOXES_POINTS = []
	for out in outs:
		for detection in out:
			scores = detection[5:]
			class_id = np.argmax(scores)
			confidence = scores[class_id]
			if confidence > required_confidence:
				# Object detected
				#print(class_id)
				center_x = int(detection[0] * width)
				center_y = int(detection[1] * height)
				w = int(detection[2] * width)
				h = int(detection[3] * height)

				# Rectangle coordinates
				x = int(center_x - w / 2)-int(0.07*w)
				y = int(center_y - h / 2)-int(0.07*h)

				boxes.append([x, y, w, h])
				confidences.append(float(confidence))
				class_ids.append(class_id)

	indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
	#print(indexes)
	font = cv2.FONT_HERSHEY_PLAIN
	for i in range(len(boxes)):
		if i in indexes:
			x, y, w, h = boxes[i]

			crop_img = img[y:y+int(rect_scale*h), x:x+int(rect_scale*w)]
			hcd_img = hcd(crop_img)

			#hcd_img_height, hcd_img_width, hcd_img_channels = hcd_img.shape
			#hcd_img_center_x = int(hcd_img_width/2)
			#hcd_img_center_y = int(hcd_img_height/2)
			#print(hcd_img_height)
			#print(hcd_img_width)
			#print(hcd_img_center_x)
			#print(hcd_img_center_y)
			#center_color = hcd_img[hcd_img_center_y, hcd_img_center_x]
			#print ("center_color: {0}".format(center_color))
			"""
			hcd_img_height, hcd_img_width, hcd_img_channels = hcd_img.shape
			hcd_img_center_x = int(hcd_img_width/2)
			hcd_img_center_y = int(hcd_img_height/2)
			print (hcd_img_width)
			print (hcd_img_height)
			print("--------------")
			print (hcd_img_center_x)
			print (hcd_img_center_y)
			print("--------------")
			print (hcd_img[hcd_img_center_x, hcd_img_center_y])
			print (hcd_img[hcd_img_height-1, hcd_img_width-1])
			for i in range(0, hcd_img_height):
				for j in range(0, hcd_img_width):
					if hcd_img[i, j] is not hcd_img[hcd_img_center_x, hcd_img_center_y]:
						hcd_img[i, j] = (0, 0, 0)
			"""
			mask = cv2.cvtColor(hcd_img, cv2.COLOR_BGR2GRAY)
			#cv2.imshow('mask', mask)
			#cv2.waitKey(0)

			th = 135
			imask =  mask>th

			hcd_img_canvas = np.zeros_like(hcd_img, np.uint8)
			hcd_img_canvas[imask] = hcd_img[imask]

			box_corn_points = cf(hcd_img_canvas)#hcd_img_canvas
			#box_corn_points_a = []
			#box_corn_points_a.append(box_corn_points)
			#label = str(classes[class_ids[i]])
			#color = colors[class_ids[i]]
			#cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
			#cv2.imshow('img', img)
			#cv2.putText(img, label, (x, y + 30), font, 3, color, 2)
			boxes_point = []
			boxes_point = [(box_corn_points)]
			BOXES_POINTS.append((boxes, box_corn_points))

	#cv2.imshow('img', img)
	return BOXES_POINTS

def nn_caler(img, net, layer_names):
	rect_scale = 1.1
	#img = cv2.imread("./images/nn_test.jpg")
	# Load Yolo
	#net = cv2.dnn.readNet("yolov3_training_last.weights", "yolo-obj.cfg")

	#layer_names = net.getLayerNames()
	output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

	# Name custom object
	classes = ["box"]

	NON_FUNC_BOXES_POINTS = box_recognizer(img, net, classes, output_layers, 0.4, rect_scale)

	print (len(NON_FUNC_BOXES_POINTS))
	print ("NON_FUNC_BOXES_POINTS:\n {0}".format(NON_FUNC_BOXES_POINTS))

	boxes = []

	for nfbp in range(len(NON_FUNC_BOXES_POINTS)):	
		box_center, box_corner_points = NON_FUNC_BOXES_POINTS[nfbp]

		#color = np.array((np.asscalar(np.int16(cent_color[0])),np.asscalar(np.int16(cent_color[1])),np.asscalar(np.int16(cent_color[2]))))
		#color = np.array((int(cent_color[0]),int(cent_color[1]),int(cent_color[2])))
		#print ("color: {0}".format(color))

		print ("box_center:\n {0}".format(box_center))
		print ("box_corner_points:\n {0}".format(box_corner_points))

		x, y, w, h = box_center[nfbp]
		cv2.rectangle(img, (x, y), (x + int(rect_scale*w), y + int(rect_scale*h)), (255, 0, 0), 2)
		cv2.circle(img, (x, y), 25, (0,255,0), -1)
		# cv2.imshow('img_with_rectngle', img)
		#cv2.waitKey(0)

		box = []

		for bcp in range(len(box_corner_points) - 1):
			bcp_x, bcp_y = box_corner_points[bcp]
			new_x=x+bcp_x
			new_y=y+bcp_y

			box.append([new_x, new_y])

			# cv2.circle(img, (new_x, new_y), 5, (0,0,255), -1)
			#cv2.imshow('img_with_rectngle', img)
			#cv2.waitKey(0)

		# cv2.imshow('img_with_rectngle', img)
		#cv2.waitKey(0)

		boxes.append(box)

	return boxes


# Load Yolo
net = cv2.dnn.readNet("yolov3_training_last.weights", "yolo-obj.cfg")

layer_names = net.getLayerNames()


#img = cv2.imread("./images/image0(1).png")
#nn_caler(img, net, layer_names)
#cv2.waitKey(0)

if __name__ == "__main__":
	out = cv2.VideoWriter('outpyy.mp4',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (640,480))
	pruf = cv2.VideoWriter('pruff2.mp4',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (640,480))

	cap = cv2.VideoCapture(0)
	while(1):
		ret, img = cap.read()
		if ret == True:
			out.write(img)
			nn_caler(img, net, layer_names)
			pruf.write(img)

			if cv2.waitKey(10) == 27:
				break

	cap.release()
	cv2.destroyAllWindows()

	"""
	rect_scale = 1.1
	img = cv2.imread("./images/nn_test.jpg")
	# Load Yolo
	net = cv2.dnn.readNet("yolov3_training_last.weights", "yolo-obj.cfg")

	layer_names = net.getLayerNames()
	output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

	# Name custom object
	classes = ["box"]

	NON_FUNC_BOXES_POINTS = box_recognizer(img, net, classes, output_layers, 0.7, rect_scale)
	print ("NON_FUNC_BOXES_POINTS:\n {0}".format(NON_FUNC_BOXES_POINTS))

	for nfbp in range(len(NON_FUNC_BOXES_POINTS)):	
		box_center, box_corner_points = NON_FUNC_BOXES_POINTS[nfbp]

		print ("box_center:\n {0}".format(box_center))
		print ("box_corner_points:\n {0}".format(box_corner_points))

		x, y, w, h = box_center[nfbp]
		cv2.rectangle(img, (x, y), (x + int(rect_scale*w), y + int(rect_scale*h)), (255, 0, 0), 2)
		cv2.circle(img, (x, y), 25, (0,255,0), -1)
		cv2.imshow('img_with_rectngle', img)
		cv2.waitKey(0)

		for bcp in range(len(box_corner_points)):
			bcp_x, bcp_y = box_corner_points[bcp]
			new_x=x+bcp_x
			new_y=y+bcp_y
			cv2.circle(img, (new_x, new_y), 5, (0,0,255), -1)

		cv2.imshow('img_with_rectngle', img)
		cv2.waitKey(0)
	"""


