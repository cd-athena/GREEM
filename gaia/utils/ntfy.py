
import os
from gaia.utils.cli_parser import CLI_PARSER
from gaia.utils.configuration_classes import NtfyConfig


USE_NTFY: bool = CLI_PARSER.is_ntfy_enabled()

ntfy_config: NtfyConfig = NtfyConfig(base_url="<ip-address>")

def send_ntfy(topic: str, message: str, print_message: bool = False) -> str:
    if not __valid_base_url():
        return ''
    if USE_NTFY:
        print(f'curl -d "{message}" {ntfy_config.base_url}/{topic}')
        os.system(f'curl -d "{message}" {ntfy_config.base_url}/{topic}')
    if print_message:
        print(message)
        
        
def __valid_base_url() -> bool:
    if ntfy_config.base_url == '<ip-address>':
        print('NTFY base url is not defined')
        return False
    
    return True


if __name__ == '__main__':
    print(ntfy_config)
    send_ntfy('encoding', 'hello from python')
