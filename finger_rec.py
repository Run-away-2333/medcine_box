# -*- coding: utf-8 -*-
import serial
import time
import json
import threading

# 打开串口
PS_Getimage = [0XEF, 0X01, 0XFF, 0XFF, 0XFF, 0XFF, 0X01, 0X00, 0X03, 0X01, 0X00, 0X05]  # 录入图像
PS_GenChar1 = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, 0x01, 0x00, 0x08]  # 在特征区1生成特征
PS_GenChar2 = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, 0x02, 0x00, 0x09]  # 在特征区2生成特征
PS_Match = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x03, 0x00, 0x07]  # 对比匹配与否
PS_Search_stored1 = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x08, 0x04, 0x01, 0x00, 0x01, 0x00, 0x20, 0x00,
                     0x2F]  # 以特征区1的指纹特征进行全局搜索
PS_Search_stored2 = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x08, 0x04, 0x02, 0x00, 0x01, 0x00, 0x20, 0x00,
                     0x30]  # 以特征区2的指纹特征进行全局搜索
PS_RegModel = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x05, 0x00, 0x09]  # 合并1、2区特征并存于1、2区
PS_StoreChar_1tox = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x06, 0x06, 0x01, 0x00, 0x03, 0x00,
                     0x11]  # 在指纹库指定ID处添加指纹
PS_Empty = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x0d, 0x00, 0x11]  # 清空指纹库
PS_DeletChar = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x07, 0x0c, 0x00, 0x01, 0x00, 0x01, 0x00, 0x16]  # 清空指纹库
# global rec_data
rec_data = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
ID = None

mutex = threading.Lock()

with open("./config.json") as json_file:  # 配置文件
    init_config = json.load(json_file)

serialPort = init_config['com'][1]  # 串口6
baudRate = 57600  # 波特率


def Send_A_Cmd(serInstance, atCmdStr):
    # print("Command: %s" % atCmdStr)
    serInstance.write(atCmdStr)


def receive_data(ser):
    global rec_data
    while not (ser.inWaiting() > 0):
        pass
    rec_data = []
    time.sleep(0.1)
    if ser.inWaiting() > 0:
        for num in range(0, ser.inWaiting()):
            rec_data.insert(num, ser.read(1))
    ##===========调试用===========
    # if rec_data != [3,3,3,3,3,3,3,3,3,3]:
    #     if rec_data != []:
    #         print( rec_data )  # 可以接收中文


def check_and_set(ID):
    check = 0
    PS_StoreChar_1tox[11] = (ID // 256) % 256
    PS_StoreChar_1tox[12] = ID % 256
    check = PS_StoreChar_1tox[6] + (PS_StoreChar_1tox[7] * 256) + PS_StoreChar_1tox[8] + PS_StoreChar_1tox[9] + \
            PS_StoreChar_1tox[10] + (PS_StoreChar_1tox[11] * 256) + PS_StoreChar_1tox[12]
    PS_StoreChar_1tox[13] = (check // 256) % 256
    PS_StoreChar_1tox[14] = check % 256


def ADD_FINGERPRINT(ser):
    with open("fingerprint_databases/fingerprint_record.json") as json_file:
        json_data = json.load(json_file)
    current_size = json_data["current_size"]  # 读取当前容量
    save_id = 1  # 初始化将要保存的id
    counter = 0  # 指纹个数计数器
    if current_size >= 40:
        print("指纹库数据已满")
    else:
        while save_id <= 200:
            if str(save_id) in json_data:
                if json_data[str(save_id)] == "":
                    break
            else:
                break
            save_id += 5  # 寻找空值id
        nickname = str(save_id)  # 键值名
        while counter < 5:
            print(f'接下来将进行 {5 - counter} 次录入 (可以换手指进行以提高指纹命中率) >>')
            time.sleep(1)
            print("请录入指纹！")
            while rec_data[9] != b'\x00':  # 改成do while
                Send_A_Cmd(ser, PS_Getimage)
                receive_data(ser)
            rec_data[9] = 3
            while rec_data[9] != b'\x00':
                Send_A_Cmd(ser, PS_GenChar1)
                receive_data(ser)
            rec_data[9] = 3
            time.sleep(1)
            print("请确认刚才的指纹！")
            while rec_data[9] != b'\x00':
                Send_A_Cmd(ser, PS_Getimage)
                receive_data(ser)
            rec_data[9] = 3
            while rec_data[9] != b'\x00':
                Send_A_Cmd(ser, PS_GenChar2)
                receive_data(ser)
            rec_data[9] = 3
            Send_A_Cmd(ser, PS_Match)
            receive_data(ser)
            if rec_data[9] != b'\x00':
                print("不匹配, 录入指纹失败, 请重新录入")
            else:
                print("匹配, 请安指引继续操作")
                print(f"指纹库{save_id + counter}号创建成功！")
                counter += 1
            rec_data[9] = 3
            check_and_set(save_id + counter)
            Send_A_Cmd(ser, PS_StoreChar_1tox)
            receive_data(ser)
            if rec_data[9] == b'\x00':
                rec_data[9] = 3
            rec_data[9] = 3
        json_data.update({str(save_id - save_id % 5 + 1): nickname})
        json_data["current_size"] += 1
        with open("fingerprint_databases/fingerprint_record.json", 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)  # indent 缩进
            print("保存成功")


# 新增
def AddFingerprint(text, label, telephone_number):
    with mutex:
        label.setStyleSheet("QLabel{\n"
                            "    \n"
                            "   background-image: url(./resource_dir/src_img/fingerprint_type_in.png);\n"
                            "}")
        local_ser = serial.Serial(serialPort, baudRate, timeout=0.5)
        with open("fingerprint_databases/fingerprint_record.json") as json_file:
            json_data = json.load(json_file)
        current_size = json_data["current_size"]  # 读取当前容量
        save_id = 1  # 初始化将要保存的id
        counter = 0  # 指纹个数计数器
        if current_size >= 40:
            text.put("\n指纹库已满")
        else:
            while save_id <= 200:
                if str(save_id) in json_data:
                    if json_data[str(save_id)] == "":
                        break
                else:
                    break
                save_id += 5  # 寻找空值id
            nickname = telephone_number  # 键值名
            text.put('开始录入(切换手指指纹能更加广泛)')
            while counter < 5:
                text.put(f'剩余{5 - counter}次')
                time.sleep(1)
                text.put("请录入指纹")
                while rec_data[9] != b'\x00':  # 改成do while
                    Send_A_Cmd(local_ser, PS_Getimage)
                    receive_data(local_ser)
                rec_data[9] = 3
                while rec_data[9] != b'\x00':
                    Send_A_Cmd(local_ser, PS_GenChar1)
                    receive_data(local_ser)
                rec_data[9] = 3
                time.sleep(1)
                text.put("\n请确认刚才的指纹")
                while rec_data[9] != b'\x00':
                    Send_A_Cmd(local_ser, PS_Getimage)
                    receive_data(local_ser)
                rec_data[9] = 3
                while rec_data[9] != b'\x00':
                    Send_A_Cmd(local_ser, PS_GenChar2)
                    receive_data(local_ser)
                rec_data[9] = 3
                Send_A_Cmd(local_ser, PS_Match)
                receive_data(local_ser)
                if rec_data[9] != b'\x00':
                    text.put("不匹配, 请重新录入")
                else:
                    text.put("匹配请继续")
                    text.put(f"指纹库{save_id + counter}号创建成功！")
                    counter += 1
                rec_data[9] = 3
                check_and_set(save_id + counter)
                Send_A_Cmd(local_ser, PS_StoreChar_1tox)
                receive_data(local_ser)
                if rec_data[9] == b'\x00':
                    rec_data[9] = 3
                rec_data[9] = 3
            json_data.update({str(save_id - save_id % 5 + 1): nickname})
            json_data["current_size"] += 1
            with open("fingerprint_databases/fingerprint_record.json", 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)  # indent 缩进
                text.put("\n保存成功")
        label.setStyleSheet("QLabel{\n"
                            "    \n"
                            "   background-image: url(./resource_dir/src_img/fingerprint_pass.png);\n"
                            "}")
        # text.setStyleSheet("""QTextEdit{
        #     background-color: rgb(46, 46, 46);
        #     font-family: 礼品卉自由落体;
        #     color: #c0c0c0;
        #     border: none;
        # }""")
        local_ser.close()


# 查询
def CheckFingerprint(text, telephone_number):
    with mutex:
        local_ser = serial.Serial(serialPort, baudRate, timeout=0.5)
        with open("fingerprint_databases/fingerprint_record.json") as json_file:
            json_data = json.load(json_file)
        counter = 3
        while counter > 0:
            time.sleep(1)
            text.put("请刷入指纹")
            rec_data[9] = 3
            while rec_data[9] != b'\x00':
                Send_A_Cmd(local_ser, PS_Getimage)
                receive_data(local_ser)
            rec_data[9] = 3
            while rec_data[9] != b'\x00':
                Send_A_Cmd(local_ser, PS_GenChar1)
                receive_data(local_ser)
            rec_data[9] = 3
            Send_A_Cmd(local_ser, PS_Search_stored1)
            receive_data(local_ser)
            if rec_data[9] == b'\x00':
                rec_id = int.from_bytes(rec_data[10] * 256 + rec_data[11], byteorder='big', signed=False)
                if telephone_number == json_data[str(rec_id - rec_id % 5 + 1)]:
                    return json_data[str(rec_id - rec_id % 5 + 1)]
                else:
                    counter -= 1
                    text.put("\n请再次尝试")
            elif rec_data[9] == b'\x09':
                text.put("请重新刷入指纹")
            elif rec_data[9] == b'\x01':
                text.put("数据收包错误！")
        text.put("身份验证错误, 指纹库中没有匹配的身份!")
        local_ser.close()
        return ""


# 匹配指纹
def MatchFingerprint(text):
    with mutex:
        local_ser = serial.Serial(serialPort, baudRate, timeout=0.5)
        with open("fingerprint_databases/fingerprint_record.json") as json_file:
            json_data = json.load(json_file)
        counter = 3
        while counter > 0:
            time.sleep(1)
            text.put("请刷入指纹")
            rec_data[9] = 3
            while rec_data[9] != b'\x00':
                Send_A_Cmd(local_ser, PS_Getimage)
                receive_data(local_ser)
            rec_data[9] = 3
            while rec_data[9] != b'\x00':
                Send_A_Cmd(local_ser, PS_GenChar1)
                receive_data(local_ser)
            rec_data[9] = 3
            Send_A_Cmd(local_ser, PS_Search_stored1)
            receive_data(local_ser)
            if rec_data[9] == b'\x00':
                rec_id = int.from_bytes(rec_data[10] * 256 + rec_data[11], byteorder='big', signed=False)
                if str(rec_id - rec_id % 5 + 1) in json_data:
                    text.put(f'匹配到{json_data[str(rec_id - rec_id % 5 + 1)]}用户的指纹')
                    return json_data[str(rec_id - rec_id % 5 + 1)]
                else:
                    counter -= 1
                    text.put("\n请再次尝试")
            elif rec_data[9] == b'\x09':
                counter -= 1
                text.put("未检测到指纹, 请重新刷入")
            elif rec_data[9] == b'\x01':
                text.put("数据收包错误！")
        text.put("身份验证错误, 不存在该指纹")
        local_ser.close()
        return ""


def CHECK_FINGERPRINT(ser):
    with open("fingerprint_databases/fingerprint_record.json") as json_file:
        json_data = json.load(json_file)
    counter = 5
    while counter > 0:
        time.sleep(1)
        print("请刷入指纹")
        rec_data[9] = 3
        while rec_data[9] != b'\x00':
            Send_A_Cmd(ser, PS_Getimage)
            receive_data(ser)
        rec_data[9] = 3
        while rec_data[9] != b'\x00':
            Send_A_Cmd(ser, PS_GenChar1)
            receive_data(ser)
        rec_data[9] = 3
        Send_A_Cmd(ser, PS_Search_stored1)
        receive_data(ser)
        if rec_data[9] == b'\x00':
            rec_id = int.from_bytes(rec_data[10] * 256 + rec_data[11], byteorder='big', signed=False)
            print(rec_id)
            print(f"登录成功, 亲爱的{json_data[str(rec_id - rec_id % 5 + 1)]}用户, 早上号^_^!")
            return
        elif rec_data[9] == b'\x09':
            counter -= 1
            print("请重新刷入指纹")
        elif rec_data[9] == b'\x01':
            print("数据收包错误！")
    print("身份验证错误, 指纹库中没有匹配的身份!")


def CLEAR_LIBRARY(ser):
    with open("fingerprint_databases/fingerprint_record.json") as json_file:
        json_data = json.load(json_file)
    for _key in json_data:
        if _key == "id":
            continue
        elif _key == "current_size":
            json_data[_key] = 0
        else:
            json_data[_key] = ""
    rec_data[9] = 3
    while rec_data[9] != b'\x00':
        Send_A_Cmd(ser, PS_Empty)
        receive_data(ser)
    with open("fingerprint_databases/fingerprint_record.json", 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)  # indent 缩进
    print("指纹库已清空!")


def check_and_set_delete(ID, delete_num):
    global det_check
    PS_DeletChar[10] = (ID // 256) % 256
    PS_DeletChar[11] = ID % 256
    PS_DeletChar[12] = (delete_num // 256) % 256
    PS_DeletChar[13] = delete_num % 256
    det_check = PS_DeletChar[6] + (PS_DeletChar[7] * 256) + PS_DeletChar[8] + PS_DeletChar[9] + (
                PS_DeletChar[10] * 256) + \
                PS_DeletChar[11] + (PS_DeletChar[12] * 256) + PS_DeletChar[13]
    PS_DeletChar[14] = (det_check // 256) % 256
    PS_DeletChar[15] = det_check % 256


def DELETE_FINGERPRINTS(ser):
    with open("fingerprint_databases/fingerprint_record.json") as json_file:
        json_data = json.load(json_file)
    del_name = input("请输入要删除指纹的用户: ")
    reserve_json_data = {value: key for key, value in json_data.items()}  # 字典反转
    print(reserve_json_data)
    check_and_set_delete(int(reserve_json_data[del_name]), 5)
    rec_data[9] = 3
    Send_A_Cmd(ser, PS_DeletChar)
    receive_data(ser)
    if rec_data[9] == b'\x00':
        print(f"成功删除 {reserve_json_data[del_name]} ~ {int(reserve_json_data[del_name]) + 5}号 的指纹")
        print(f"成功删除{del_name}的指纹")
        json_data["current_size"] -= 1
        json_data[reserve_json_data[del_name]] = ""
        with open("fingerprint_databases/fingerprint_record.json", 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)  # indent 缩进
            print("保存成功")
    elif rec_data[9] == b'\x01':
        print("数据收包错误!")
    elif rec_data[9] == b'\x10':
        print("删除模板失败！")


if __name__ == '__main__':
    ser = serial.Serial(serialPort, baudRate, timeout=0.5)
    print("参数设置：串口= %s ，波特率= %d" % (serialPort, baudRate))

    while True:
        # -----------------------正式代码-------------------------
        print("请选择功能：1.录入指纹	  2.身份验证     3.删除ID=x起的n枚指纹	 4.格式化指纹库	 5.退出")
        selection = eval(input())
        if selection == 1:
            ADD_FINGERPRINT(ser)
        elif selection == 2:
            CHECK_FINGERPRINT(ser)
        elif selection == 3:
            DELETE_FINGERPRINTS(ser)
        elif selection == 4:
            CLEAR_LIBRARY(ser)
        elif selection == 5:
            break

