import cv2
from busface.util import get_model_path

config_path = get_model_path("resnet_ssd_v1.prototxt")
model_path = get_model_path("resnet_ssd_v1.caffemodel")
detector = cv2.dnn.readNetFromCaffe(config_path, model_path)
detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
target = (300, 300)
configConfidence = 50/100


def compile_detection_image(input_image):
    image = input_image.copy()
    scale = set_scale(image)
    image = scale_image(image, scale)
    return [image, scale]

def set_scale(image):
    height, width = image.shape[:2]
    source = max(height, width)

    scale = target[0] / source

    return scale

def scale_image(image, scale):
    height, width = image.shape[:2]
    interpln = cv2.INTER_LINEAR if scale > 1.0 else cv2.INTER_AREA
    if scale != 1.0:
        dims = (int(width * scale), int(height * scale))
        image = cv2.resize(image, dims, interpolation=interpln)
    return image

def to_bounding_box_dict(left, top, right, bottom):

    return [int(round(left)),
    		int(round(top)),
			int(round(right))-int(round(left)),
			int(round(bottom))-int(round(top))]

def process_output(faces, scale, width, height):
    # face[0] -- left
    # face[1] -- top
    # face[2] -- right
    # face[3] -- bottom

    faces = [to_bounding_box_dict(face[0] / scale, face[1] / scale, face[2] / scale, face[3]/ scale) for face in faces]

    return faces

def detect_faces_dnn(inputImg):

	[detect_image, scale] = compile_detection_image(inputImg) 
	height, width = detect_image.shape[:2]
	for angle in [0]:
		current_image = detect_image
		blob = cv2.dnn.blobFromImage(current_image,
										1.0,target,
										[104, 117, 123],
										False,
										False)
		detector.setInput(blob)
		detected = detector.forward()
		faces = list()
		for i in range(detected.shape[2]):
			confidence = detected[0,0,i,2]
			if confidence >= configConfidence:
				faces.append([(detected[0, 0, i, 3] * width),
							(detected[0, 0, i, 4] * height),
							(detected[0, 0, i, 5] * width),
							(detected[0, 0, i, 6] * height)])

		return process_output(faces, scale, width, height)

def drawPos(pic,x,y,w,h,txt,colr):
	boadw = 10
	cv2.line(pic,(x,y),(x+boadw,y),colr,1)
	cv2.line(pic,(x,y),(x,y+boadw),colr,1)

	cv2.line(pic,(x+w,y),(x+w-boadw,y),colr,1)
	cv2.line(pic,(x+w,y),(x+w,y+boadw),colr,1)

	cv2.line(pic,(x,y+h),(x+boadw,y+h),colr,1)
	cv2.line(pic,(x,y+h),(x,y+h-boadw),colr,1)

	cv2.line(pic,(x+w,y+h),(x+w-boadw,y+h),colr,1)
	cv2.line(pic,(x+w,y+h),(x+w,y+h-boadw),colr,1)

	font = cv2.FONT_HERSHEY_SIMPLEX
	cv2.putText(pic,txt,(x,y-10), font, 0.5,colr,1,cv2.LINE_AA)