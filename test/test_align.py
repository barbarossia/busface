import cv2
import numpy as np
import dlib
import os
import shutil

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('../test/shape_predictor_68_face_landmarks.dat')

def test_detector_face_noalign():
    images_path = '../test/6rfl_b.jpg'
    faces = face_data_normalizer(images_path, align_faces_=False, output_size=50)
    write_faces_to_disk('data/faces', faces)

def test_detector_face_align():
    images_path = '../test/6rfl_b.jpg'
    faces = face_data_normalizer(images_path, align_faces_=True, output_size=256)
    write_faces_to_disk('data/faces', faces)

def write_faces_to_disk(directory, faces):
    print("writing faces to disk...")
    if os.path.exists(directory):
        shutil.rmtree(directory)
    print('creating output directory: %s' % (directory))
    os.mkdir(directory)
    for i in range(faces.shape[0]):
        cv2.imwrite(''.join([directory, "%03d.jpg" % i]), faces[i, :, ::-1])
    print("wrote %d faces" % (faces.shape[0]))

def face_data_normalizer(images_path, align_faces_=True, output_size=256):
    image = cv2.imread(images_path)
    if image is None:
        return

    faces = []
    #image = image[:, :, ::-1]  # BGR to RGB
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
                faces.append(face)
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
                    faces.append(face)
                except:
                    continue
        faces = np.asarray(faces)
        return faces

