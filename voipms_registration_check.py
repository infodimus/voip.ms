import requests
import os
import json
import smtplib
from email.mime.text import MIMEText
import datetime
import shutil

MAX_LOG_FILE_SIZE_MB = 100 #100 MB

LOG_FILE_PATH = "/full_path_to/voipms.log"
BACKUP_LOG_FILE_PATH = "/full_path_to/voipms.log.bkp"

VOIPMS_LOGIN_EMAIL = "voipmsloginemail@example.tld"
VOIPMS_API_PASSWORD = "voipms strong API password"

SMTP_SERVER = 'smtp.example.tld'
SMTP_PORT = 465 # or 587
USERNAME = 'mysenderemailaddress@example.tld'
PASSWORD = 'password for myemailaddress@example.tld' # use password for application for Gmail and Yahoo
SENDER_EMAIL = USERNAME
RECEIVER_EMAIL = 'myreceiveremailaddress@example.tld'

SIP_ACCOUNT_1 = 'your voip.ms SIP user'
SIP_ACCOUNT_2 = 'your another voip.ms SIP user' #remove if not needed
    

def write_to_log(s):
    """
    Writes a given string, along with the current date and time, to a log file located at LOG_FILE_PATH.

    Parameters:
    - s (str): The string to be written to the file.
    """
    # Get the current date and time
    current_time = datetime.datetime.now()
    # Format the date and time
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Create the log entry with the timestamp
    log_entry = f"{timestamp} - {s}\n"

    # Open the log file in append mode
    with open(LOG_FILE_PATH, 'a') as file:
        file.write(log_entry)  # Write the log entry to the file

def check_and_backup_log():
    """
    Checks if the size of 'voipms.log' exceeds 100 MB. If it does, it backs up the file to 'voipms.log.bkp'
    and resets the 'voipms.log' file.
    """
    
       
    # Check if the file exists
    if not os.path.exists(LOG_FILE_PATH):
        print("Log file does not exist.")
        return

    # Get the size of the file in bytes
    file_size = os.path.getsize(LOG_FILE_PATH)

    # Convert size to megabytes
    size_in_mb = file_size / (1024 * 1024)

    # Check if the file size is greater than 100 MB
    if size_in_mb > MAX_LOG_FILE_SIZE_MB:
        # Copy the file to a backup
        shutil.copy(LOG_FILE_PATH, BACKUP_LOG_FILE_PATH)
        print(f"File backed up to {backup_file_path}")

        # Reset the original log file
        open(LOG_FILE_PATH, 'w').close()  # This opens the file in write mode and immediately closes it, truncating it to 0 bytes
        print("Original log file has been reset.")

    else:
        print("Log file size is under the limit. No action taken.")

def send_email(smtp_server, smtp_port, username, password, sender_email, receiver_email, subject, body):
    """
    Sends an email using SMTP with SSL.

    Parameters:
    - smtp_server (str): Address of the SMTP server.
    - smtp_port (int): Port for SSL connection.
    - username (str): SMTP server username (usually the sender's email).
    - password (str): SMTP server password.
    - sender_email (str): Email address of the sender.
    - receiver_email (str): Email address of the receiver.
    - subject (str): Subject of the email.
    - body (str): Body of the email (plain text).
    """
    # Create a MIMEText object
    email_message = MIMEText(body)
    email_message['From'] = sender_email
    email_message['To'] = receiver_email
    email_message['Subject'] = subject

    # Send the email
    try:
        # Connect to the SMTP server using SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(username, password)  # login to the email server
            server.sendmail(sender_email, receiver_email, email_message.as_string())  # send the email
            print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')

def send_email_to_me(sip_account, body, isFailed):
    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT
    username = USERNAME
    password = PASSWORD
    sender_email = USERNAME
    receiver_email = RECEIVER_EMAIL
    
    if isFailed == True:
        subject = "Registration failed for account " + sip_account
    else:
        subject = "Registration restored for account " + sip_account
    send_email(smtp_server, smtp_port, username, password, sender_email, receiver_email, subject, body)

def send_email_for_failed_registration(sip_account, text):
    file_path = "/home/main/voipms/noreg_" + sip_account + ".txt"

    if not os.path.exists(file_path):
        send_email_to_me(sip_account, text, True)
        with open(file_path, 'w') as file:
            file.write("This file is created to prevent further email sending.")
            print(f"File '{file_path}' created.")
            write_to_log(f"File '{file_path}' created.")

    else:
        print(f"The file '{file_path}' exists. No email sent.")
        write_to_log(f"The file '{file_path}' exists. No email sent.")

def send_email_for_restored_registration(sip_account, text):
    file_path = "/home/main/voipms/noreg_" + sip_account + ".txt"

    if os.path.exists(file_path):
        send_email_to_me(sip_account, text, False)        
    else:
        print(f"The file '{file_path}' does not exist. No email sent.")


def reset_lock(sip_account):
    file_path = "/home/main/voipms/noreg_" + sip_account + ".txt"
    if os.path.exists(file_path):
    # If it exists, delete the file
        os.remove(file_path)
        print(f"reset_lock(): The file '{file_path}' has been deleted.")
        write_to_log(f"reset_lock(): The file '{file_path}' has been deleted.")
    else:
        # If the file does not exist, print a message
        print(f"reset_lock(): The file '{file_path}' does not exist.")
        write_to_log(f"reset_lock(): The file '{file_path}' does not exist.")


class VoipMS:
    def __init__(self, username: str, password: str):
        self.params: dict[str, str] = {
            "api_username": username,
            "api_password": password
        }
        self.url = "https://voip.ms/api/v1/rest.php"

    def send_sms(self, did: str, destination: str, message: str) -> requests.Response:
        """Send an sms.

        Parameters
        ----------
        did : str
            Your SMS enabled VoipMS DID.

        destination : str
            The number you want to send an SMS to.

        message : str
            The body of your SMS message (max chars: 160)
        
        """
        _params: dict[str, str] = {
            "method": "sendSMS",
            "did": did,
            "dst": destination,
            "message": message
        }
        self.params.update(_params)
        return requests.get(self.url, params=self.params)

        

    def get_registration_status(self, account: str) -> requests.Response:
        """gets regostration status

        Parameters
        ----------
        account : str
            account

        
        """
        _params: dict[str, str] = {
            "method": "getRegistrationStatus",
            "account": account
        }
        self.params.update(_params)
        return requests.get(self.url, params=self.params)


def validate_registration(voipms, sip_account):
        response = voipms.get_registration_status(sip_account)
        print(response.json(),end='\n')
        write_to_log(response.json())

        
        jresponse = response.json()
        registration_status = jresponse["registered"]
        print("registered = ", registration_status, end='\n')

        #registration_status = 'no'
        
        if registration_status == 'no':
           send_email_for_failed_registration(sip_account, str(jresponse))
        else:
           send_email_for_restored_registration(sip_account, str(jresponse))
           reset_lock(sip_account) 
           
        
        return (registration_status, jresponse)
   
    
def main(voipms: VoipMS):
    check_and_backup_log()

    write_to_log(f"VoipMS Registration validation started")

    message = "Hello World"
    #response = voipms.send_sms(did="990001111", destination="9990002222", message=message)
    sip_account = SIP_ACCOUNT_1
    status, response = validate_registration(voipms, sip_account)
    
    sip_account = SIP_ACCOUNT_2
    status, response = validate_registration(voipms, sip_account)

    write_to_log(f"VoipMS Registration validation ended\n")



if __name__ == "__main__":
    main(VoipMS(VOIPMS_LOGIN_EMAIL, VOIPMS_API_PASSWORD))
