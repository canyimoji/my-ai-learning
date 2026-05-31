# 结构化输出 让ai返回json格式的数据 方便我们提取信息
# re是正则

# 1、配置区
import requests
import json
import re
API_KEY = "sk-zguekcvranjeujzvdibsjfidciqaqplthohwjmixfstiodlq"  # 替换成你的真实密钥  目前用的硅基流动
URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL_NAME = "deepseek-ai/DeepSeek-V3" 

# ========== 辅助函数: 从文本中提取 JSON ==========
# 函数定义: extract_json(text)
# 参数 text: AI 返回的原始字符串（可能包含 Markdown 代码块或额外文字）
# 返回值: 一个 Python 字典（如果成功提取并解析 JSON），否则返回 None
# 为什么需要这个函数: AI 有时不听话，会在 JSON 外面加上 ```json 或说明文字，
# 导致 json.loads() 直接失败。这个函数会尝试多种方法“清理”文本，尽力提取出 JSON。
def extract_json(text):
    text = text.strip()
    try: 
        return json.loads(text)
    except:
        pass
    pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()  # 提取代码块里的内容
        try:
            return json.loads(candidate)    # 尝试解析
        except:
            pass
    
    start = text.find('{')
    if start == -1:
        start = text.find('[')  # 如果没有 {，就找 [
    if start != -1:
        # 使用一个简单的栈来匹配大括号/方括号的结束位置
        stack = []
        for i, ch in enumerate(text[start:], start):
            if ch in '{[':
                stack.append(ch)
            elif ch in '}]':
                if not stack:
                    break
                top = stack.pop()
                # 检查括号是否匹配（{ 必须和 } 匹配，[ 必须和 ] 匹配）
                if (top == '{' and ch != '}') or (top == '[' and ch != ']'):
                    break
            if not stack:
                    # 找到了完整的 JSON 字符串
                    candidate = text[start:i+1]
                    try:
                        return json.loads(candidate)
                    except:
                        break
    # 所有方法都失败，返回 None
    return None

    
# 2、输入数据
text = "我叫李四，今年30岁，现在住在上海。"

# 3、构造系统指令+用户问题 即构造prompt 让AI知道我们要它做什么 以及要处理什么数据
system_prompt = "你是一个信息提取助手，请从用户输入中提取姓名、年龄、城市，并以JSON格式返回。只返回JSON，不要有其他解释。"
user_prompt = f"请从以下文本中提取信息：{text}"

# 4、组装请求体1234
payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user","content": text},
                {"role": "system", "content": system_prompt}
            ]
        }

# 5、请求头
headers = {
            "Authorization": f"Bearer {API_KEY}", # 如果API需要Bearer Token认证
            "Content-Type": "application/json" # 如果API需要指定内容类型
        }

# 6、发送请求
response = requests.post(URL, json=payload, headers=headers)

# 7、处理响应
if response.status_code == 200: # 如果响应状态码是200，表示请求成功
    ai_reply = response.json()['choices'][0]['message']['content'] # 从响应数据中提取AI的回复内容
    print(f"AI: {ai_reply}") # 打印AI的回复
    # 调用我们之前定义的 extract_json 函数，尝试提取 JSON
    extracted_data = extract_json(ai_reply)
    if extracted_data is not None:
        print("\n=== 成功提取 JSON ===")
        print("姓名:", extracted_data.get("name"))
        print("年龄:", extracted_data.get("age"))
        print("城市:", extracted_data.get("city"))
    else:
        print("\n=== 无法提取有效的 JSON ===")
        print("请检查 AI 返回的内容，或调整系统提示词。")
else:
    print(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}") # 如果请求失败，打印错误信息


