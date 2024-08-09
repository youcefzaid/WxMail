![Alt text](/screenshot.png "WxMail screenshot")

# WxMail

Bulk email access checker tool, searches through a list of email accounts for specific keywords.

## Features

- Multi-threaded email checking
- Customizable search criteria (subject, sender, body)
- Date filtering
- Random shuffling of input list

## Requirements

- Python 3.6+
- Required packages: `imaplib`, `termcolor`

## Setup

1. Install required packages:
   ```
   pip install termcolor
   ```

2. Create a `config.json` file with email provider settings:
   ```json
   [
     {
       "Domains": ["example.com"],
       "Hostname": "imap.example.com",
       "Port": 993
     }
   ]
   ```

3. Prepare a combolist file with email:password pairs, one per line.

## Usage
`python main.py combolist.txt --threads 20 --search-in subject --keyword "important" --since 01-Jan-2024`

Arguments:
- `combolist`: Path to the combolist file
- `--threads`: Number of threads (default: 20)
- `--search-in`: Where to search (subject, from, body)
- `--keyword`: Keyword to search for
- `--since`: Minimum date (format: DD-Mon-YYYY)

Results are saved in `found.txt`.

## Disclaimer

Ensure you have permission to access the email accounts. Use responsibly and ethically.