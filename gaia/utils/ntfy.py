
import os

NTFY_BASE_URL: str = '3.76.6.7'

TOPICS: list[str] = [
    'encoding'
]


def send_ntfy(topic: str, message: str) -> str:
    if topic in TOPICS:
        os.system(f'curl -d "{message}" {NTFY_BASE_URL}/{topic}')


if __name__ == '__main__':
    send_ntfy('encoding', 'hello from python')
