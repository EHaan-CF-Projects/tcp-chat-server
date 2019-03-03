#! /usr/local/bin/python3
from client import ChatClient
import threading
import socket
import sys


PORT = 6783


class ChatServer(threading.Thread):
    def __init__(self, port, host='localhost'):
        super().__init__(daemon=True)
        self.port = port
        self.host = host
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP
        )
        self.client_pool = []

        try:
            self.server.bind((self.host, self.port))
        except socket.error:
            print('Bind failed {}'.format(socket.error))
            sys.exit()

        self.server.listen(10)


    def parser(self, id, nick, conn, message):
        if message.decode().startswith('@'):
            data = message.decode().split(maxsplit=1)

            if data[0] == '@quit':
                conn.sendall(b'You have left the chat.')
                reply = nick.encode() + b'has left the channel.\n'
                [c.conn.sendall(reply)
                    for c in self.client_pool if len(self.client_pool)]
                self.client_pool = [c for c in self.client_pool if c.id != id]
                conn.close()

            elif data[0] == '@list':
                for c in self.client_pool:
                    name = c.nick
                    reply = name.encode() + b'\n'
                    [c.conn.sendall(reply) for c in self.client_pool]

            elif data[0] == '@nickname':
                nickname = data[1].strip()
                for c in self.client_pool:
                    if c.id == id:
                        c.nick = nickname
                    conn.sendall(b'Your new nickname is ' + nickname.encode())
            elif data[0] == '@dm':
                dm_parts = data[1].split(maxsplit=1)
                recipient_name = dm_parts[0]
                message = dm_parts[1].encode()

                found = False
                for client in self.client_pool:
                    if client.nick == recipient_name:
                        client.conn.sendall(message)
                        found = True


                if not found:
                    conn.sendall(b'Check recipient name')

            else:
                conn.sendall(b'Invalid command. Please try again.\n')

        else:
            reply = nick.encode() + b': ' + message
            [c.conn.sendall(reply)
             for c in self.client_pool if len(self.client_pool)]

    def run_thread(self, id, nick, conn, addr):
        print('{} connected with {}:{}'.format(nick, addr[0], str(addr[1])))
        try:
            while True:
                data = conn.recv(4096)
                self.parser(id, nick, conn, data)
        except (ConnectionResetError, BrokenPipeError, OSError):
            conn.close()

    def run(self):
        print('Server running on {}'.format(PORT))
        while True:
            conn, addr = self.server.accept()
            client = ChatClient(conn, addr)
            self.client_pool.append(client)
            threading.Thread(
                target=self.run_thread,
                args=(client.id, client.nick, client.conn, client.addr),
                daemon=True
            ).start()

    def exit(self):
        self.server.close()


if __name__ == '__main__':
    server = ChatServer(PORT)
    try:
        server.run()
    except KeyboardInterrupt:
        [c.conn.close() for c in server.client_pool if len(server.client_pool)]
        server.exit()
