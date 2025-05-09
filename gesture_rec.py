import cv2
import requests
import base64
# import pyttsx3

# engine = pyttsx3.init()
# client_id 为官网获取的AK， client_secret 为官网获取的SK
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials' \
       '&client_id=rmO6jLGRH2ayzpsWW848mYfe&client_secret=PKfgBGGCssP3pOnOKeai9O5KFEVLnNG9'
# response = requests.get(host)
# global ac_token
# if response:
#     print(response.json())
#     ac_token=response.json()["access_token"]
# print(ac_token)
import json
'''
手势识别
'''

finger_digital_arr = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight']

request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/gesture"

with open("./gesture_databases/access_token.txt") as access_file:
    access_token = access_file.read()

with open("config.json", 'r') as file_:
    cfg = json.load(file_)


# 获取token
def GetAccessToken():
    require_host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials' \
           '&client_id=COh16I5zzx8VmJQYHknt9emo&client_secret=pkDHiMymGdqeaqiIKWzabX1VgvGkXWou'
    gesture_response = requests.get(require_host)
    if gesture_response.status_code != 200:  # 请求失败
        print('none')
        return None
    else:
        return gesture_response.json()["access_token"]


# 手势识别之握拳注册药品
def FistRegisterMedicine(text_queue):
    global access_token
    # with open("./gesture_databases/access_token.txt") as access_file:
    #     access_token = access_file.read()
    refresh_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    register_cap = cv2.VideoCapture(int(cfg["camera_id"]))  # 创建一个 VideoCapture 对象
    counter = 0
    while counter <= 1500:
        cap_flag, frame = register_cap.read()
        cv2.imshow("register_medicine", frame)
        if counter % 50 == 0:
            cv2.imwrite("./gesture_databases/fist.jpg", frame)
            src_img = open("./gesture_databases/fist.jpg", 'rb')
            fist_img = base64.b64encode(src_img.read())
            params = {"image": fist_img}
            response_1 = requests.post(refresh_url, data=params, headers=headers)
            if response_1.status_code == 200 and response_1.json().get('result') is not None:
                print(response_1.json())
                for x in response_1.json()['result']:
                    if x['classname'] == 'Ok':
                        # engine.say("拳头")
                        # engine.runAndWait()
                        text_queue.put('\n注册完成, 不满意再次点击')
                        register_cap.release()
                        cv2.destroyAllWindows()
                        return frame
                    elif x['classname'] == 'Thumb_up':
                        text_queue.put('\n注册已经取消')
                        register_cap.release()
                        cv2.destroyAllWindows()
                        return None
            else:
                access_token = GetAccessToken()
                refresh_url = request_url + "?access_token=" + access_token
                if access_token is None:
                    text_queue.put('\naccess_token获取失败, 刷新中...')
                with open("./gesture_databases/access_token.txt", 'wt') as save_file:
                    save_file.write(access_token)
                print(f"Error: {response_1.status_code}: {response_1.text}")
        cv2.waitKey(10) & 0xFF
        counter += 1


def OpenAssignMedicineBox(text_queue):
    global access_token
    refresh_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    register_cap = cv2.VideoCapture(int(cfg["camera_id"]))  # 创建一个 VideoCapture 对象
    counter = 0
    while counter <= 500:
        cap_flag, frame = register_cap.read()
        cv2.imshow("open_medicine_box", frame)
        if counter % 50 == 0:
            cv2.imwrite("./gesture_databases/fist.jpg", frame)
            src_img = open("./gesture_databases/fist.jpg", 'rb')
            fist_img = base64.b64encode(src_img.read())
            params = {"image": fist_img}
            refresh_url = request_url + "?access_token=" + access_token
            response_1 = requests.post(refresh_url, data=params, headers=headers)
            if 'result' not in response_1.json():
                print(response_1.json())
                access_token = GetAccessToken()
                continue
            gesture_res = response_1.json()['result']
            if response_1.status_code == 200 and gesture_res is not None:
                for single_gesture in gesture_res:
                    for index in range(0, len(finger_digital_arr)):
                        if single_gesture['classname'] == finger_digital_arr[index]:
                            text_queue.put(f'\n打开{index+1}号药盒')
                            register_cap.release()
                            cv2.destroyAllWindows()
                            return index+1
                        if single_gesture['classname'] == 'Thumb_up':
                            register_cap.release()
                            cv2.destroyAllWindows()
                            return 0
            else:
                access_token = GetAccessToken()
                refresh_url = request_url + "?access_token=" + access_token
                if access_token is None:
                    text_queue.put('\naccess_token获取失败, 刷新中...')
                with open("./gesture_databases/access_token.txt", 'wt') as save_file:
                    save_file.write(access_token)
                print(f"Error: {response_1.status_code}: {response_1.text}")
        cv2.waitKey(10) & 0xFF
        counter += 1
    return None
# FistRegisterMedicine()
# cap.release() #释放摄像头
# cv2.destroyAllWindows()#删除建立的全部窗口
