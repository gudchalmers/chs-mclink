"""
This server authenticates players, then spawns them in an empty world and does
the bare minimum to keep them in-game.
"""
import configparser
import ipaddress
import json
import time
import hmac
import hashlib

import requests
from quarry.data.data_packs import data_packs, dimension_types
from quarry.net.server import ServerFactory, ServerProtocol
from quarry.types.chat import Message
from quarry.types.uuid import UUID
from twisted.internet import reactor
from random import seed
from random import randint

from text import Text

URL = "http://mclink.test/"
TOKEN = ""


class RegisterProtocol(ServerProtocol):

    def __init__(self, factory, remote_addr):
        super().__init__(factory, remote_addr)
        self.valid = False
        self.velocityQueryId = -1
        self.title_tick = None
        self.countdown = 10

    def packet_login_start(self, buff):
        if self.login_expecting != 0:
            raise ServerProtocol.ProtocolError("Out-of-order login")

        # Run normally if not velocity
        if not self.factory.config.getboolean('velocity'):
            ServerProtocol.packet_login_start(self, buff)

        else:
            self.velocityQueryId = randint(0, 320534324)
            self.send_packet("login_plugin_request",
                             self.buff_type.pack_varint(self.velocityQueryId),
                             self.buff_type.pack_string("velocity:player_info"),
                             self.buff_type.pack("B", 0))
            buff.discard()

    def packet_login_plugin_response(self, buff):
        # Check if we are using velocity and verify it's response and set data
        if self.factory.config.getboolean('velocity'):
            query_id = buff.unpack_varint()
            if query_id == self.velocityQueryId:
                if buff.unpack("?"):
                    signature = buff.read(32)
                    pos = buff.pos

                    data = buff.read()
                    buff.pos = pos

                    my_sign = hmac.new(bytes(self.factory.config.get('velocity_key'), 'utf-8'), data,
                                       hashlib.sha256).digest()
                    if hmac.compare_digest(my_sign, signature):
                        version = buff.unpack_varint()
                        if version != 1:
                            self.close("Unsupported forwarding version " + version + ", wanted 1")
                        else:
                            self.remote_addr = ipaddress.ip_address(buff.unpack_string())
                            self.uuid = buff.unpack_uuid()
                            self.display_name = buff.unpack_string()
                            self.login_expecting = None
                            self.display_name_confirmed = True
                            buff.discard()
                            self.player_joined()
                    else:
                        self.close("Unable to verify player details")
        buff.discard()

    def player_joined(self):
        # Call super. This switches us to "play" mode, marks the player as
        #   in-game, and does some logging.
        ServerProtocol.player_joined(self)

        # Build up fields for "Join Game" packet
        entity_id = 0
        max_players = 0
        hashed_seed = 42
        view_distance = 2
        game_mode = 3
        prev_game_mode = 3
        is_hardcore = False
        is_respawn_screen = True
        is_reduced_debug = True
        is_debug = False
        is_flat = True
        dimension_count = 1
        dimension_name = "mclink"
        dimension_type = dimension_types[754, "minecraft:the_end"]  # Hardcoded 1.16.4 protocol version
        data_pack = data_packs[754]  # Hardcoded 1.16.4 protocol version

        # Send "Join Game" packet
        self.send_packet(
            "join_game",
            self.buff_type.pack("i?BB", entity_id, is_hardcore, game_mode, prev_game_mode),
            self.buff_type.pack_varint(dimension_count),  # world count
            self.buff_type.pack_string(dimension_name),  # world name(s)
            self.buff_type.pack_nbt(data_pack),  # dimension registry
            self.buff_type.pack_nbt(dimension_type),  # dimension
            self.buff_type.pack_string(dimension_name),  # world name
            self.buff_type.pack("q", hashed_seed),  # hashed seed
            self.buff_type.pack_varint(max_players),  # max players (unused)
            self.buff_type.pack_varint(view_distance),  # view distance
            self.buff_type.pack("????", is_reduced_debug, is_respawn_screen, is_debug, is_flat))

        self.send_packet("plugin_message",
                         self.buff_type.pack_string("minecraft:brand"),
                         self.buff_type.pack_string("MCLink"))

        # Send "Player Position and Look" packet
        self.send_packet(
            "player_position_and_look",
            self.buff_type.pack("dddff?",
                                0,  # x
                                255,  # y
                                0,  # z
                                0,  # yaw
                                0,  # pitch
                                0b00000),  # flags
            self.buff_type.pack_varint(0))  # teleport id

        # Start sending "Keep Alive" packets
        self.ticker.add_loop(20, self.update_keep_alive)

        self.send_commands()
        self.send_packet("title",
                         self.buff_type.pack_varint(3),
                         self.buff_type.pack("iii", 10, 4200, 20))

        self.send_title()
        self.title_tick = self.ticker.add_loop(4200, self.send_title)

        msg = [Text.HEADER]
        d = send_request("check", {'uuid': self.uuid.to_hex()})

        if d['status'] == "denied":
            msg.append(Text.SETUP)
        else:
            self.valid = True
            msg.append(Text.LOGIN_VERIFIED)
        self.send_chat(Message(msg))

    def send_title(self):
        self.send_packet("title",
                         self.buff_type.pack_varint(0),
                         self.buff_type.pack_chat(Message(Text.MC_LINK)))

        self.send_packet("title",
                         self.buff_type.pack_varint(1),
                         self.buff_type.pack_chat(Message(Text.LOOK_AT_CHAT)))

    def update_keep_alive(self):
        # Send a "Keep Alive" packet
        self.send_packet("keep_alive", self.buff_type.pack('Q', 0))

    def packet_chat_message(self, buff):
        msg = buff.unpack_string()

        # Handle register commands, email is validated on backend too
        if msg.startswith("/register"):
            if msg.endswith("@student.chalmers.se"):
                d = send_request("register",
                                 {'email': msg.split(" ")[-1], 'uuid': self.uuid.to_hex(), 'name': self.display_name})
                if 'uuid' in d and d['uuid'][0] == "uuid_taken":
                    if self.valid:
                        self.send_chat(Message(Text.ALREADY_VERIFIED))
                    else:
                        self.send_chat(Message(Text.VALIDATION_MAIL))
                elif 'email' in d:
                    msg = []
                    for e in d['email']:
                        msg.append({"text": e, "color": "red"})
                    self.send_chat(Message(intersperse(msg, {"text": "\n "})))
                elif 'status' in d and d['status'] == "success":
                    self.send_chat(Message(Text.VALIDATION_MAIL))
                else:
                    self.send_chat(Message(Text.UNKNOWN_ERROR))
                    self.logger.error("Unknown error!")
                    self.logger.error(json.dumps(d, separators=(',', ':')))
            else:
                self.send_chat(Message(Text.INVALID_EMAIL))

        # Handle verify commands
        elif msg.startswith("/verify"):
            parts = msg.split(" ")
            if len(parts) == 2:
                d = send_request("verify", {'token': parts[1], 'uuid': self.uuid.to_hex()})
                if 'status' in d and d['status'] == 'success':
                    self.send_chat(Message(Text.VERIFICATION_DONE))
                    self.send_sound("entity.firework_rocket.launch")
                    time.sleep(0.2)
                    self.send_sound("entity.firework_rocket.blast")
                    self.send_sound("entity.firework_rocket.blast_far")
                    time.sleep(0.1)
                    self.send_sound("entity.firework_rocket.large_blast")
                    self.send_sound("entity.firework_rocket.twinkle_far")
                    time.sleep(0.2)
                    self.send_sound("ui.toast.challenge_complete")
                    self.valid = True
                    # self.start_send_to_main()
                elif 'status' in d and d['status'] == 'done':
                    self.send_chat(Message(Text.ALREADY_VERIFIED))
                else:
                    self.send_chat(Message(Text.INVALID_VERIFY_CODE))
            else:
                self.send_chat(Message(Text.INVALID_VERIFY_COMMAND))

        # Let the users unregister them self
        elif msg.startswith("/unregister"):
            send_request("unregister", {'uuid': self.uuid.to_hex()})
            self.send_chat(Message(Text.UNREGISTERED))
            self.valid = False

        # Show help for the commands
        elif msg.startswith("/help"):
            self.send_chat(Message(Text.HELP))

        else:
            self.send_chat(Message(Text.UNKNOWN_COMMAND))

    def send_chat(self, message, sender=None):
        if sender is None:
            sender = UUID(int=0)

        self.send_packet(
            "chat_message",
            self.buff_type.pack_chat(message),
            self.buff_type.pack('B', 1),
            self.buff_type.pack_uuid(sender)
        )

    def send_sound(self, name):
        self.send_packet("named_sound_effect",
                         self.buff_type.pack_string("minecraft:" + name),
                         self.buff_type.pack_varint(8),
                         self.buff_type.pack("iiiff", 0, 35555 * 8, 0, 1, 1))

    def packet_tab_complete(self, buff):
        transaction = buff.unpack_varint()
        text = buff.unpack_string()
        tmp = text.replace("/register", "")
        if len(tmp) > 1 and "@student.chalmers.se" not in tmp:
            # Abort if there is a space in the email
            if " " in tmp[1:]:
                return

            # Only add what is missing form the email
            addition = "@student.chalmers.se"
            if '@' in tmp:
                email = tmp[tmp.index('@'):]
                if email not in addition:
                    return
                addition = addition.replace(email, "")

            self.send_packet("tab_complete",
                             self.buff_type.pack_varint(transaction),
                             self.buff_type.pack_varint(len(text)),
                             self.buff_type.pack_varint(len(addition)),
                             self.buff_type.pack_varint(1),
                             self.buff_type.pack_string(addition),
                             self.buff_type.pack("?", False))

    # Complex structure for the commands to show
    def send_commands(self):
        self.send_packet("declare_commands", self.buff_type.pack_commands(Text.COMMANDS))

    def start_send_to_main(self):
        self.ticker.remove(self.title_tick)
        self.countdown = 10
        self.send_countdown_title()
        self.send_packet("title",
                         self.buff_type.pack_varint(1),
                         self.buff_type.pack_chat(Message(Text.SEND_TO_MAIN)))
        self.ticker.add_loop(20, self.send_countdown_title)

    def send_countdown_title(self):
        self.send_packet("title",
                         self.buff_type.pack_varint(0),
                         self.buff_type.pack_chat(Message({"text": self.countdown})))

        self.countdown -= 1
        if self.countdown <= 0:
            self.send_to_main()

    def send_to_main(self):
        server = self.factory.config.get('main_server').encode("utf-8")
        self.send_packet("plugin_message",
                         self.buff_type.pack_string("mclink:connect"),
                         self.buff_type.pack("H", len(server)) + server)


class RegisterFactory(ServerFactory):
    protocol = RegisterProtocol
    config = None
    motd = Text.MOTD
    max_players = 42
    icon_path = "./gud.png"


def main(argv):
    global URL, TOKEN
    # Parse options
    import argparse
    parsed = configparser.ConfigParser()
    parsed.read('mclink.ini')
    config = parsed['MCLink']

    URL = config.get('url', fallback='http://mclink.test/')
    TOKEN = config.get('token')
    if TOKEN is None:
        print("Need to include a token in the settings file")
        exit(-1)
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--host", default="127.0.0.1", help="address to listen on")
    parser.add_argument("-p", "--port", default=15556, type=int, help="port to listen on")
    parser.add_argument("--offline", action="store_true", help="offline server")
    args = parser.parse_args(argv)

    # Create factory
    factory = RegisterFactory()
    factory.config = config
    factory.online_mode = config.getboolean('online', fallback=(not args.offline))

    # Listen
    factory.listen(args.host, args.port)
    reactor.run()


def send_request(location, data):
    data['t'] = TOKEN
    r = requests.post(url=URL + location, data=data)
    print(r.text)
    return r.json()


def intersperse(lst, item):
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result


if __name__ == "__main__":
    import sys

    seed()
    main(sys.argv[1:])
