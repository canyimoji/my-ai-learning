import requests

API_KEY = "sk-zguekcvranjeujzvdibsjfidciqaqplthohwjmixfstiodlq"  # 替换成你的真实密钥  目前用的硅基流动
URL = "https://api.deepseek.com/v1/chat/completions"

print("===== 我的第一个 AI 聊天机器人（） =====")
print("输入问题，输入 exit 退出")

while True:
        user_msg = input("请问你想问我什么: ") # 获取用户输入
        if user_msg.lower() == 'exit': # 如果用户输入 exit 就退出循环
            print("再见！")
            break

        # 构造请求数据，符合OpenAI API的格式
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": user_msg
                },
                {"role": "system", "content": "你是一个乐于助人的助手。"},
            ]
        }
        headers = {
                "Authorization": f"Bearer {API_KEY}", # 如果API需要Bearer Token认证
                "Content-Type": "application/json" # 如果API需要指定内容类型
        }

        response = requests.post(URL, json=payload, headers=headers) # 发送POST请求到deepseek的API服务器，传递请求数据和请求头
        if response.status_code == 200: # 如果响应状态码是200，表示请求成功
            data = response.json() # 解析响应数据为JSON对象
            ai_reply = data['choices'][0]['message']['content'] # 从响应数据中提取AI的回复内容
            print(f"AI: {ai_reply}") # 打印AI的回复
        else:
            print(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}") # 如果请求失败，打印错误信息