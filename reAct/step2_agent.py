# 加入工具调用和循环（但先不处理解析失败）
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

def mock_weather(city):
    if city == "北京":
        return "25度，晴天"
    return "未知"

# 工具映射
tools = {"get_weather": mock_weather}

# 系统提示
system_prompt = """你是 Agent。格式要求：
Thought: 你的思考
Action: 函数名(参数)

可用函数：get_weather(城市名)
当最终答案准备好时，Action: FINISH(答案)"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "北京天气怎么样？"}
]

max_steps = 3
for step in range(max_steps):
    print(f"\n--- 步骤 {step+1} ---")
    llm_output = call_llm(messages)
    print("LLM 输出:", llm_output)

    # 提取 Action
    action_match = re.search(r"Action:\s*(.+)", llm_output)
    if not action_match:
        print("未找到 Action，结束")
        break
    action_str = action_match.group(1).strip()
    print("Action:", action_str)

    # 处理 FINISH
    if action_str.startswith("FINISH"):
        final_match = re.search(r"FINISH\((.*)\)", action_str)
        answer = final_match.group(1) if final_match else "完成"
        print("最终答案:", answer)
        break

    # 解析函数调用，例如 get_weather(北京)
    func_match = re.match(r"(\w+)\((.*)\)", action_str)
    if not func_match:
        print("Action 格式错误，结束")
        break
    func_name, args_str = func_match.group(1), func_match.group(2)
    # 简单解析参数（去除引号，按逗号分割）
    args = [arg.strip().strip('"') for arg in args_str.split(',')] if args_str else []

    if func_name not in tools:
        print(f"未知函数 {func_name}，结束")
        break

    # 执行工具
    result = tools[func_name](*args)
    print("工具返回:", result)

    # 将 LLM 的输出和观察结果加入消息历史
    messages.append({"role": "assistant", "content": llm_output})
    messages.append({"role": "user", "content": f"Observation: {result}"})

# 循环结束