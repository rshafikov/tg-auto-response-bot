import argparse
import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from dotenv import dotenv_values
from telethon import TelegramClient, events

logging.basicConfig(
    format='[%(levelname)s %(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)

logger = logging.getLogger(__name__)

DEFAULT_GAME_PATTERN = r".*приглашаю.*поиграть.*волейбол.*"
DEFAULT_TRAINING_PATTERN = r".*сегодня.*тренировка.*"


@dataclass(slots=True)
class ClientParams:
    chats: list[int]
    users: list[int]
    pattern: str


class TelegramBot:
    def __init__(self, api_id: int, api_hash: str) -> None:
        self.client = TelegramClient('tg_session', api_id, api_hash)

    async def add_event(self, chats: list, users: list, pattern: str) -> None:
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        event = events.NewMessage(
            incoming=True,
            chats=chats,
            from_users=users,
            pattern=pattern
        )
        self.client.add_event_handler(callback=self.send_plus, event=event)

    @staticmethod
    async def send_plus(event: events.NewMessage.Event) -> None:
        """Handle incoming messages."""
        await asyncio.sleep(1)
        await event.reply('+')
        print(f'Bot replied to:\n{event.message.stringify()}')

    async def show_profile(self) -> None:
        """Print the Telegram profile."""
        async with self.client:
            my_profile = await self.client.get_me()
            print(my_profile.stringify())

    async def list_chats(self) -> None:
        """List available chats."""
        async with self.client:
            async for dialog in self.client.iter_dialogs():
                if not dialog.name.lower().endswith('bot'):
                    print(f'chat {dialog.name!r} -> ID: {dialog.id}')

    async def run_bot(self, params) -> None:
        """Run the bot with the given pattern."""
        print('Starting bot...')
        async with self.client:
            await self.add_event(params.chats, params.users, params.pattern)
            print('Bot started:')
            await self.client.run_until_disconnected()

    async def disconnect_after(self, seconds: int) -> None:
        """Schedule the bot to disconnect after a given time."""
        await asyncio.sleep(seconds)
        print('Finishing bot...')
        await self.client.disconnect()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Telegram bot for handling chat events.")
    parser.add_argument('--me', action='store_true',
                        help='Show your Telegram profile')
    parser.add_argument('--my-chats', action='store_true',
                        help='List your chats to find usere you want to '
                             'track')
    parser.add_argument('--run', action='store_true',
                        help='Run chat tracking')
    parser.add_argument('--pattern', type=str,
                        help='Regex to filter messages',
                        default=None)
    parser.add_argument('--timer', type=int, default=15,
                        help='Time in minutes before disconnecting ('
                             'default: '
                             '15 seconds)')
    return parser.parse_args()


def load_env_variables() -> (int, str, ClientParams):
    env = dotenv_values(".env")
    api_id = int(env.get("API_ID"))
    api_hash = env.get("API_HASH")
    client_params = ClientParams(
        chats=[int(u) for u in env.get("CHAT_IDS", []).split(',')[:-1]],
        users=[int(u) for u in env.get("USER_IDS", []).split(',')[:-1]],
        pattern=env.get("PATTERN", DEFAULT_TRAINING_PATTERN)
    )

    if api_id is None or api_hash is None:
        raise RuntimeError('API_ID or API_HASH must be set in .env')

    print(f'Current tracking users: {client_params.users}')
    print(f'Current tracking chats: {client_params.chats}')
    print(f'Current pattern: "{client_params.pattern}"')
    return api_id, api_hash, client_params


async def main() -> None:
    args = parse_args()
    api_id, api_hash, params = load_env_variables()
    bot = TelegramBot(api_id, api_hash)

    tasks = []
    if args.me:
        tasks.append(bot.show_profile())
    if args.my_chats:
        tasks.append(bot.list_chats())
    if args.pattern:
        params.set('PATTERN', args.pattern)
    if args.run:
        tasks.append(bot.run_bot(params))
        if args.timer > 0:
            tasks.append(bot.disconnect_after(args.timer))

    if tasks:
        print(f'start: {datetime.now()}')
        print(f'end: {datetime.now() + timedelta(seconds=args.timer)}')
        await asyncio.gather(*tasks)

    else:
        print("No tasks to run. Use --help for options.")


def main_cmd():
    asyncio.run(main())


if __name__ == '__main__':
    main_cmd()
