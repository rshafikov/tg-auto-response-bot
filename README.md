# Telegram Auto-Response Bot

This is a simple Telegram bot built with Telethon that listens for specific messages in a Telegram chat and responds automatically.

## Features
- Listens for messages matching a specific regex **pattern**, **user** and **chat**.
- Responds with a `+` to matched messages (you can change it).
- Can be configured via `.env` file.
- Supports listing chats and viewing the bot's profile.
- Runs for a specified duration before disconnecting automatically.

## Requirements
- [Docker](https://www.docker.com/get-started/)

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/rshafikov/tg-auto-response-bot
   cd telegram-auto-response-bot
   ```

2. Create a `.env` file in the project root with the following content:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   ```
   - `API_ID` and `API_HASH` are obtained from [my.telegram.org](https://my.telegram.org/).

3. You might want to find chat IDs or user IDs for your task, to do that change command field in `compose.yaml`:
    ```shell
    uv run main.py --me --my-chats
    ```
4. Finally, run docker compose and authenticate yourself:
    ```shell
    docker compose up -d
    docker attach tg-bot
    # write phone number of your telegram account
    # and provide 2FA code
    ```

5. After you receive desired information finish your `.env` file
    ```
    CHAT_IDS=123456789,-987654321,  # comma required
    USER_IDS=111111111,222222222,  # comma required
    PATTERN=.*приглашаю.*поиграть.*волейбол.*  # write the pattern as is 
    ```
   - `CHAT_IDS` is a comma-separated list of chat IDs to monitor.
   - `USER_IDS` is a comma-separated list of user IDs whose messages to track.
   - `PATTERN` is a regex pattern for filtering messages.

## Usage

Change `command` field in `compose.yaml` file in accordance with your task.

- **Show your profile:**
  ```sh
   uv run main.py --me
  ```

- **List available chats:**
  ```sh
  uv run main.py --my-chats
  ```

- **Run the bot:**
  ```sh
  uv run main.py --run --timer 15
  ```
  - `--run` starts message tracking.
  - `--timer` sets the bot to disconnect after the given number of seconds (default: 15 seconds).
  
- **Run the bot with a custom pattern:**
  ```sh
  python bot.py --run --pattern ".*сегодня.*тренировка.*"
  ```

## How It Works
1. The bot connects to Telegram using the provided API credentials.
2. It listens for new messages in the specified chats from the specified users.
3. If a message matches the defined regex pattern, the bot replies with `+`.
4. The bot automatically disconnects after the specified duration.

## Logs & Debugging
- Logging is enabled with warnings by default.
- Modify the `logging.basicConfig` level in `bot.py` to adjust verbosity.
