from PIL import Image
from io import BytesIO
import boto3
import logging

logger = logging.getLogger(__name__)

def pacify(face_file):
    pacify_img = Image.open('/app/pacifier.png')
    face_bytes = face_file.read()
    rekog = boto3.client('rekognition', 'us-east-1')
    res = rekog.detect_faces(Image={'Bytes': face_bytes})

    if len(res['FaceDetails']) == 0:
        raise Exception("No face detected in the image")

    face = res['FaceDetails'][0]

    img = Image.open(BytesIO(face_bytes))
    img_width = img.width
    img_height = img.height
    
    face_top_x = img_width * face['BoundingBox']['Left']
    face_top_y = img_height * face['BoundingBox']['Top']
    face_width = img_width * face['BoundingBox']['Width']
    face_height = img_height * face['BoundingBox']['Height']
    face_bottom_x = face_top_x + face_width
    face_bottom_y = face_top_y + face_height

    mouthLeft = ([x for x in face['Landmarks'] if x['Type'] == 'mouthLeft'])[0]
    mouthRight = ([x for x in face['Landmarks'] if x['Type'] == 'mouthRight'])[0]

    mouthRightX = img_width * mouthRight['X']
    mouthRightY = img_height * mouthRight['Y']
    mouthLeftX = img_width * mouthLeft['X']
    mouthLeftY = img_height * mouthLeft['Y']
    mouthCenterX = mouthRightX - ( (mouthRightX - mouthLeftX) / 2)
    mouthCenterY = mouthRightY - ( (mouthRightY - mouthLeftY) / 2)

    placement = (int(mouthCenterX), int(mouthCenterY))

    logger.info(res['FaceDetails'][0])
    logger.info("%d, %d" % (img.width, img.height))
    logger.info('%d, %d, %d, %d, %d, %d' % (face_top_x, face_top_y, face_width, face_height, face_bottom_x, face_bottom_y))
    logger.info("%d, %d, %d, %d" % (mouthRightX, mouthRightY, mouthLeftX, mouthLeftY))
    logger.info("%d, %d, %d, %d" % (
        mouthRightX,
        mouthRightY,
        mouthLeftX,
        mouthLeftY
    ))
    logger.info("%d, %d" % (mouthCenterX, mouthCenterY))
    logger.info(placement)
    mouth_width = mouthRightX - mouthLeftX
    ratio = mouth_width / pacify_img.width
    p_width = pacify_img.width * ratio
    p_height = pacify_img.height * ratio

    small_pacifier = pacify_img.resize((int(p_width), int(p_height)), Image.LANCZOS)
    img.paste(
        small_pacifier,
        (int(placement[0]-(p_width/2)), int(placement[1]-(p_height/2))),
        small_pacifier
    )
    return img
