import cv2
import os
import json
from ultralytics import YOLO

medicine_model = YOLO(model="model_databases/best.pt")

with open("config.json", 'r') as file_:
    cfg = json.load(file_)


def MedicineInference():
    cap_1 = cv2.VideoCapture(int(cfg["camera_id"]))
    counter = 0
    match_res = None
    while counter <= 100:
        ret, frame = cap_1.read()
        if not ret:
            break
        else:
            cv2.waitKey(20)
            counter += 1
            cv2.imshow(winname="medicine_recognize", mat=frame)
            if counter > 100 and counter % 10 == 0:
                # cv2.imshow(winname="药品识别", mat=frame)
                match_res = FlannMatch(frame)
                if match_res == "":
                    pass
                else:
                    cap_1.release()
                    cv2.destroyAllWindows()
                    return match_res
            elif counter % 10 == 0:
                res = medicine_model(frame, conf=0.25)
                rec_length = len(res[0].boxes.conf)
                # cv2.imshow(winname="medicine_recognize", mat=frame)
                print(res[0].boxes.conf)
                if rec_length == 0:
                    counter += 1
                    continue
                # 绘制推理结果
                # annotated_img = res[0].plot(labels=False)
                # # 显示图像
                # cv2.imshow(winname="medicine_recognize", mat=annotated_img)
                cap_1.release()
                cv2.destroyAllWindows()
                return res[0].names[int(res[0].boxes.cls[0].item())]
        # counter += 1
    cap_1.release()
    cv2.destroyAllWindows()
    return ""


# FLANN匹配
def FlannMatch(match_img):
    sift_algorithm = cv2.SIFT_create()
    src_kp, src_des = sift_algorithm.detectAndCompute(match_img, None)
    # 定义FLANN匹配器
    index_params = dict(algorithm=1, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    medicine_dir = "medicine_databases/"
    for filename in os.listdir(medicine_dir):
        # print(filename)
        if filename.endswith(".jpg"):
            databases_img = cv2.imread(medicine_dir + filename)
            data_kp, data_des = sift_algorithm.detectAndCompute(databases_img, None)
            # 使用KNN算法匹配
            matches = flann.knnMatch(src_des, data_des, k=2)
            # 去除错误匹配
            good = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good.append(m)
            if len(good) > 50:
                return filename[:-4]
            # 可视化匹配结果（可选）
            # matched_img = cv2.drawMatches(match_img, src_kp, databases_img, data_kp, good, None)
            # cv2.imshow("Matched Features", matched_img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
    return ""


if __name__ == '__main__':
    print(MedicineInference())


