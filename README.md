# ICal-checker

This GitHub repository is simply a discord bot (to be hosted) coded in python.

## What does it do?

It checks with a given ICal link if there are any events coming up.

## How to use it?

1. Launch the bot a first time, it will create a `config.json` file.
2. Fill the `config.json` file with your bot token and the ICal link you want to check.
3. Launch the bot a second time and that's it!

## Prerequisites

- Python 3.9 or higher
- discord.py 2.0 or higher
- icalendar
- pytz
- requests
- json
- asyncio
- sys
- datetime
- os

Here is a command to install all the prerequisites:

```bash	
pip install discord.py icalendar pytz requests json asyncio sys datetime os
```

And here is a command to update all the prerequisites:

```bash
pip install -U discord.py icalendar pytz requests json asyncio sys datetime os
```

## How to launch the bot?

```bash
python main.py
```

## How to launch the bot in background?

Make a service file in `/etc/systemd/system/` with the following content:

```bash
[Unit]
Description=ICal-checker
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/main.py
WorkingDirectory=/path/to/main.py
Restart=always
User=your_user

[Install]
WantedBy=multi-user.target
```

Reload the daemon:

```bash
sudo systemctl daemon-reload
```

Start the service:

```bash
sudo systemctl start ical-checker.service
```

Enable the service:

```bash
sudo systemctl enable ical-checker.service
```

## How to stop the bot?

```bash
sudo systemctl stop ical-checker.service
```

## How to restart the bot?

```bash
sudo systemctl restart ical-checker.service
```

## How to check the status of the bot?

```bash
sudo systemctl status ical-checker.service
```

## How to launch the bot with a screen?

```bash
screen -S ical-checker
python main.py
```

## How to detach the screen?

```bash
Ctrl + A + D
```

## How to reattach the screen?

```bash
screen -r ical-checker
```

## How to kill the screen?

```bash
screen -X -S ical-checker quit
```

## How to kill the bot?

```bash
Ctrl + C
```

And that's it! You can now use the bot!

## How to contribute?

You can contribute by forking the repository and making a pull request.
