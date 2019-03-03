  def parser(self, id, nick, conn, message):
        if message.decode().startswith('@'):
            data = message.decode().split(maxsplit=1)

            if data[0] == '@quit':
                conn.sendall(b'You have left the chat.')
                reply = nick.encode() + b'has left the channel.\n'
                [c.conn.sendall(reply) for c in self.client_pool if len(self.client_pool)]
                self.client_pool = [c for c in self.client_pool if c.id != id]
                conn.close()

            elif data[0] == '@list':
                for c in self.client_pool:
                    name = c.nick
                    reply = name.encode() + b'\n'
                    [c.conn.sendall(reply) for c in self.client_pool if len(self.client_pool)]

            elif data[0] == '@nickname':
                nickname = data[1].strip()
                for i in self.client_pool:
                    if i.id == id:
                        i.nick = nickname
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
                        conn.sendall(b'sending message')

                if not found:
                    conn.sendall(b'Check recipient name')

            else:
                conn.sendall(b'Invalid command. Please try again.\n')

        else:
            reply = nick.encode() + b': ' + message
            [c.conn.sendall(reply) for c in self.client_pool if len(self.client_pool)]
