class Text:
    HEADER = [{"text": "~~~~~~ ", "color": "light_purple"}, {"text": "G.U.D. ", "color": "gold", "bold": True},
              {"text": "MCLink", "color": "gold"}, {"text": " ~~~~~~", "color": "light_purple"},
              {"text": "\n "}]

    SETUP = [{"text": "To join the mc server you need to authenticate your mc account by verifying your Chalmers "
                      "student email.\n\nStart by typing the following (replacing CID with your CID):\n",
              "color": "white"}, {"text": "/register", "color": "gray"}, {"text": " CID@student.chalmers.se",
                                                                          "color": "aqua"}]

    LOGIN_VERIFIED = [{"text": "You are already verified. To join the game connect to: ", "color": "green"},
                      {"text": "mc.chs.se", "color": "gold",
                       "clickEvent": {"action": "copy_to_clipboard", "value": "mc.chs.se"},
                       "hoverEvent": {"action": "show_text",
                                      "value": {"text": "Click to copy address", "color": "aqua"}}}, {"text": "\n\n"},
                      {"text": "You can unregister from the server list anytime with:", "color": "gray"}, {"text": "\n"},
                      {"text": "/unregister", "color": "aqua"}]

    MC_LINK = {"text": "MCLink"}
    LOOK_AT_CHAT = {"text": "Look at chat for instructions", "bold": True}

    SEND_TO_MAIN = {"text": "Sending you to the server", "bold": True}

    VALIDATION_MAIL = {"text": "A validation mail have been sent your mailbox, the mail includes "
                               "a command you need to run here to complete the validation"}

    UNKNOWN_ERROR = {"text": "Unknown error!", "color": "red"}

    INVALID_EMAIL = [{"text": "Invalid email, it needs to end with '", "color": "red"},
                     {"text": "@student.chalmers.se", "color": "yellow"},
                     {"text": "'.", "color": "red"}]

    VERIFICATION_DONE = [{"text": "\n"}, {"text": "Verification completed, to join the game connect to: ", "color": "green"},
                         {"text": "mc.chs.se", "color": "gold",
                          "clickEvent": {"action": "copy_to_clipboard", "value": "mc.chs.se"},
                          "hoverEvent": {"action": "show_text",
                                         "value": {"text": "Click to copy address", "color": "aqua"}}}, {"text": "\n\n"},
                         {"text": "You can unregister from the server list anytime with:", "color": "gray"}, {"text": "\n"},
                         {"text": "/unregister", "color": "aqua"}]

    ALREADY_VERIFIED = {"text": "You are already verified.", "color": "yellow"}

    INVALID_VERIFY_CODE = {"text": "Invalid verification code.", "color": "red"}

    INVALID_VERIFY_COMMAND = {"text": "Invalid verification command.", "color": "red"}

    UNREGISTERED = [{"text": "\n"}, {"text": "Unregistered from the list!", "color": "green"}, {"text": "\n\n"},
                    {"text": "To re register enter (replacing CID with your CID):", "color": "white"}, {"text": "\n"},
                    {"text": "/register", "color": "gray"}, {"text": " CID@student.chalmers.se", "color": "aqua"}]

    JOIN_INVALID = {"text": "You need to register before you can run this command!", "color": "red"}

    JOIN_VALID = {"text": "Sending you to the server!", "color": "green"}

    UNKNOWN_COMMAND = {"text": "Unknown command!", "color": "red"}

    HELP = [{"text": "\n\n"}, {"text": "Help:", "color": "gold"}, {"text": "\n"},
            {"text": "/register", "color": "aqua"}, {"text": " <email>", "color": "yellow"},
            {"text": " - Register you chalmers student email with this commands.",
             "color": "gray"}, {"text": "\n"}, {"text": "/verify", "color": "aqua"},
            {"text": " <token>", "color": "yellow"},
            {"text": " - Finishes the linking with a token acquired from a mail sent to you.",
             "color": "gray"}, {"text": "\n"}, {"text": "/unregister", "color": "aqua"}, {
                "text": "- Unregister from the server list, won't be able to login until"
                        "you register again.",
                "color": "gray"}, {"text": "\n"}, {"text": "/help", "color": "aqua"},
            {"text": " - Shows this list.", "color": "gray"}]

    MOTD = "\u00a76G.U.D.\u00a7a MCLink\u00a7r\u00a7k \u258a\u00a7b 1.15.2\u00a7r\n\u00a77Chalmers Studentk\u00e5r"

    COMMANDS = {
        "type": "root",
        "children": {
            "register": {
                "type": "literal",
                "children": {
                    "email": {
                        "type": "argument",
                        "children": {},
                        "redirect": None,
                        "executable": True,
                        "name": "email",
                        "parser": "brigadier:string",
                        "properties": {
                            "behavior": 2
                        },
                        "suggestions": "minecraft:ask_server",
                    }
                },
                "executable": False,
                "redirect": None,
                "name": "register",
                "suggestions": None,
            },
            "verify": {
                "type": "literal",
                "children": {
                    "token": {
                        "type": "argument",
                        "children": {},
                        "redirect": None,
                        "executable": True,
                        "name": "token",
                        "parser": "brigadier:string",
                        "properties": {
                            "behavior": 2
                        },
                        "suggestions": None,
                    }
                },
                "executable": False,
                "redirect": None,
                "name": "verify",
                "suggestions": None,
            },
            "unregister": {
                "type": "literal",
                "children": {},
                "redirect": None,
                "executable": True,
                "name": "unregister",
                "suggestions": None,
            },
            "help": {
                "type": "literal",
                "children": {},
                "redirect": None,
                "executable": True,
                "name": "help",
                "suggestions": None,
            },
        },
        "executable": False,
        "redirect": None,
        "name": None,
        "suggestions": None,
    }
