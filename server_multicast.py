import socket
import threading
import json

SERVER_PORT = 5000
BROADCAST_IP = '192.168.0.255'
ROOMS = {}  # {room_name: (multicast_ip, port)}
MULTICAST_BASE = '224.1.1.'
MULTICAST_PORT = 6000

def send_broadcast_update():
    msg = json.dumps({'type': 'update', 'rooms': ROOMS}).encode()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(msg, (BROADCAST_IP, SERVER_PORT))
    s.close()

def udp_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', SERVER_PORT))
    while True:
        data, addr = s.recvfrom(1024)
        try:
            req = json.loads(data.decode())
            if req.get('type') == 'list':
                resp = json.dumps({'type': 'list', 'rooms': ROOMS}).encode()
                s.sendto(resp, addr)
        except Exception:
            continue

def server_console():
    next_room_id = 1
    while True:
        cmd = input("Comenzi: add <room>, del <room>, list\n> ")
        if cmd.startswith("add"):
            _, room = cmd.split()
            if room not in ROOMS:
                multicast_ip = MULTICAST_BASE + str(next_room_id)
                ROOMS[room] = (multicast_ip, MULTICAST_PORT)
                print(f"Room '{room}' created at {multicast_ip}:{MULTICAST_PORT}")
                send_broadcast_update()
                next_room_id += 1
        elif cmd.startswith("del"):
            _, room = cmd.split()
            if room in ROOMS:
                del ROOMS[room]
                print(f"Room '{room}' deleted.")
                send_broadcast_update()
        elif cmd == "list":
            print("Rooms:", ROOMS)
        else:
            print("Comenzi: add <room>, del <room>, list")

if __name__ == "__main__":
    threading.Thread(target=udp_listener, daemon=True).start()
    server_console()