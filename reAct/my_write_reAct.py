import requests
import re
from typing import Dict, Callable, Any, List, Optional
# 

API_KEY = "sk-zguekcvranjeujzvdibsjfidciqaqplthohwjmixfstiodlq"
URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL = "deepseek-ai/DeepSeek-V3"

def call_llm (msg):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    playload = {
        'model': MODEL,
        'messages':msg,
        "temperature": 0
    }
    resp = requests.post(URL, json = playload, headers = headers, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"API 错误: {resp.text}")
    return resp.json()["choices"][0]["message"]["content"]

def mock_weather(city):
    if city == "北京":
        return "25度，晴天"
    return "未知"

# 工具映射
tools = {"get_weather": mock_weather}

# 定义system提示词
system_prompt = """你是 Agent。格式要求：
Thought: 你的思考
Action: 函数名(参数)

可用函数：get_weather(城市名)
当最终答案准备好时，Action: FINISH(答案)"""

messages = [
    {"role":"system", "content": system_prompt},
    {"role":"user", "content": "北京天气怎么样？"}  
]

max_steps = 3    #循环最大次数
max_retries = 2   # 解析失败时最多重试次数
for step in range(max_steps):
    print(f"\n--- 步骤 {step+1} ---")
    llm_output = call_llm(messages)
    action_str = None
    # 重试机制
    for retry in range(max_retries):
        # 提取 Action
        action_match = re.search(r"Action:\s*(.+)", llm_output)
        if action_match:
            action_str = action_match.group(1).strip()
            break # 解析成功，跳出重试循环
        # 解析失败，要求 LLM 重新生成
        print(f"  解析失败，重试 {retry+1}/{max_retries}")
        # 把失败信息加入到消息队列  之后重试即在启动agent
        messages.append({"role": "assistant", "content": llm_output})
        messages.append({"role": "user", "content": "格式错误！请确保输出包含 'Action:' 行，格式如：Action: get_weather(北京)。不要输出多余解释。"})
        llm_output = call_llm(messages)    
        break
    # 如果for循环正常结束没被break 就会执行else代码 如果被break打断就不执行   for else组合
    else: # 所有重试都失败
        print("无法解析 Action，退出")
        break

    if action_str is None :
        print('无法获得有效action, 退出程序')
        break

    # 处理 FINISH
    if action_str.startswith("FINISH"):
        final_match = re.search(r"FINISH\((.*)\)", action_str)
        print("final_match:",final_match)
        answer = final_match.group(1) if final_match else "完成"
        print("最终答案:", answer)
        break

     # 解析函数调用，例如 get_weather(北京)
    func_match = re.match(r"(\w+)\((.*)\)", action_str)
    print("final_match:",func_match)
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
    try:
        result = tools[func_name](*args)
    except Exception as e:
        result = f"工具执行错误: {e}"
    print(f"工具 {func_name}{args} 返回: {result}")

    # 将 LLM 的输出和观察结果加入消息历史
    messages.append({"role": "assistant", "content": llm_output})
    messages.append({"role": "user", "content": f"Observation: {result}"})