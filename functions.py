import requests
import subprocess, json
from typing import Union
from playwright.sync_api import sync_playwright
import re
import time
import functools
from email_validator import validate_email, EmailNotValidError
import smtplib
import random
from email.mime.text import MIMEText
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, date



# Define the scope (read-only access to Gmail)
#SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
def get_service():
    """Authenticate and build the Gmail API service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)
service = get_service()

def get_label_id(service, label_name):
    """Get the ID of a label by its name."""
    try:
        labels = service.users().labels().list(userId='me').execute().get('labels', [])
        for label in labels:
            if label['name'].lower() == label_name.lower():
                return label['id']
        print(f"Label '{label_name}' not found.")
        return None
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
def add_label_to_threads_by_email(service, email_address, label_id):
    """Add a label to all threads involving a specific email address."""
    try:
        query = f"from:{email_address} OR to:{email_address}"
        threads = service.users().threads().list(userId='me', q=query).execute().get('threads', [])
        for thread in threads:
            service.users().threads().modify(
                userId='me',
                id=thread['id'],
                body={'addLabelIds': [label_id]}
            ).execute()
        print(f"Added label to {len(threads)} threads involving {email_address}.")
    except HttpError as error:
        print(f"An error occurred: {error}")
def get_labels_on_threads_by_email(service, email_address):
    """Get all labels on messages within threads involving a specific email address."""
    try:
        query = f"from:{email_address} OR to:{email_address}"
        threads = service.users().threads().list(userId='me', q=query).execute().get('threads', [])
        label_set = set()
        for thread in threads:
            thread_details = service.users().threads().get(userId='me', id=thread['id']).execute()
            for msg in thread_details['messages']:
                label_set.update(msg.get('labelIds', []))
        labels = service.users().labels().list(userId='me').execute().get('labels', [])
        label_names = [label['name'] for label in labels if label['id'] in label_set]
        print(f"Labels on threads involving {email_address}: {', '.join(label_names)}")
        return label_names
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
        print(f"An error occurred: {error}")
def is_valid_text(text: str) -> bool:
    pattern = r'^[a-zA-Z0-9~`!@#$%^&*()_\-+={}\[\]:;"\'<>,.?/\\| ]+$'
    return bool(re.match(pattern, text))
def get_subscriber_count(channel_url):
    response = requests.get(channel_url)
    match = re.search(r"(\d+(\.\d+)?[KM]?)\s+subscribers", response.text)
    if match:
        num_str = match.group(1)
        if "K" in num_str:
            return int(float(num_str.replace("K", "")) * 1000)
        elif "M" in num_str:
            return int(float(num_str.replace("M", "")) * 1000000)
        else:
            return int(num_str)
    return None

def is_valid_email(mail_id: str) -> bool:
    """
    :param mail_id:
    :param deliverability_check:
    :return: bool
    """
    try:
        emailinfo = validate_email(mail_id, check_deliverability=False)
        return True
    except EmailNotValidError as e:
        return False

def time_it(func):
    """
    A decorator to check the time taken for execution for different functions
    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        #print(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result
    return wrapper
@time_it
def scrape_twitter_profile(twitter_profile_url):
    """
    Scrapes Twitter profile for gmail
    :param twitter_profile_url:
    :return:
    Dictionary containing the profile info
    """
    # Launch a headless browser with Playwright
    try:
        with sync_playwright() as p:
            # Start Chromium in headless mode (set headless=False to see the browser)
            browser = p.chromium.launch(headless=True)
            # Create a new page
            page = browser.new_page()
            # Navigate to the Twitter profile URL
            page.goto(f'{twitter_profile_url}')
            # Wait for the profile's display name element to load (up to 10 seconds)
            page.wait_for_selector('[data-testid="UserName"]', timeout=10000)

            # Extract display name
            display_name_element = page.query_selector('[data-testid="UserName"]')
            display_name = display_name_element.text_content().strip() if display_name_element else "Not found"

            # Extract bio
            bio_element = page.query_selector('[data-testid="UserDescription"]')
            bio = bio_element.text_content().strip() if bio_element else "No bio"

            # Extract join date (looks for a span containing "Joined")
            join_date_element = page.query_selector('span:has-text("Joined")')
            join_date = join_date_element.text_content().strip() if join_date_element else "Not found"

            # Extract followers count from the aria-label attribute
            followers_element = page.query_selector('[aria-label*="Followers"][role="link"]')
            followers = (followers_element.get_attribute('aria-label').split()[0]
                         if followers_element else "Not found")

            # Extract following count from the aria-label attribute
            following_element = page.query_selector('[aria-label*="Following"][role="link"]')
            following = (following_element.get_attribute('aria-label').split()[0]
                         if following_element else "Not found")

            # Close the browser
            browser.close()
    except:
        return {
            "display_name": "",
            "bio": "",
            "join_date": "",
            "followers": "",
            "following": ""
        }
    else:
            # Return the scraped data as a dictionary
            return {
                "display_name": display_name,
                "bio": bio,
                "join_date": join_date,
                "followers": followers,
                "following": following
            }

@time_it
def extract_emails(text: str):
    """
    Extracts emails form input text
    :param text:
    :return: list of found mails:
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?=\s|$)'
    return [str(email).lower() for email in re.findall(email_pattern, text) if not email.lower().endswith(('.jpg', '.png', '.gif', '.jpeg'))]

@time_it
def get_follower_count(client_id, access_token , user_id=None, user_login=None):
    """
    Returns follower count, requires either userId or user_login
    :param client_id:
    :param access_token:
    :param user_id:
    :param user_login:
    :return:
    """
    try:
        # Check if at least one parameter is provided
        if user_id is None and user_login is None:
            raise ValueError("You must provide either user_id or user_login")

        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {access_token}'
        }

        # If user_id is not provided, get it from user_login
        if user_id is None:
            users_url = 'https://api.twitch.tv/helix/users'
            users_params = {'login': user_login}
            users_response = requests.get(users_url, headers=headers, params=users_params)
            users_data = users_response.json()
            if not users_data['data']:
                return None  # User not found
            user_id = users_data['data'][0]['id']

        # Get the follower count using the user_id
        followers_url = 'https://api.twitch.tv/helix/channels/followers'
        followers_params = {'broadcaster_id': user_id, 'first': 1}
        followers_response = requests.get(followers_url, headers=headers, params=followers_params)
        if followers_response.status_code == 200:
            followers_data = followers_response.json()
            return followers_data['total'] #Returns follower count
        else:
            return 0  # Could not get follower count
    except:
        return 0


@time_it
def get_live_streams(game_id: str, client_id, access_token):
    """
    Returns a list of live streams
    user_name = streams[i]['user_name'], similar for viewer count
    :param game_id:
    :return:
    """
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }

    url = "https://api.twitch.tv/helix/streams"
    params = {
        "game_id": game_id,
        "first": 50  # Max results per request
    }

    all_streams = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        all_streams.extend(data["data"])

        # Check if there's a next page
        pagination = data.get("pagination", {}).get("cursor")
        if not pagination:
            break  # No more data

        # Set cursor for next request
        params["after"] = pagination

        # Wait for 80ms before next request (Since Twitch free tier API is refilled every 75ms)
        time.sleep(0.08)

    return all_streams
@time_it
def scrape_twitch_about(url):
    """Scrapes the about part of a twitch user
        :param Twitch about url
        :return data: A json file
    """
    try:
        # Execute the Node.js script with the URL as an argument
        result = subprocess.run(
            ['node', 'JS components/scraper.js', url],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse the JSON output from the Node.js script
        data = json.loads(result.stdout)
        print(data)
        return data

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr}")
        return {"links":"", "email":""}

def get_labels(mail_id: str):
    return get_labels_on_threads_by_email(service, mail_id)
def add_label(label_name: str, mail_id):
    id = get_label_id(service, label_name)
    add_label_to_threads_by_email(service, mail_id, label_id=id)

def send_mail(message: str, mail_id: str, subject: str):
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(os.getenv("mail"), os.getenv("pass"))
    msg = MIMEText(message, 'html')
    sender = "Ank@threeclovermedia.com"
    msg["Subject"] = subject    #f"Let’s Work Together – {str(usernames[i]).capitalize()} x Three Clover Media"
    msg["From"] = sender
    msg["To"] = mail_id
    s.sendmail(sender, mail_id, msg.as_string())



def get_twitch_game_id(client_id: str, access_token: str, game_name: str) -> int:
    url = "https://api.twitch.tv/helix/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }
    params = {"name": game_name}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]["id"]
        else:
            raise ValueError("Game not found")
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def has_replied(sender_email):
    # Load or obtain credentials
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    if type(sender_email) == list:
        mails_list = set([email.strip() for email in sender_email.lower().split(",")])
        for mail in mails_list:
            try:
                # Check for emails from the specified sender
                query = f'from:{mail}'
                results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
                if 'messages' in results:
                    print(f"Yes, you have an email from {sender_email}!")
                    return True
                else:
                    print(f"No emails from {sender_email} found.")
            except HttpError as error:
                print(f"An error occurred: {error}")
                return True
            return False
    else:
        try:
            # Check for emails from the specified sender
            query = f'from:{sender_email}'
            results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
            if 'messages' in results:
                print(f"Yes, you have an email from {sender_email}!")
                return True
            else:
                print(f"No emails from {sender_email} found.")
                return False
        except HttpError as error:
            print(f"An error occurred: {error}")
            return True


def get_message_subject(message_id):
    """
    Retrieve the subject of a specific email using its message ID.

    Args:
        service: Authorized Gmail API service instance.
        message_id: The ID of the message to retrieve.

    Returns:
        The subject of the message, or "No Subject" if not found. Returns None if an error occurs.
    """
    try:
        # Fetch only the Subject header using metadata format
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='metadata',
            metadataHeaders=['Subject']
        ).execute()

        # Extract the subject from the headers
        headers = message['payload'].get('headers', [])
        if headers:
            return headers[0]['value']
        return "No Subject"
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_subjects_by_email(email_address, user_name):
    """
    Retrieve all subjects of emails involving a specific email address.

    Args:
        service: Authorized Gmail API service instance.
        email_address: The email address to search for (in 'from' or 'to' fields).

    Returns:
        A list of subjects of the matching emails, or None if an error occurs.
    """
    subjects = []
    try:
        page_token = None
        while True:
            # List messages where the email address is sender or recipient
            response = service.users().messages().list(
                userId='me',
                q=f"from:{email_address} OR to:{email_address}",
                pageToken=page_token
            ).execute()

            # Get message IDs and fetch their subjects
            messages = response.get('messages', [])
            for msg in messages:
                subject = get_message_subject(msg['id'])
                if subject:
                    subjects.append(subject)

            # Handle pagination
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        if subjects:
            return subjects
        else:
            return [f"Let’s Work Together – {user_name.capitalize()} x Three Clover Media"]
    except HttpError as error:
        print(f"An error occurred: {error}")
        return [f"Let’s Work Together – {user_name.capitalize()} x Three Clover Media"]

@time_it
def scrape_youtube(channel_url: Union[list, set]):
    """
    Scrapes about session for emails
    :param channel_url:
    :return: list containing all found mails
    """
    mails = []
    try:
        for link in channel_url:
            response = requests.get(link)
            mails.extend(str(i).lower() for i in set(extract_emails(response.text)))
        return mails
    except:
        return mails
def calculate_date_difference(input_date: str):
    if input_date == "Null":
        return 0
    today = date.today()
    given_date = datetime.strptime(input_date, "%Y-%m-%d").date()
    difference = today - given_date
    return int(difference.days)




def remove_label_from_emails(email_address, label_name):
    """Remove a label from emails linked to an email address, with a delay between each operation."""
    label_id = get_label_id(service, label_name)
    if not label_id:
        return

    query = f"from:{email_address} OR to:{email_address}"
    page_token = None

    while True:
        try:
            # Fetch up to 100 messages at a time
            response = service.users().messages().list(
                userId='me',
                q=query,
                pageToken=page_token,
                maxResults=100
            ).execute()
            messages = response.get('messages', [])
            if not messages:
                print("No more messages to process.")
                break

            # Process each message individually with a delay
            for msg in messages:
                message_id = msg['id']
                try:
                    service.users().messages().modify(
                        userId='me',
                        id=message_id,
                        body={'removeLabelIds': [label_id]}
                    ).execute()
                    print(f"Label removed from message {message_id}")
                except HttpError as error:
                    print(f"Error on message {message_id}: {error}")

                # Add a delay after each modification
                time.sleep(0.1)  # 0.1 seconds delay

            # Move to the next page of results
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as error:
            print(f"Oops, something went wrong: {error}")
            break

if __name__ == '__main__':
    print(get_twitch_game_id(access_token="grand-theft-auto-v"))
    #add_label("Creator", "basilbenny1002@gmail.com")
    # print(calculate_date_difference("2025-3-8"))
    # print(get_labels("basilbenny1003@gmail.com"))