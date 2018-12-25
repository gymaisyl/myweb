import socket


def service_client(client_socket):
    # 处理客户端请求

    # 1.接收浏览器发送的请求 GET /HTTP/1.1
    request = client_socket.recv(1024)
    print(request)

    # 返回 http格式数据给浏览器

    response = "HTTP/1.1 200 OK\r\n"  # 这里的\r\n是作为换行
    response += "\r\n"  # 请求头和请求体之间的空格
    response += "Time is Short, I need Python"

    client_socket.send(response.encode("utf-8"))

    client_socket.close()  # 套接字关闭


def main():
    # 创建套接字
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 端口绑定
    tcp_server_socket.bind(("", 7890))  # 绑定本地ip和自定义端口

    # 设置为被动连接模式
    tcp_server_socket.listen(128)

    while True:
        """等待客户端连接"""
        client_socket, client_addr = tcp_server_socket.accept()

        service_client(client_socket)

    tcp_server_socket.close()

if __name__ == '__main__':
    main()