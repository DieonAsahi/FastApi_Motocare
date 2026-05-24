from paddleocr import PaddleOCR
import cv2
import re

ocr = PaddleOCR(use_angle_cls=False, lang='en')

def read_odometer(image_path):

    result = ocr.ocr(image_path)

    detected = []

    if result and result[0]:
        for line in result[0]:
            box = line[0]
            text = line[1][0]

            digit = re.sub(r'[^0-9]', '', text)

            if digit:
                x_pos = box[0][0]  # posisi x kiri
                detected.append((x_pos, digit))

    # urut kiri ke kanan
    detected.sort(key=lambda x: x[0])

    final_text = ''.join([d[1] for d in detected])

    return final_text