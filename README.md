# CHS MCLink

This server is built on [barneygale/quarry][1], a Minecraft protocol library.

It has support to run behind [Velocity][2].

This server authenticates players, then spawns them in an empty world and does the bare minimum to keep them in-game.

When logged in the players can authenticate their Minecraft accounts by entering their student email into the `/register CID@student.chalmers.se` command.

## Requirements

- Python 3
- Supports MC 1.16.3+
- An instance of [gudchalmers/chs-mclink-backend][4] running
- Python [Virtualenv][3] (not really required but highly recommended)

## Setup

Edit the `mclink.ini` as needed for your setup.

The entries in the config are:

- `url` The url to the backend server that handles the database and emails, and is used by the server plugin to auth on login.
- `main_server` The server on Velocity to send the player when authentication is done. **Disabled for now as there were some issues**.
- `online` True if this server should verify the accounts logging in to the Minecraft servers. Need to be disabled to work behind `Velocity`.
- `velocity` True if working behind `Velocity`.
- `velocity_key` A shared key with `Velocity` auth internal messages through `HMAC` hashing. You can read more [here][5].
- `token` A shared key with the backend server for authentication.

Install all the libraries with the following:

```sh
pip install -r requirements.txt
```

Then to run the server you just need to run the following:

```sh
python mclink.py
```

### Long term

It's recommended to setup a auto run script like [systemd][6] for linux to auto run on startup and remove the requirement to have a shell open.

The following is an example `systemd` script:

```ini
[Unit]
Description=MCLink Python Service
After=multi-user.target

[Service]
Type=Simple

Restart=on-failure
RestartSec=1
WorkingDirectory=/path/to/this/folder
ExecStart=/path/to/this/folder/venv/bin/python /path/to/this/folder/mclink.py

[Install]
WantedBy=multi-user.target
```

## License

[MIT][7]

[1]: https://github.com/barneygale/quarry
[2]: https://velocitypowered.com/
[3]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments
[4]: https://github.com/gudchalmers/chs-mclink-backend
[5]: https://velocitypowered.com/wiki/users/forwarding/
[6]: https://en.wikipedia.org/wiki/Systemd
[7]: https://choosealicense.com/licenses/mit/
