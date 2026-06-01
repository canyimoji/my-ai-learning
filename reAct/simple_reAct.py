"""
最简单、可见的 ReAct Agent 演示
不依赖任何框架，只使用 requests 调用 LLM
任务：查询北京天气（模拟工具），然后给出穿衣建议
"""

import requests
import json
import re

# ===== 配置（请替换为您的真实 Key）=====
API_KEY = "sk-zguekcvranjeujzvdibsjfidciqaqplthohwjmixfstiodlq"
URL = "https://api.siliconflow.cn/v1/chat/completions"
MODEL = "deepseek-ai/DeepSeek-V3"
# =====================================

def mock_weather(city):
    """模拟天气工具，返回固定数据"""
    if city == "北京":
        return "25°C，晴天"
    else:
        return "未知城市"

def add_number(a,b):
    # python是强类型语言字符串相加会拼接 正则提取的是字符   增加参数清洗类型转换
    # 将参数转化为int 或 flat
    # 异常兜底 转换失败如接收到abc，则保持原样或报错
    return float(a) + float(b)

# 工具映射表
# 可以通过tools[func_name](arg)调用
tools = {
    "get_weather": mock_weather,
    "add_number": add_number
}

# ※※※※※※※   系统提示：强制 Agent 输出指定格式 告诉ai有哪些工具  什么时候结束
SYSTEM_PROMPT = """你是一个ReAct Agent。你需要通过“思考-行动-观察”循环来完成任务。
每次输出必须严格遵循以下格式：
Thought: 你当前的想法。
Action: 你要执行的动作，格式为 函数名(参数) ，例如 get_weather(北京)
当你已经有足够信息回答用户时，输出：
Action: FINISH(最终答案)

可用的函数：
- get_weather(城市名)：返回该城市的天气。
- add_number(a, b): 返回两个数字的和。

现在开始！"""

# 调用LLM
def call_llm(messages):
    """调用 LLM，返回回复文本"""
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0  # temperature 0 最稳定  0.7 有点创意  1.0 很发散
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(URL, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"API错误: {resp.text}")
    return resp.json()["choices"][0]["message"]["content"]

#提取正则
def extract_action(llm_output):
    """从 LLM 输出中提取 Action 行把:部分后面提取出来"""
    match = re.search(r"Action:\s*(.+)", llm_output)
    if match:
        #匹配正则第一个()内容
        return match.group(1).strip()
    return None

#解析Action字符串
def parse_action(action_str):
    """解析 Action 字符串，如 'get_weather(北京)' -> (函数名, 参数)"""
    match = re.match(r"(\w+)\((.*)\)", action_str)
    # w+ 抓函数名  \w找字母数字下划线 +至少一个 ()抓起来 即抓连续字母或数字   
    # .*抓参数      \(\) 抓括号 .任意字符   *任意多个  
    if match:
        # 单个参数
        # func_name = match.group(1)
        # args = match.group(2).split(',')[0].strip()
        # 多个参数
        func_name = match.group(1)
        args_str = match.group(2)
        args = [arg.strip() for arg in args_str.split(',')]
        return func_name, args 
    return None, None

def run_agent(user_question, max_steps=5, max_parse_retries=2):  #max_steps=5防止死循环 max_parse_retries=2 解析重试最大次数为2
    """初始消息设置身份和内容"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_question}
    ]
    
    step = 0
    while step < max_steps:
        step += 1
        print(f"\n--- 第 {step} 步 ---")
        
        # 调用 LLM
        llm_output = call_llm(messages)
        print("LLM 输出:\n", llm_output)
        
        # 提取 Action
        action_str = extract_action(llm_output)
        if not action_str:
            print("未找到 Action，终止")
            break
        
        # 如果 Action 是 FINISH
        if action_str.startswith("FINISH"):
            # 提取 FINISH 括号内的最终答案
            final_match = re.search(r"FINISH\((.*)\)", action_str)
            final_answer = final_match.group(1) if final_match else "任务完成"
            print(f"最终答案: {final_answer}")
            return final_answer
        
        # 解析 Action 函数调用
        func_name, arg = parse_action(action_str)
        # not in如果func_name 不在tools这个字典里   即判断某个东西不在某个容器时
        if func_name not in tools:
            print(f"未知函数: {func_name}，终止")
            break
        
        # 执行工具
        print(f"执行工具: {func_name}({arg})")
        # *args把列表或元组拆开变成一个个独立参数传给函数   arg是单个参数  *arg解码[1,1]  1,1分别作为参数
        observation = tools[func_name](*arg)
        print(f"观察结果: {observation}")
        
        # 将 LLM 输出和观察结果加入到消息历史
        messages.append({"role": "assistant", "content": llm_output})
        # 将工具执行结果伪装成用户消息
        messages.append({"role": "user", "content": f"Observation: {observation}"})
    
    print("达到最大步数，未完成")
    return None

if __name__ == "__main__":
    question = input('请输入:')
    # question = "北京天气怎么样？如果晴天就建议出门，否则建议带伞。"
    print(f"用户问题: {question}")
    run_agent(question)