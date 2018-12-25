import socket
import multiprocessing
import threading
import re


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
        response = "HTTP/1.1 404 NOT FOUND\r\n"
        response += "\r\n"
        response += "the page is not found"
        client_socket.send(response.encode("utf-8"))
    else:
        response = "HTTP/1.1 200 OK\r\n"  # 这里的\r\n是作为换行
        response += "\r\n"  # 请求头和请求体之间的空格
        html_content = f.read()
        f.close()
        # 发送response_header
        client_socket.send(response.encode("utf-8"))
        # 发送response_body
        client_socket.send(html_content)

    client_socket.close()  # 套接字关闭


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

        # p = multiprocessing.Process(target=service_client, args=(client_socket,))
        # p.start()
        t = threading.Thread(target=service_client, args=(client_socket, ))
        t.start()

        """实现多进程完成web
        子进程的资源不是共享的
        子进程开始执行后，对于client_socket这个套接字对象的fd会变成两个，
        如果在主进程里面client_socket不进行关闭，
        在子进程的client_socket关闭后，指向的fd并没有消失，
        客户端就不知道4此挥手结束，
        那么客户端就会一直等待"""
        # client_socket.close()

        # service_client(client_socket)

    tcp_server_socket.close()

if __name__ == '__main__':
    main()