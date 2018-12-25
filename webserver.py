import socket
import multiprocessing
import threading
import re

import gevent
from gevent import monkey


monkey.patch_all()


def service_client(client_socket):
    # 处理客户端请求

    # 1.接收浏览器发送的请求 GET /HTTP/1.1
    request = client_socket.recv(1024).decode()
    print(request)

    request_lines = request.splitlines()

    # 获取请求的内容
    ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
    file_name = ""
    if ret:
        file_name = ret.group(1)
        if file_name == "/":
            file_name = "/index.html"

    # 返回 http格式数据给浏览器

    # 针对请求的内容打开对应的文件，有就打开并返回，没有的话，就需要返回404页面
    try:
        f = open("./" + file_name, "rb")
    except:
        response_body = "the page is not found"
        response_body = response_body.encode("utf-8")
        response_header = "HTTP/1.1 404 not found\r\n"
        response_header += "Content-Length: %d\r\n" % (len(response_body))
        response_header += "\r\n"

        # 发送response_header
        response = response_header.encode("utf-8") + response_body
        # 发送response_body
        client_socket.send(response)

    else:
        html_content = f.read()
        f.close()
        response_body = html_content

        response_header = "HTTP/1.1 200 OK\r\n"  # 这里的\r\n是作为换行
        # 告诉浏览器response_body的长度
        response_header += "Content-Length: %d\r\n" % (len(response_body))
        response_header += "\r\n"  # 请求头和请求体之间的空格

        # 发送response_header
        response = response_header.encode("utf-8") + response_body
        # 发送response_body
        client_socket.send(response)

    # client_socket.close()  # 套接字关闭


def main():
    # 创建套接字
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 避免服务器主动关闭导致的端口占用
    tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 端口绑定
    tcp_server_socket.bind(("", 7890))  # 绑定本地ip和自定义端口

    # 设置为被动连接模式
    tcp_server_socket.listen(128)

    while True:
        """等待客户端连接"""
        client_socket, client_addr = tcp_server_socket.accept()

        gevent.spawn(service_client, client_socket)

    tcp_server_socket.close()

if __name__ == '__main__':
    main()