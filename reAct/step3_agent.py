# 第四步：增加解析失败的重试
# 现在我们在提取 Action 失败时，不立即退出，而是要求 LLM 重新生成（最多重试 2 次）。
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

tools = {"get_weather": mock_weather}

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
max_retries = 2   # 解析失败时最多重试次数

for step in range(max_steps):
    print(f"\n--- 步骤 {step+1} ---")
    
    # ---- 获取 LLM 输出，带重试机制 ----
    llm_output = call_llm(messages)
    for retry in range(max_retries):
        # 尝试提取 Action
        action_match = re.search(r"Action:\s*(.+)", llm_output)
        if action_match:
            action_str = action_match.group(1).strip()
            break   # 解析成功，跳出重试循环
        # 解析失败，要求 LLM 重新生成
        print(f"  解析失败，重试 {retry+1}/{max_retries}")
        # 把错误的输出加入消息历史，并告诉 LLM 格式错误
        messages.append({"role": "assistant", "content": llm_output})
        messages.append({"role": "user", "content": "格式错误！请确保输出包含 'Action:' 行，格式如：Action: get_weather(北京)。不要输出多余解释。"})
        llm_output = call_llm(messages)
    else:
        # 所有重试都失败
        print("无法解析 Action，退出")
        break
    
    print("LLM 输出:\n", llm_output)
    print("Action:", action_str)
    
    # 处理 FINISH
    if action_str.startswith("FINISH"):
        final_match = re.search(r"FINISH\((.*)\)", action_str)
        answer = final_match.group(1) if final_match else "完成"
        print("最终答案:", answer)
        break
    
    # 解析函数调用
    func_match = re.match(r"(\w+)\((.*)\)", action_str)
    if not func_match:
        print("Action 格式错误（无法解析函数名和参数）")
        break
    func_name, args_str = func_match.group(1), func_match.group(2)
    args = [arg.strip().strip('"') for arg in args_str.split(',')] if args_str else []
    
    if func_name not in tools:
        print(f"未知函数 {func_name}")
        break
    
    result = tools[func_name](*args)
    print("工具返回:", result)
    
    # 更新消息历史
    messages.append({"role": "assistant", "content": llm_output})
    messages.append({"role": "user", "content": f"Observation: {result}"})

print("程序结束")