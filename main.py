import time
import requests
import random
from mnemonic import Mnemonic
from eth_account import Account
from eth_account.messages import encode_defunct
from colorama import Fore, init
import cloudscraper


init()

Account.enable_unaudited_hdwallet_features()
inviter_code = "GUyUCsrHBYlVaoI"
TASKS = {
    "join_twitter": "f8a1de65-613d-4500-85e9-f7c572af3248",
    "like_twitter": "34ec5840-3820-4bdd-b065-66a127dd1930",
    "join_telegram": "2daf1a21-6c69-49f0-8c5c-4bca2f3c4e40",
    "create_wallet": "df2a34a4-05a9-4bde-856a-7f5b8768889a",
}


def create_wallet_and_login():
    mnemo = Mnemonic("english")
    mnemonic = mnemo.generate(strength=128)
    account = Account.from_mnemonic(mnemonic)
    timestamp = int(time.time() * 1000)
    message = f"MESSAGE_ETHEREUM_{timestamp}:{timestamp}"
    encoded_message = encode_defunct(text=message)
    signed = account.sign_message(encoded_message)
    signature = signed.signature.hex()
    address = account.address

    url = (
        f"https://back.aidapp.com/user-auth/login"
        f"?strategy=WALLET&chainType=EVM"
        f"&address={address}"
        f"&token={message}"
        f"&signature=0x{signature}"
        f"&inviter={inviter_code}"
    )

    headers = {
        "accept": "*/*",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        access_token = response_json.get("tokens", {}).get("access_token")
        if access_token:
            return access_token, mnemonic, address
        else:
            return "Error: No access_token found", mnemonic, address
    else:
        return f"Error: {response.status_code} - {response.text}", mnemonic, address

def join_campaign(access_token):
    url = "https://back.aidapp.com/questing/campaign/6b963d81-a8e9-4046-b14f-8454bc3e6eb2/join"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {access_token}",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 201:
        print("JOIn Success:")
    else:
        print("Error:", response.status_code, response.text)


def perform_task_and_claim_rewards(access_token, task_id, task_name):
    task_url = f"https://back.aidapp.com/questing/mission-activity/{task_id}"
    reward_url = f"https://back.aidapp.com/questing/mission-reward/{task_id}"

    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {access_token}",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    }

    # Melakukan task
    print(f"{Fore.GREEN}\nPerforming task: {task_name}...{Fore.RESET}")
    task_response = requests.post(task_url, headers=headers)

    if task_response.status_code == 201:
        print(f"{Fore.GREEN}Task {task_name} completed successfully.{Fore.RESET}")
    else:
        print(f"{Fore.RED}Error performing task: {task_response.status_code}{Fore.RESET}")
        return False

    delay = random.uniform(2, 5)
    print(f"{Fore.YELLOW}Waiting {delay:.2f} seconds before claiming reward...{Fore.RESET}")
    time.sleep(delay)

    print(f"{Fore.GREEN}Claiming reward for: {task_name}...{Fore.RESET}")
    reward_response = requests.post(reward_url, headers=headers)

    if reward_response.status_code == 201:
        print(f"{Fore.GREEN}Reward for task {task_name} claimed successfully.{Fore.RESET}")
        print(f"{Fore.CYAN}Reward Response Text: {reward_response.text}{Fore.RESET}")
        return True
    else:
        print(f"{Fore.RED}Error claiming reward: {reward_response.status_code}{Fore.RESET}")
        return False
    
def save_mnemonic_to_file(mnemonic):
    with open("mnemonic.txt", "a") as file:
        file.write(mnemonic + "\n")
    print(f"{Fore.YELLOW}Mnemonic saved to mnemonic.txt{Fore.RESET}")


if __name__ == "__main__":
    while True:
        access_token, mnemonic, address = create_wallet_and_login()
        print(f"{Fore.BLUE}Generated wallet with address: {address}{Fore.RESET}")
        join_campaign(access_token)

        if "Error" not in access_token:
            print(f"{Fore.CYAN}Using wallet address: {address}{Fore.RESET}")
            all_tasks_completed = True
            any_reward_claimed = False

            for task_name, task_id in TASKS.items():
                if not perform_task_and_claim_rewards(access_token, task_id, task_name):
                    all_tasks_completed = False
                else:
                    any_reward_claimed = True

                time.sleep(random.randint(10, 20))

            if all_tasks_completed and any_reward_claimed:
                save_mnemonic_to_file(mnemonic)
            else:
                print(
                    f"{Fore.RED}Error: Not all tasks were successful or no rewards were claimed. Mnemonic not saved.{Fore.RESET}")
            print(
                f"{Fore.GREEN}All tasks completed for this account. Moving to the next one...\n{Fore.RESET}")
        else:
            print(
                f"{Fore.RED}Login failed. Could not retrieve access token.{Fore.RESET}")
            break
