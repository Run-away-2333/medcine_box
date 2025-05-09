# -*- coding: UTF-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import json


def SMTP_Server(email: str, medicine_name: str, num: int):
    with open("./config.json") as json_file:  # 配置文件
        init_config = json.load(json_file)
    sender = init_config['smtp']['sender']
    receivers = [email]
    password = init_config['smtp']['varify']  # 替换为QQ邮箱生成的授权码

    # 邮件内容
    message = MIMEText(f'请您在两个小时内及时服用{medicine_name}, 一次{num}粒/包', 'plain', 'utf-8')

    # 使用formataddr规范头部格式（自动处理RFC2047编码）
    message['From'] = formataddr(("智能药盒", sender))  # 格式：编码后的别名 <真实邮箱>
    message['To'] = formataddr(("用药", receivers[0]))

    # 主题设置
    message['Subject'] = '用药提醒'  # 简单主题可直接赋值

    try:
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as smtpObj:
            smtpObj.login(sender, password)
            smtpObj.sendmail(sender, receivers, message.as_string())
            smtpObj.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"发送失败: {str(e)}")


if __name__ == '__main__':
    # SMTP_Server('674060542@qq.com', "左氟氧沙星", 3, "12:00-14:00")
    print()
