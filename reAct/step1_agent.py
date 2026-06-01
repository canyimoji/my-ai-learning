'''
相对于step0来说 step1加入了加入 Thought 和 Action
'''
import requests
import re

API_KEY = "你的Key"
URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL = "deepseek-ai/DeepSeek-V3"

def call_llm(messages):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": messages, "temperature": 0}
    resp = requests.post(URL, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"API 错误: {resp.text}")
    return resp.json()["choices"][0]["message"]["content"]

# 消息历史
messages = [
    {"role": "system", "content": "你是一个 ReAct Agent。每次输出格式：\nThought: 你的想法\nAction: 函数名(参数)\n当可以回答用户时，Action: FINISH(最终答案)"},
    {"role": "user", "content": "请输出一个 Thought 和 Action，Action 为 FINISH(测试通过)"}
]

reply = call_llm(messages)
print("LLM 输出:\n", reply)

# 提取 Action
action_match = re.search(r"Action:\s*(.+)", reply)
if action_match:
    action_line = action_match.group(1).strip()
    print("提取到的 Action:", action_line)
else:
    print("未找到 Action")