import requests
import re
import json

# 配置（请替换您的 Key）
API_KEY = "你的硅基流动API_Key"
URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL = "deepseek-ai/DeepSeek-V3"

def call_llm(prompt):
    """发送 prompt 到 LLM，返回回复文本"""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }
    resp = requests.post(URL, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"API 错误: {resp.text}")
    return resp.json()["choices"][0]["message"]["content"]

# 给 LLM 的提示
prompt = """你是一个 Agent。请严格按照以下格式输出：
Action: FINISH(Hello, world!)

不要输出其他内容。"""

reply = call_llm(prompt)
print("LLM 回复:", reply)

# 提取 FINISH 括号内的内容
match = re.search(r"FINISH\((.*)\)", reply)
if match:
    final = match.group(1)
    print("最终答案:", final)
else:
    print("提取失败")