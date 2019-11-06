import numpy as np
import cv2
import traceback
import busface.model.faceDetector as fd
import urllib.request
from busface.util import logger, APP_CONFIG, get_model_path
import dlib


DESIRED_SIZE = int(APP_CONFIG['sample.output_size'])
SCALE_RATIO = float(APP_CONFIG['sample.scale_ratio'])

model_path = get_model_path("shape_predictor_68_face_landmarks.dat")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(model_path)

class AppURLopener(urllib.request.FancyURLopener):
    version = "App/1.7"

def face_data_normalizer(image, align_faces_=True, output_size=256):
    faces = []

    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)

    if len(rects) > 0:
        # loop over the face detections
        for (i, rect) in enumerate(rects):
            if align_faces_:
                ######### Align with facial features detector #########

                shape = predictor(gray, rect)  # get facial features
                shape = np.array([(shape.part(j).x, shape.part(j).y) for j in range(shape.num_parts)])

                # center and scale face around mid point between eyes
                center_eyes = shape[27].astype(np.int)
                eyes_d = np.linalg.norm(shape[36] - shape[45])
                face_size_x = int(eyes_d * 2.)
                if face_size_x < 50: continue

                # rotate to normalized angle
                d = (shape[45] - shape[36]) / eyes_d  # normalized eyes-differnce vector (direction)
                a = np.rad2deg(np.arctan2(d[1], d[0]))  # angle
                scale_factor = float(output_size) / float(face_size_x * 2.)  # scale to fit in output_size
                if scale_factor > SCALE_RATIO: continue
                # rotation (around center_eyes) + scale transform
                M = np.append(cv2.getRotationMatrix2D((center_eyes[0], center_eyes[1]), a, scale_factor),
                              [[0, 0, 1]], axis=0)
                # apply shift from center_eyes to middle of output_size
                M1 = np.array([[1., 0., -center_eyes[0] + output_size / 2.],
                               [0., 1., -center_eyes[1] + output_size / 2.],
                               [0, 0, 1.]])
                # concatenate transforms (rotation-scale + translation)
                M = M1.dot(M)[:2]
                # warp
                try:
                    face = cv2.warpAffine(image, M, (output_size, output_size), borderMode=cv2.BORDER_REPLICATE)
                except:
                    continue
                face = cv2.resize(face, (output_size, output_size))
                img_encode = cv2.imencode('.jpg', face)[1]
                blob = img_encode.tobytes()
                faces.append(blob)
            else:
                ######### "No align" with just the detector #########
                if rect.width() < 50: continue

                # find scale factor
                scale_factor = float(output_size) / float(rect.width() * 2.)  # scale to fit in output_size

                # scale around the center of the face (shift a bit for the approximate y-position of the eyes)
                M = np.append(cv2.getRotationMatrix2D((rect.center().x, rect.center().y - rect.height() / 6.), 0,
                                                      scale_factor), [[0, 0, 1]], axis=0)
                # apply shift from center_eyes to middle of output_size
                M1 = np.array([[1., 0., -rect.center().x + output_size / 2.],
                               [0., 1., -rect.center().y + output_size / 2. + rect.height() / 6.],
                               [0, 0, 1.]])
                # concatenate transforms (rotation-scale + translation)
                M = M1.dot(M)[:2]
                try:
                    face = cv2.warpAffine(image, M, (output_size, output_size), borderMode=cv2.BORDER_REPLICATE)
                    img_encode = cv2.imencode('.jpg', face)[1]
                    blob = img_encode.tobytes()
                    faces.append(blob)
                except:
                    continue
        #faces = np.asarray(faces)
        return faces


def parse_faces(url):
    inputImg = url_to_image(url)
    faces = face_data_normalizer(inputImg, align_faces_=True, output_size=DESIRED_SIZE)
    return faces

def url_to_image(url):
    try:
        opener = AppURLopener()
        response = opener.open(url)
        image = np.asarray(bytearray(response.read()), dtype="uint8")
        #image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    except Exception as e:
        traceback.print_exc()
        return None
    return image
