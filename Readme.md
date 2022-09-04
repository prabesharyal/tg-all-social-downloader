# Youtube Downloader For Telegram

An python bot to download Public Videos/Audios from Links in Telegram Chat/Channel.
>- ___Note___: It not only works for Youtube, but support a lot of sites. It downloads in webm format from youtube. Basically this downloader is intended to be used in telegram chats and in telegram video player.
>- Audio can be downloaded from audio-only sites like sound cloud.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/prabesharyal/tg-all-social-downloader/tree/main/)
# Table of Contents
 1. [Introduction](#1)
    1. [About Bot](#1.1)
	2. [Working Principle](#1.2)
 3. [Knowing All Variables](#2)
	4. [BOT Token](#2.1)
 5. [Requirements](#3)
    1. [Python](#3.1)
		1. [PIPs](#3.1.1)
 6. [Deploy](#4)
 7. [License](#lic)


# Read this throughly before deploying the bot: <a name="1"></a>

## What is this bot about?<a name="1.1"></a>
This bot is make specifically for one purpose. That is to monitor Telegram Groups and Chats and download Public Videos/Audios from Links in Telegram Chat/Channel.

## How does this bot work?<a name="1.2"></a>
> **This bot works in various steps as :**
> - It listens for new messages in your Telegram Groups.
> - Scans for messages with URL Regex.
> - Tries to download that link
> - If download is done, it sends to telegram.
> - Deletes that specific message only.

<br>

# Get Variables <a name="2"></a>

## Bot Token <a name="2.1"></a>
- You can get Telegram Bot Token `BOT_TOKEN` from [BotFather](https://t.me/@BotFather) bot on telegram.

<br>
# Required Softwares and Languages <a name="3"></a>

## Python <a name="3.1"></a>
> Download Python From here :
> - [Python Latest Version](https://www.python.org/downloads/)
>
> *While installing, tick install **path / environment** variables whatever is given*

### Python Snippets <a name="3.1.1"></a>
- **Install required python modules using commands below:**
> - `pip install python-telegram-bot --pre`
> - `pip install yt-dlp`

- __Install all above modules using :__
> - `pip install -r requirements.txt`


# Deploying the bot <a name="4"></a>

## Deploying Locally
- Install Python, PIPs using [above methods](#3)
- Download all files in this repo.
- Replace variables at the top of `main.py` file with your ones, removing `os.environ.get('BOT_TOKEN')` commands.

> Type ***any one*** of the following command on terminal to run bot:
> - `py main.py`
> - `python main.py`
> - `python3 main.py`

## Deploying to HEROKU :
Press the button below or at the top of this readme and insert necessary [environment variables](#environ) and you're done.
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/prabesharyal/tg-all-social-downloader/tree/main/)

# License <a name="lic"></a>
> Distributed Under GPL or MIT License by [@PrabeshAryalNP](https://t.me/prabesharyalnp) on [social](https://twitter.com/prabesharyalnp) or [@PrabeshAryal](https://github.com/prabesharyal) on code sites.

<!-- Bored to write Readme previously, Now fine haha. -->