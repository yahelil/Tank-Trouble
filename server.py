import socket
import threading

ending_symbol = b"~"


def receive_msg(sock):
    msg = b""
    while ending_symbol not in msg:
        msg += sock.recv(1)
    return msg.decode()[:-1]


def send_msg(sock, msg):
    sock.send(msg.encode() + ending_symbol)


class Server:
    def __init__(self, _host, _port, _number_of_clients):
        self.num_of_bullets = 0
        self.number_of_clients = _number_of_clients
        self.bullets_pos = []
        self.port = _port
        self.host = _host
        self.socket = socket.socket()
        self.is_blue = True
        self.tank_positions = ['0,0,0', '0,0,0']  # green_pos, blue_pos
        self.bullets = []

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(self.number_of_clients)

    def accept(self):
        return self.socket.accept()

    def main_loop(self):
        self.start()
        while 1:
            threading.Thread(target=self.pleasantly_talking, args=[self.accept()[0], self.is_blue], daemon=True).start()

    def pleasantly_talking(self, client, is_blue):
        if is_blue:
            self.is_blue = False
        client.send(b"B" if is_blue else b'G')
        while 1:
            self.tank_positions[int(is_blue)] = receive_msg(client)
            send_msg(client, str(self.tank_positions[int(not is_blue)]))
            received_num = int(receive_msg(client))
            if received_num- self.num_of_bullets > 0: # if a new bullet has been shot
                self.num_of_bullets = received_num
                self.bullets = receive_msg(client).split('|')[:-1]
                print(f'bullets: {self.bullets}')
                for x in self.bullets:
                    list = x.split(',')
                    list = [float(a) for a in list]
                    self.bullets_pos.append(tuple(list))
                    print(f'bullets_pos: {self.bullets_pos}')
                bullet_pos_msg = ''
                for bullet_pos in self.bullets_pos:
                    bullet_pos_msg += str(bullet_pos)[1:-1] + "|"
                    for i in range(len(self.tank_positions)):
                        tank = self.tank_positions[i].split(',')
                        if float(tank[0]) <= bullet_pos[0] <= float(tank[0]) + 35 and float(tank[1]) <= bullet_pos[1] <= float(tank[1]) + 31:
                            color = "Blue" if i else "Green"
                            print(f"collision with {color}")
                print(f"bullet_pos_msg: {bullet_pos_msg}")
                send_msg(client, bullet_pos_msg)
                self.bullets_pos.clear()


if __name__ == "__main__":
    app = Server("127.0.0.1", 80, 2)
    app.main_loop()




