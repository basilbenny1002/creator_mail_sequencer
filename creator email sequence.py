import pandas
from tqdm import tqdm
import smtplib
import time, random
from functions import has_replied, add_label, get_labels, calculate_date_difference, get_subjects_by_email, remove_label_from_emails
import datetime
from email.mime.text import MIMEText

today = datetime.date.today()


FILE_NAME = "3clovermedia leads all creator leads.csv"
# s = smtplib.SMTP("smtp.gmail.com", 587)
# s.starttls()
# s.login("Ank@threeclovermedia.com", "iojw uppy ztsn sjdv")

df = pandas.read_csv(FILE_NAME)
usernames = df['Username'].tolist()
followers = df['Followers'].tolist()
viewer_count = df['Viewer_count'].tolist()
language = df['Language'].tolist()
game = df['Game'].tolist()
discord = df['Discord'].tolist()
youtube = df['Youtube'].tolist()
contact = df['Contact'].tolist()
initial_contact = df['Initial contact'].tolist()
second_follow_up = df['Second follow up'].tolist()
third_follow_up = df['Third follow up'].tolist()
initial_contact_date = df['Initial contact date'].tolist()
second_contact_date = df['Second contact date'].tolist()
third_contact_date = df['Third contact date'].tolist()
subscriber_count = df['Subscriber count'].tolist()
replied = df["Has replied"].tolist()
classify = df['Classify'].tolist()
interested = df['Interested'].tolist()

def send_mail(message: str, mail_id: str, subject: str):
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login("Ank@threeclovermedia.com", "iojw uppy ztsn sjdv")
    msg = MIMEText(message, 'html')
    sender = "Ank@threeclovermedia.com"
    msg["Subject"] = subject    #f"Let’s Work Together – {str(usernames[i]).capitalize()} x Three Clover Media"
    msg["From"] = sender
    msg["To"] = mail_id
    s.sendmail(sender, mail_id, msg.as_string())
    s.quit()

def initial_message(mail_id: str, platform: str, user_name: str, i:int):
    initial_message = f"""
                            <html>
              <body style="font-family: sans-serif; font-size: 12px; color: black;">
                <p>Hey {user_name.capitalize()}!</p>

                <p>I’m Ank, Junior Growth Specialist at <a href="https://www.threeclovermedia.com/" style="color: blue; text-decoration: underline;">Three Clover Media</a>, an Influencer Management agency. We help creators turn their content into real opportunities by securing brand deals, sponsorships, and collaborations.</p>

                <p>We operate on a simple 10% commission model—meaning no upfront costs or fees. Our goal is to connect influencers with brands that align with their audience and values, while also offering services like content strategy, monetization support, and professional editing for short-form content on platforms like TikTok, Instagram, and YouTube Shorts.</p>

                <p>We’ve worked with creators like 
                  <a href="https://www.youtube.com/channel/UCQ52Vb5prBWiGflzMGjxj4g" style="color: blue; text-decoration: underline;">Issamezany</a>, 
                  <a href="https://www.youtube.com/tacularr" style="color: blue; text-decoration: underline;">Tacularr</a>, 
                  <a href="https://www.youtube.com/@Warriorrust" style="color: blue; text-decoration: underline;">Warrior</a>, 
                  <a href="https://www.youtube.com/@mikeyduck0371" style="color: blue; text-decoration: underline;">Mikeyduck</a>, 
                  and many others, helping them land brand partnerships and expand their reach. 
                  I came across your content and really love what you’re doing—especially on {platform}! 
                  I’d love to learn more about your goals and see if we’d be a good fit.</p>

                <p>Have you worked with an agency before? If not, I’d be happy to share how we can help you grow. Let me know what you think!</p>

                <p>Looking forward to hearing from you.</p>

                <p>Best,<br>
                Ank<br>
                Three Clover Media<br>
                <a href="mailto:aniruank@gmail.com" style="color: blue; text-decoration: underline;">aniruank@gmail.com</a></p>
              </body>
            </html>
                """
    mails_list = set([email.strip() for email in mail_id.lower().split(",")])
    for mail in mails_list:
        send_mail(initial_message, mail_id=mail, subject=f"Let’s Work Together – {str(usernames[i]).capitalize()} x Three Clover Media")
        add_label("Initial contact", mail)
        add_label("Creator", mail)
        add_label("Waiting for reply", mail)
    initial_contact_date[i] = (str(today))
    initial_contact[i] = "Yes"

def do_second_follow_up(mail_id: str, i: int, user_name: str, platform: str):
    second_message = f"""<html>
  <body style="font-family: sans-serif; font-size: 12px; color: black;">
    <p>Hey {user_name.capitalize()}!</p>
    <p>Hope you're doing well! Just wanted to follow up on my last message. I really love what you’re doing on {platform} and think we could help you land some great sponsorships.</p>
    <p>At <a href="https://www.threeclovermedia.com/" style="color: blue; text-decoration: underline;">Three Clover Media</a>, we work with creators like you to secure brand deals and monetize content—without any upfront fees. I’d love to learn more about your goals and see if we’re a good fit.</p>
    <p>Let me know if you're open for a quick chat!</p>
    <p>Best,<br>
    Ank<br>
    Three Clover Media<br>
    <a href="mailto:aniruank@gmail.com" style="color: blue; text-decoration: underline;">aniruank@gmail.com</a></p>
  </body>
</html>"""
    mails_list = set([email.strip() for email in mail_id.lower().split(",")])
    for mail in mails_list:
        send_mail(second_message, mail, subject=f"{get_subjects_by_email(mail, user_name)[-1]}")
        add_label("Second contact", mail)
        remove_label_from_emails(mail, "Initial contact")
    second_follow_up[i] = "Yes"
    second_contact_date[i] = str(today)



def do_third_follow_up(mail_id: str, i: int, user_name: str, platform: str):
    third_message = f"""<html>
  <body style="font-family: sans-serif; font-size: 12px; color: black;">
    <p>Hey {user_name.capitalize()},</p>
    <p>I know things can get busy, so I wanted to follow up again. We work with creators like you to secure sponsorships, build partnerships, and grow their brand—without any upfront costs.</p>
    <p>If this is something that interests you, let me know!</p>
    <p>Best,<br>
    Ank<br>
    Three Clover Media<br>
    <a href="mailto:aniruank@gmail.com" style="color: blue; text-decoration: underline;">aniruank@gmail.com</a></p>
  </body>
</html>"""
    mails_list = set([email.strip() for email in mail_id.lower().split(",")])
    for mail in mails_list:
        send_mail(third_message, mail, subject=f"{get_subjects_by_email(mail, user_name)[-1]}")
        add_label("Third contact", mail)
        remove_label_from_emails(mail, "Second contact")
    third_follow_up[i] = "Yes"
    third_contact_date[i] = str(today)
def process_labels(mail_id: str, i):
    labels = get_labels(mail_id)
    for label in labels:
        if label == "Interested":
            interested[i] = "Yes"
        if label == "Not interested":
            interested[i] = "No"


try:
    count = 0
    for i in tqdm(range(len(usernames)), desc="Mailing the users"):
        # count=count+1
        # if count > 100:
        #     break
        time.sleep(random.randint(1, 2))
        mails_list = set([email.strip() for email in contact[i].lower().split(",")])
        if contact[i] == "Couldn't find a valid gmail" or contact[
            i] == "Couldn't find a valid mail" or contact[i] == "Couldn't find a valid email":
            print("Couldn't find mail")
            continue
        if replied[i] == "Yes":
            for mails in mails_list:
                labels = get_labels(mails)
                if "Interested" not in labels:
                    if "Not interested" not in labels:
                        add_label("classify", mails)
                        remove_label_from_emails(mails, "Waiting for reply")
                        classify[i] = "Yes"
                    else:
                        interested[i] = "No"
                        classify[i] = "Null"
                        remove_label_from_emails(mails, "classify")
                        remove_label_from_emails(mails, "Initial contact")
                        remove_label_from_emails(mails, "Waiting for reply")
                        remove_label_from_emails(mails, "Second contact")
                        remove_label_from_emails(mails, "Third contact")
                else:
                    interested[i] = "Yes"
                    classify[i] = "Null"
                    remove_label_from_emails(mails, "classify")
                    remove_label_from_emails(mails, "Initial contact")
                    remove_label_from_emails(mails, "Waiting for reply")
                    remove_label_from_emails(mails, "Second contact")
                    remove_label_from_emails(mails, "Third contact")

                remove_label_from_emails(mails, "Waiting for reply")
            continue
        if initial_contact[i] == "Yes" and second_follow_up[i] == "Yes" and third_follow_up[i] == "Yes":
            continue
        if int(followers[i]) > int(subscriber_count[i]):
            platform = "Twitch"
        else:
            platform = "YouTube"
        if initial_contact[i] == "No" and contact[i] != "Couldn't find a valid gmail" and contact[
            i] != "Couldn't find a valid mail" and contact[i] != "Couldn't find a valid email":
            initial_message(mail_id=contact[i], platform=platform, user_name=usernames[i], i=i)
            continue

        elif has_replied(mails_list):
            replied[i] = "Yes"
            for mails in mails_list:
                labels = get_labels(mails)
                if "Interested" not in labels:
                    if "Not interested" not in labels:
                        add_label("classify", mails)
                        remove_label_from_emails(mails, "Waiting for reply")
                        classify[i] = "Yes"
                    else:
                        remove_label_from_emails(mails, "classify")
                        interested[i] = "No"
                        classify[i] = "Null"
                        remove_label_from_emails(mails, "Initial contact")
                        remove_label_from_emails(mails, "Waiting for reply")
                        remove_label_from_emails(mails, "Second contact")
                        remove_label_from_emails(mails, "Third contact")
                else:
                    classify[i] = "Null"
                    interested[i] = "Yes"
                    remove_label_from_emails(mails, "classify")
                    remove_label_from_emails(mails, "Initial contact")
                    remove_label_from_emails(mails, "Waiting for reply")
                    remove_label_from_emails(mails, "Second contact")
                    remove_label_from_emails(mails, "Third contact")
            continue

        elif initial_contact[i] == "Yes" and second_follow_up[i] == "No" and calculate_date_difference(initial_contact_date[i]) > 3:
            do_second_follow_up(contact[i], i, user_name=usernames[i], platform=platform)
            second_follow_up[i] = "Yes"
            second_contact_date[i] = str(today)
            continue

        elif has_replied(mails_list):
            replied[i] = "Yes"
            for mails in mails_list:
                labels = get_labels(mails)
                if "Interested" not in labels:
                    if "Not interested" not in labels:
                        add_label("classify", mails)
                        remove_label_from_emails(mails, "Waiting for reply")
                        classify[i] = "Yes"
                    else:
                        classify[i] = "Null"
                        remove_label_from_emails(mails, "classify")
                        interested[i] = "No"
                else:
                    classify[i] = "Null"
                    remove_label_from_emails(mails, "classify")
                    interested[i] = "Yes"
            continue

        elif initial_contact[i] == "Yes" and second_follow_up[i] == "Yes" and third_follow_up[i] == "No" and calculate_date_difference(second_contact_date[i]) > 3:
            do_third_follow_up(contact[i], i, user_name=usernames[i], platform=platform)
            third_follow_up[i] = "Yes"
            third_contact_date[i] = str(today)
            continue

        else:
            print(f"Final else condition reached {i}")
            #TODO break
            continue

except Exception as e:
    print(f"Some error occurred: {e}")
    datas = {
        "Username": usernames,
        "Followers": followers,
        "Viewer_count": viewer_count,
        "Language": language,
        "Game": game,
        "Discord": discord,
        "Youtube": youtube,
        "Contact": contact,
        "Initial contact": initial_contact,  # Following your example’s key for 'Initial message'
        "Second follow up": second_follow_up,  # Following your example’s key for 'Second follow up'
        "Third follow up": third_follow_up,
        "Initial contact date": initial_contact_date,
        "Second contact date": second_contact_date,
        "Third contact date": third_contact_date,
        "Subscriber count": subscriber_count,
        "Has replied": replied,
        "Classify": classify,
        "Interested": interested,
    }
    processed_data = pandas.DataFrame(datas)
    processed_data.to_csv(f"{FILE_NAME} error happened", index=False)

else:
    datas = {
        "Username": usernames,
        "Followers": followers,
        "Viewer_count": viewer_count,
        "Language": language,
        "Game": game,
        "Discord": discord,
        "Youtube": youtube,
        "Contact": contact,
        "Initial contact": initial_contact,            # Following your example’s key for 'Initial message'
        "Second follow up": second_follow_up,   # Following your example’s key for 'Second follow up'
        "Third follow up": third_follow_up,
        "Initial contact date": initial_contact_date,
        "Second contact date": second_contact_date,
        "Third contact date": third_contact_date,
        "Subscriber count": subscriber_count,
        "Has replied": replied,
        "Classify": classify,
        "Interested": interested,
    }
    processed_data = pandas.DataFrame(datas)
    processed_data.to_csv(f"{FILE_NAME}", index=False)