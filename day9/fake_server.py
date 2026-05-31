# from 模块名 import 函数名 只导入类，使用时直接函数名()，不需要模块名.函数名()了
# 只用模块里少量东西用from 模块名 import 函数1,函数2,函数3 
# 用到模块大量功能用import 模块名
# json.loads() 将JSON字符串解析为Python对象
# json.dumps() 将Python对象转换为JSON字符串

#  导入所需的模块 HTTPServer启动web服务,  BaseHTTPRequestHandler处理HTTP请求
#  import json整个模块用于处理JSON数据 ，使用时得json.函数名

from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# 处理请求的类，继承自BaseHTTPRequestHandler，重写了do_POST方法来处理POST请求
class FakeApiHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length']) # 获取请求体的长度
        body = json.loads(self.rfile.read(length)) # 读取请求体并解析为JSON对象
        print(f"收到请求: {body}") # 打印收到的请求内容
        user_msg = body['messages'][-1]['content'] # 获取用户最后一条消息
        reply = f"你说了: {user_msg}。我是假的AI，但流程正确" # 构造回复内容


    # 这里格式固定返响应
        self.send_response(200) # 告诉客户端状态码正常200
        self.send_header('Content-Type', 'application/json') #  告诉客户端回复内容是JSON格式
        self.end_headers() # 结束响应头的发送

    # 这里格式采用OpenAI的API格式 ,choices是一个列表，里面每个元素是一个字典，字典里有message字段，message字段又是一个字典，里面有content字段，content字段的值就是回复的内容
        response = {
            "choices": [
                {
                    "message": {
                        "content": reply
                    }
                }
            ]
        }

    # 发送响应数据
        self.wfile.write(json.dumps(response).encode('utf-8')) # 将响应数据转换为JSON字符串并编码为字节流发送给客户端

# 启动服务器
if __name__ == "__main__":
    server = HTTPServer(('127.0.0.1', 9191), FakeApiHandler) # 创建HTTP服务器，绑定地址和处理请求的类
    print('启动假API服务器，地址为 http://127.0.0.1:9191')
    server.serve_forever() # 创建HTTP服务器，绑定地址和处理请求的类，并开始监听请求
    print('保持这个终端运行不要关闭')

