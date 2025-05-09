import json

import cv2
import face_recognition
import time
import os
from datetime import datetime

known_encodings = []
known_names = []

with open("config.json", 'r') as file_:
    cfg = json.load(file_)


def ShowFace():
    """
    摄像头人脸检测并保存函数
    功能：打开摄像头检测人脸，检测到立即保存图片并退出，超时未检测则退出

    参数：
    timeout: int 超时时间（秒），默认15秒
    output_path: str 保存图片路径，默认"detected_face.jpg"
    """
    timeout = 15
    output_path = 'face_databases/'
    # 初始化摄像头（0表示默认摄像头）
    cap = cv2.VideoCapture(int(cfg["camera_id"]))
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return

    # 记录开始时间
    start_time = time.time()

    try:
        while True:
            # 读取摄像头帧
            ret, frame = cap.read()
            if not ret:
                print("错误：无法获取视频帧")
                break

            # 将BGR图像转换为RGB格式（face_recognition需要RGB格式）
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 人脸检测（使用HOG模型，适合CPU实时检测）
            face_locations = face_recognition.face_locations(rgb_frame)

            # 如果检测到人脸
            if len(face_locations) > 0:
                # 生成带时间戳的文件名
                # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # filename = f"face_{timestamp}.jpg"

                # 保存图片（使用原始BGR格式保存，保持OpenCV兼容性）
                # cv2.imwrite(filename, frame)
                # print(f"检测到人脸，已保存图片至：{filename}")
                return frame

            # 显示实时画面（可选）
            cv2.imshow('Face Detection', frame)

            # 检测超时
            if (time.time() - start_time) > timeout:
                print(f"{timeout}秒内未检测到人脸")
                return None

            # 按'q'键可手动退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return None

    finally:
        # 释放资源
        cap.release()
        cv2.destroyAllWindows()


def RefreshFaceDatabases(text_queue=None):
    """
    实时人脸匹配函数
    功能：读取目录中的已知人脸图片，实时匹配摄像头画面，匹配成功立即返回，超时返回None

    参数：
    database_dir: str  包含已知人脸图片的目录路径
    timeout: int      超时时间（秒），默认15秒
    tolerance: float  人脸匹配阈值（越小越严格），默认0.6

    返回：
    match_name: str|None  匹配到的人名（使用文件名），未匹配返回None
    """
    # ========================= 1. 加载已知人脸数据库 =========================
    database_dir = 'face_databases'

    global known_encodings
    global known_names

    # 遍历目录中的所有文件
    for filename in os.listdir(database_dir):
        # 只处理图片文件（支持jpg, png, jpeg）
        # print(os.path.splitext(filename)[0], known_names)
        if os.path.splitext(filename)[0] in known_names or os.path.splitext(filename)[0].find('reduce') != -1:
            print('exists')
            continue
        filepath = os.path.join(database_dir, filename)
        # print("???")
        # 加载图片并转换颜色空间
        image = face_recognition.load_image_file(filepath)

        # 提取人脸编码（假设每张图片只有一个人脸）
        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            # 取第一张检测到的人脸
            known_encodings.append(encodings[0])
            # 使用文件名（不带扩展名）作为人名标识
            known_names.append(os.path.splitext(filename)[0])
        else:
            print(f"警告：{filename} 未检测到人脸，已跳过")

    index = 0
    for face_name in known_names:
        if face_name+".jpg" not in os.listdir(database_dir):
            known_encodings.remove(index)
            known_names.remove(index)
            print("remove")
            index -= 1
        index += 1

    if text_queue is not None:
        text_queue.put('人脸数据库更新完成')

    if not known_encodings:
        print("错误：数据库中没有有效人脸数据")
        return None


def TestFace(face_message=""):
    global known_encodings
    global known_names

    timeout = 15
    tolerance = 0.6
    # ========================= 2. 初始化摄像头 =========================
    cap = cv2.VideoCapture(int(cfg["camera_id"]))
    if not cap.isOpened():
        print("错误：无法打开摄像头")
        return None

    if face_message.endswith('.jpg'):
        face_message = face_message[:-4]

    assign_face = None

    if face_message != "":  # 找到指定人脸
        for index in range(0, len(known_names)):
            if face_message == known_names[index]:
                assign_face = known_encodings[index]
                break
    # 设置视频分辨率（提高处理速度）
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    start_time = time.time()
    match_result = None

    try:
        # ========================= 3. 实时匹配循环 =========================
        while True:
            # 读取视频帧
            ret, frame = cap.read()
            if not ret:
                print("错误：无法获取视频帧")
                break

            # 将BGR转换为RGB格式
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 检测人脸位置（使用HOG模型保证实时性）
            face_locations = face_recognition.face_locations(rgb_frame)

            # 如果检测到人脸
            if face_locations:
                # 提取所有人脸编码
                current_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                # 遍历每个检测到的人脸

                for encoding in current_encodings:
                    if face_message != "":  # 指定人脸不需匹配所有人脸
                        matches = face_recognition.compare_faces(
                            [assign_face, ], encoding, tolerance=tolerance
                        )
                        # print(matches)
                    else:
                        # 与数据库进行比对
                        matches = face_recognition.compare_faces(
                            known_encodings, encoding, tolerance=tolerance
                        )

                    # 检查是否有匹配项
                    if True in matches:
                        if face_message == "":  # 检测人脸与数据库比对
                            # 获取第一个匹配项的索引
                            first_match_index = matches.index(True)
                            match_result = known_names[first_match_index]
                            print(f"匹配：{match_result}")
                            return match_result
                        if face_message != "":  # 检测人脸与指定人脸匹配
                            print(f"匹配: {face_message}")
                            return face_message

            # 显示实时画面（左上角显示倒计时）
            elapsed_time = time.time() - start_time
            cv2.imshow('Face Matching', frame)
            # 超时检测
            if elapsed_time >= timeout:
                print("超时：未匹配到已知人脸")
                break

            # 按Q键可手动退出
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    finally:
        # 释放资源
        cap.release()
        cv2.destroyAllWindows()

    return ""


if __name__ == "__main__":
    # 使用示例
    # ShowFace()
    RefreshFaceDatabases()
    RefreshFaceDatabases()
    # TestFace()
    time_1 = time.time()
    print(time_1)
    TestFace("3_3")
    print(time.time() - time_1)
    time_1 = time.time()
    TestFace()
    print(time.time() - time_1)
    time_1 = time.time()
    TestFace("1_1")
    print(time.time() - time_1)
    time_1 = time.time()
    TestFace()
    print(time.time() - time_1)
    time_1 = time.time()
    TestFace("张宸恺_674060542@qq.com")
    print(time.time() - time_1)
    time_1 = time.time()
    TestFace()
    print(time.time() - time_1)
    # time_1 = time.time()