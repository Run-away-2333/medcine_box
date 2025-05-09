import time

import serial
import asyncio
import queue
import threading

box_flag: bool = False
mutex = threading.Lock()
mutex_2 = threading.Lock()
string_queue: queue = queue.Queue()  # string队列


def InitPort(com_str: serial) -> serial:
    # 串口连接
    com_id = serial.Serial(com_str, 9600)  # 绑定端口
    com_id.timeout = 2
    print(f"{com_str}初始化完成")
    return com_id


# 格式为 open_box_1 为打开一号药盒
def OpenBox(com_a: serial, open_id: str):
    with mutex:
        motion = "open_box_" + open_id
        string_queue.put(motion)


def OpenBoxNew(open_id: str):
    with mutex:
        motion = "open_box_" + open_id
        string_queue.put(motion)


def CloseBox(com_a: serial, close_id: str):
    with mutex:
        motion = "close_box_" + close_id
        string_queue.put(motion)


def GetDH():
    with mutex:
        string_queue.put('DH')
    # com_a.write(b"DH")
    # for _ in range(0, 3):
    #     back_code: str = com_a.readline().decode('utf-8').strip()
    #     print("back: ", back_code)
    #     if " " in back_code:
    #         com_a.write(b"ok")
    #         return back_code
    # return ""


def AudioOpen(com_b: serial, flag):
    print("监听串口启动")
    while not flag.is_set():
        back_code = com_b.readline().decode('utf-8').strip()
        # print(back_code)
        if back_code == "":
            continue
        with mutex:
            motion = back_code
            string_queue.put(motion)


def PopQueue(com_a: serial):
    with mutex_2:
        print("queue: [", end="")
        for i in range(0, string_queue.qsize()):
            print(string_queue.queue[i], end=", ")
        print("]")
        if string_queue.empty():
            print('empty')
            return
        queue_front: str = string_queue.get()
        binary_front: bytes = queue_front.encode('utf-8').strip()
        com_a.write(binary_front)
        cnt = 3
        while cnt != 0:
            cnt -= 1
            if "_box_" in queue_front:  # 开关箱子
                back_code = com_a.readline().decode('utf-8').strip()
                print(back_code)
                if back_code == queue_front + "_ok":
                    break
            elif queue_front == 'DH':
                back_code: str = com_a.readline().decode('utf-8').strip()
                # print("back_code: ", back_code)
                if " " in back_code:
                    return back_code
        return ""


def ComSleep(index):
    time.sleep(index)


