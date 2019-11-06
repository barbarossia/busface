from busface.spider.faceParser import parse_faces, url_to_image


def test_save_detect_face():
    face_url = 'https://pics.javcdn.pw/cover/5h4p_b.jpg'

    blob = parse_faces(face_url)
    blob




