import socket
import struct
import threading
import json
import sys

SERVER_PORT = 5000
BROADCAST_IP = '192.168.0.255'

def discover_rooms():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(2)
    msg = json.dumps({'type': 'list'}).encode()
    s.sendto(msg, (BROADCAST_IP, SERVER_PORT))
    try:
        data, addr = s.recvfrom(4096)
        resp = json.loads(data.decode())
        return resp.get('rooms', {})
    except Exception as e:
        return {}
    finally:
        s.close()

def listen_multicast(multicast_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    mreq = struct.pack("4sl", socket.inet_aton(multicast_ip), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    while True:
        data, addr = sock.recvfrom(1024)
        print(f"[{addr[0]}] {data.decode()}")

def main():
    current_room = None
    current_info = None
    listener_thread = None

    while True:
        cmd = input()
        if cmd == "list":
            rooms = discover_rooms()
            print("Rooms:", rooms)
        elif cmd.startswith("join"):
            _, room = cmd.split(maxsplit=1)
            rooms = discover_rooms()
            if room in rooms:
                if listener_thread and listener_thread.is_alive():
                    print("Ieșit din camera anterioară.")
                current_info = rooms[room]
                current_room = room
                print(f"Joined {room} ({current_info[0]}:{current_info[1]})")
                listener_thread = threading.Thread(target=listen_multicast, args=(current_info[0], current_info[1]), daemon=True)
                listener_thread.start()
            else:
                print("Camera inexistentă.")
        elif cmd == "leave":
            current_room = None
            current_info = None
            print("Ai părăsit camera.")
        elif cmd.startswith("send"):
            if not current_info:
                print("Nu ești într-o cameră.")
                continue
            _, text = cmd.split(' ', 1)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            s.sendto(text.encode(), (current_info[0], current_info[1]))
            s.close()
        elif cmd == "exit":
            break
        else:
            print("Comandă necunoscută.")

if __name__ == "__main__":
    print("Comenzi: list, join <room>, leave, send <text>, exit\n> ")
    main()