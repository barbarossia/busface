from busface.spider.faceParser import parse_face, url_to_image


def test_save_detect_face():
    face_url = 'https://pics.javcdn.pw/cover/798z_b.jpg'

    blob = parse_face(face_url)
    blob




