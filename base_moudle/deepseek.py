# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="*****", base_url="https://api.deepseek.com")

with open('LLM_txt/MedicineAndDoctor.txt', 'r', encoding='utf-8') as config:
    person = config.read()


def ChatDeepSeekR1():
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": f"{person}"},
            {"role": "user", "content": "阿司匹林"},
        ],
        stream=False
    )

    # print(response.choices[0].message.content)
    src_response = response.choices[0].message.content
    fix_response = src_response.replace('*', '').replace('-', '').replace('\n\n', '\n')
    return response.choices[0].message.content


def str_de():
    str_1 = '''**阿司匹林药用信息整理：**

    1. **对症治疗：**  
       - **短期**：缓解轻至中度疼痛（头痛、牙痛、肌肉痛等）、退烧、抗炎（如关节炎）。  
       - **长期（低剂量）**：预防心脑血管疾病（心梗、中风），抑制血小板聚集。
    
    2. **服用时间建议：**  
       - **普通片剂**：饭后服用，减少胃刺激。  
       - **肠溶片**：建议饭前空腹服用（胃酸较少时更易快速进入肠道溶解）。
    
    3. **饮食注意事项：**  
       - 避免酒精（增加胃出血风险）。  
       - 减少辛辣、油腻食物（保护胃黏膜）。  
       - 长期服用者可适当补充维生素K（如菠菜、西兰花），但若联用华法林需遵医嘱。
    
    4. **其他建议：**  
       - 出现黑便、呕血等立即就医（警惕消化道出血）。  
       - 儿童/青少年病毒感染期间禁用（防瑞氏综合征风险）。
    
    ---
    
    **概括：** 阿司匹林可短期止痛退烧或长期预防血栓。普通片饭后服，肠溶片饭前服；忌酒精辛辣，长期服用注意补维生素K。警惕胃出血风险。'''

    str2 = str_1.replace('*', '')
    str3 = str2.replace('-', '')
    str4 = str3.replace('\n\n', '\n')
    print(str4)

if __name__ == '__main__':
    # ChatDeepSeekR1()
    str_de()
