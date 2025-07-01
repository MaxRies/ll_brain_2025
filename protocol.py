import socket
import struct
import logging
from enum import Enum

# --- Logging Setup ---
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# --- Protocol Definitions (based on C++ enums and structs) ---

class EquipmentType(Enum):
    """
    Defines the types of equipment as per the C++ protocol.
    Values are integer representations of ASCII characters.
    """
    NONE = 48    # '0'
    ALL = 49     # '1'
    LIGHT = 50   # '2'
    CONTROL = 51 # '3'

class MessageType(Enum):
    """
    Defines the types of messages as per the C++ protocol.
    Values are integer representations of ASCII characters.
    """
    SUBSCRIBE = ord('0')
    SET = ord('1')
    SYNC = ord('2')
    PUSH = ord('3')
    STATUS = ord('4')

# --- Message Creation Functions ---

def create_subscribe_message(equipment_type: EquipmentType) -> bytes:
    """
    Creates a subscribeMessage packet.
    Format: messageType (char), equipmentType (char)
    Size: 2 bytes
    """
    packet = struct.pack('!cc',
                         chr(MessageType.SUBSCRIBE.value).encode('ascii'),
                         chr(equipment_type.value).encode('ascii'))
    if len(packet) != 2:
        raise ValueError(f"Subscribe message size mismatch: expected 2, got {len(packet)}")
    return packet

def create_setting_message(
    base_pattern: int, base_color: int, base_speed: int, base_brightness: int,
    front_pattern: int, front_color: int, front_speed: int, front_brightness: int,
    strobe_pattern: int, strobe_color: int, strobe_speed: int, strobe_brightness: int,
    main_dim: int, duty_cycle: int
) -> bytes:
    """
    Creates a settingMessage packet.
    All fields are char (1 byte).
    Size: 15 bytes
    """
    packet = struct.pack('!cccccccccccccc',
                         chr(MessageType.SET.value).encode('ascii'), # messageType
                         chr(base_pattern).encode('ascii'),
                         chr(base_color).encode('ascii'),
                         chr(base_speed).encode('ascii'),
                         chr(base_brightness).encode('ascii'),
                         chr(front_pattern).encode('ascii'),
                         chr(front_color).encode('ascii'),
                         chr(front_speed).encode('ascii'),
                         chr(front_brightness).encode('ascii'),
                         chr(strobe_pattern).encode('ascii'),
                         chr(strobe_color).encode('ascii'),
                         chr(strobe_speed).encode('ascii'),
                         chr(strobe_brightness).encode('ascii'),
                         chr(main_dim).encode('ascii'),
                         chr(duty_cycle).encode('ascii'))
    if len(packet) != 15:
        raise ValueError(f"Setting message size mismatch: expected 15, got {len(packet)}")
    return packet

def create_synchronising_message(
    direction: int, beat_period_millis: int, beat_distinctiveness: int
) -> bytes:
    """
    Creates a synchronisingMessage packet.
    Format: messageType (char), direction (char), beat_period_millis (uint16_t),
            beat_distinctiveness (uint8_t)
    Size: 5 bytes
    """
    packet = struct.pack('<ccHB',
                         chr(MessageType.SYNC.value).encode('ascii'), # messageType
                         chr(direction).encode('ascii'),
                         beat_period_millis,
                         beat_distinctiveness)
    if len(packet) != 5:
        raise ValueError(f"Synchronising message size mismatch: expected 5, got {len(packet)}")
    return packet

def create_pushing_message(
    pushing1: int, pushing2: int, pushing3: int, pushing4: int, pushing5: int, pushing6: int
) -> bytes:
    """
    Creates a pushingMessage packet.
    All fields are char (1 byte).
    Size: 7 bytes
    """
    packet = struct.pack('!ccccccc',
                         chr(MessageType.PUSH.value).encode('ascii'), # messageType
                         chr(pushing1).encode('ascii'),
                         chr(pushing2).encode('ascii'),
                         chr(pushing3).encode('ascii'),
                         chr(pushing4).encode('ascii'),
                         chr(pushing5).encode('ascii'),
                         chr(pushing6).encode('ascii'))
    if len(packet) != 7:
        raise ValueError(f"Pushing message size mismatch: expected 7, got {len(packet)}")
    return packet

def create_statusing_message(status: int) -> bytes:
    """
    Creates a statusingMessage packet.
    Format: messageType (char), status (char)
    Size: 2 bytes
    Note: The C++ constructor had a potential typo (SyncMessage instead of StatusMessage).
          This implementation uses StatusMessage.
    """
    packet = struct.pack('!cc',
                         chr(MessageType.STATUS.value).encode('ascii'), # messageType
                         chr(status).encode('ascii'))
    if len(packet) != 2:
        raise ValueError(f"Statusing message size mismatch: expected 2, got {len(packet)}")
    return packet

# --- UDP Sending Function ---

def send_udp_packet(ip_address: str, port: int, packet_data: bytes, is_broadcast: bool = False):
    """
    Sends a UDP packet to the specified IP address and port.
    If is_broadcast is True, enables SO_BROADCAST option on the socket.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            if is_broadcast:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                logger.debug("Enabled broadcast for socket.")

            sock.sendto(packet_data, (ip_address, port))
            logger.info(f"Sent {len(packet_data)} bytes to {ip_address}:{port}")
            logger.debug(f"Packet (hex): {packet_data.hex()}")
    except socket.error as e:
        logger.error(f"Error sending UDP packet: {e}")

def send_beat_message(beat_period, beat_distinctiveness=50):
    BROADCAST_IP = "192.168.0.255"
    TARGET_PORT = 1103
    sync_packet = create_synchronising_message(
        direction=ord('0'), # This will send the ASCII character '0'
        beat_period_millis=beat_period,
        beat_distinctiveness=beat_distinctiveness
    )
    send_udp_packet(BROADCAST_IP, TARGET_PORT, sync_packet, is_broadcast=True)


# --- Example Usage ---

if __name__ == "__main__":
    LOCAL_NETWORK_PREFIX = "192.168.0" # <<< IMPORTANT: Change this to your actual network prefix
    BROADCAST_IP = f"{LOCAL_NETWORK_PREFIX}.255"
    TARGET_PORT = 1103      # Choose an appropriate port

    logger.info(f"--- Sending UDP packets to Broadcast Address: {BROADCAST_IP}:{TARGET_PORT} ---")

    # Example 3: Send a SynchronisingMessage with direction '0' to broadcast
    logger.info("Creating and sending SynchronisingMessage with direction '0' to broadcast...")
    sync_packet = create_synchronising_message(
        direction=ord('0'), # This will send the ASCII character '0'
        beat_period_millis=500,
        beat_distinctiveness=50
    )
    send_udp_packet(BROADCAST_IP, TARGET_PORT, sync_packet, is_broadcast=True)

    logger.info("--- UDP broadcast packet sending complete ---")
    logger.info("To test, you can use a simple UDP listener (e.g., `netcat -ul 12345`)")
    logger.info("or a Python UDP server script to receive these packets on all devices in your network.")