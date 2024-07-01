import requests
import json
import threading
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from colorama import init, Fore
import re
# Initialize colorama
init(autoreset=True)

totalCoin = 0
referralsCount = 0
init_total_coin = 0
refresh_time = 2 * 3600 + 50 * 60  
percentage_use_for_upgrade = 0
percentage_use_for_boost = 0

priority = ["Markets"]
# Example of priority upgrade option
# priority = [] # for all upgrade section
# priority = None  # for no upgrade
# priority = ["Specials"] # for single priority upgrade
# priority = ["Specials","Markets"] # for multiple priority upgrade, will will the order of list
# priority = "YouTube 25 Million" # for single priority upgrade, will keep upgrading until it reach max level



def request_api(path, prefix="clicker", json_data={}):
    try:
        r = requests.post(
            f"https://api.hamsterkombat.io/{prefix}/{path}", headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer 1719687415235aHv0gr7u8IZpAeOGhHN5cblG56p5FjEDBaB44dhF8kOP3Dg05fEkNruAf2NwBJUv7106749488"
            },
            json=json_data
        )
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Request error: {e}")
        return None


def update_init_total_coin():
    global init_total_coin, totalCoin
    init_total_coin = totalCoin
    upgrade()


def clicker():
    global totalCoin
    res = request_api("tap", json_data={
        "count": 999999999, "availableTaps": 99999999999999999999, "timestamp": int(datetime.now().timestamp())})
    totalCoin = res["clickerUser"]["balanceCoins"]
    print(f"{Fore.YELLOW}Earned {totalCoin}🪙")
    upgrade()


def daily():
    chiper = "MINER"
    print(f"{Fore.YELLOW}Fetching Daily Cipher Code")
    html_content = requests.get(
        "https://givemetools.com/hamster-kombat-cipher").text
    match = re.search(
        r'<p class="[^"]*"><strong>[^<]*<\/strong>([^<]*)<\/p>', html_content)
    # Extract the matched text if found
    if match:
        chiper = match.group(1)
        print(f"{Fore.GREEN}Extracted Cipher Code: {chiper}")
    else:
        print(f"{Fore.RED}Failed to Fetch Code")

    res = request_api("claim-daily-cipher", json_data={"cipher": chiper})
    if res.get("dailyCipher"):
        print(f"{Fore.GREEN}Claimed Daily Cipher")
    else:
        print(f"{Fore.RED}Cipher code was wrong or already claimed")
    task = request_api("check-task", json_data={"taskId": "streak_days"})
    if task["task"].get("isCompleted"):
        print(f"{Fore.GREEN}Claimed Daily")
    else:
        print(f"{Fore.RED}Daily Streak was already claimed")

    # Looking for todays combo
    html_content_combo = requests.get(
        "https://givemetools.com/hamster-kombat-combo").text
    print(f"{Fore.YELLOW} Fetching Combo Code")
    match = re.search(
        r'<ol>\s*<li><strong>(.*?)<\/strong><\/li>\s*<li><strong>(.*?)<\/strong><\/li>\s*<li><strong>(.*?)<\/strong><\/li>\s*<\/ol>', html_content, re.DOTALL)
    if match:
        extracted_texts = match.groups()
        print(f"{Fore.GREEN}Extracted Combo: {extracted_texts}")
    else:
        print("No Combo was found!")


def boost():
    global init_total_coin, percentage_use_for_boost
    budget = init_total_coin * percentage_use_for_boost / 100
    spent = 0
    res = request_api("boosts-for-buy")["boostsForBuy"]
    base_upgrade = res[-1]["level"] + 1
    for boost in res:
        if boost["id"] not in ["BoostFullAvailableTaps","BoostEarnPerTap"] and boost["price"] <= budget and boost["level"] < base_upgrade:
            request_api(
                "buy-boost", json_data={"boostId": boost["id"], "timestamp": int(datetime.now().timestamp())})
            print(f"{Fore.MAGENTA}Upgraded boost {boost['id']} to level {boost['level']+1}")
            budget -= boost["price"]
            spent += boost["price"]
    return budget - spent


def buy_upgrade(item, upgrade_list):
    if not item["isAvailable"] or item["isExpired"] or not isAvailable(item["condition"], upgrade_list):
        return 0
    request_api(
        "buy-upgrade", json_data={"upgradeId": item["id"], "timestamp": int(datetime.now().timestamp())})
    print(f"{Fore.MAGENTA}Updated {item['name']} to level {item['level']+1}")
    return item["price"]


def isAvailable(condition, upgrade_list):
    global referralsCount
    if not condition:
        return True
    if condition["_type"] == "ByUpgrade":
        return any(item["id"] == condition["upgradeId"] and item["level"] >= condition["level"] for item in upgrade_list)
    if condition["_type"] in ["ReferralCount", "MoreReferralsCount"]:
        return referralsCount >= condition["referralCount"]
    return True


def upgrade():
    global totalCoin, init_total_coin, percentage_use_for_upgrade
    if(totalCoin < init_total_coin):
        return
    upgrade_list = sorted(request_api("upgrades-for-buy")
                          ["upgradesForBuy"], key=lambda x: x["level"])
    budget = init_total_coin * percentage_use_for_upgrade / 100
    base_upgrade = upgrade_list[-1]["level"] + 1
    spent = boost()
    if isinstance(priority, str):
        for item in upgrade_list:
            if item["name"] == priority and item["price"] <= budget:
                spent += buy_upgrade(item, upgrade_list)
                break
    elif isinstance(priority, list):
        upgrades_by_section = defaultdict(list)
        for item in upgrade_list:
            upgrades_by_section[item['section']].append(item)
        for section in priority:
            for item in upgrades_by_section[section]:
                if item["price"] <= budget:
                    spent += buy_upgrade(item, upgrade_list)
    totalCoin -= spent


def setInterval(interval, function):
    def wrapper():
        setInterval(interval, function)
        function()
    threading.Timer(interval, wrapper).start()


def main():
    global totalCoin, init_total_coin
    logged_as = request_api(prefix="auth", path="me-telegram")
    print(f"Logged as: {Fore.GREEN}{logged_as['telegramUser']['firstName']} {logged_as['telegramUser']['lastName']}")
    sync = request_api("sync")
    request_api("add-referral",json_data={
        "friendUserId": 6825195625
    })
    clickerUser = sync['clickerUser']
    totalCoin = clickerUser['balanceCoins']
    init_total_coin = totalCoin
    print(f"Level: {Fore.YELLOW}{clickerUser['level']} ⬆️")
    print(f"Total Coin: {Fore.CYAN}{totalCoin}🪙")
    print(f"Earn per click: {Fore.MAGENTA}{clickerUser['earnPerTap']}🪙")
    print(f"Earn per Hour: {Fore.MAGENTA}{clickerUser['earnPassivePerHour']}🪙")
    print(f"maxTaps: {Fore.BLUE}{clickerUser['maxTaps']}⚡")
    if clickerUser.get('claimedCipherAt'):
        last_claimed_time = datetime.fromisoformat(clickerUser.get(
            'claimedCipherAt').replace('Z', '+00:00'))
        if last_claimed_time + timedelta(hours=12) < datetime.now(timezone.utc):
            print(f"{Fore.GREEN}Claiming Daily Cipher")
            daily()
        else:
            clicker()
            update_init_total_coin()
            print(f"{Fore.YELLOW}Daily Cipher already claimed")
    else:
        print(f"{Fore.GREEN}Claiming Daily Cipher")
        daily()
    setInterval(12 * 60 * 60, daily)
    setInterval(refresh_time, update_init_total_coin)
    setInterval(80, clicker)


main()
