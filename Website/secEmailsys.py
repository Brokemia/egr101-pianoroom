"""
Created on 10/27/2020

@author: xxnex
"""

import smtplib, email
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def get_contacts(filename):
    emails = []
    f = open(filename)
    for a_contact in f:
        emails.append(a_contact.strip())
    return emails

def read_template(filename):
    f = open(filename)
    output = ""
    for line in f:
        output += line.strip() + "\n"
    f.close()
    return output

def send_mail():
    username = "westpianorooms@outlook.com"
    password = "dukepianoroomsarethebest7854"

    emails = get_contacts('emailstext')  # read contacts
    message_template = read_template('message')

    s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    s.starttls()
    s.login(username, password)

    for email in emails:
        email = str(email)
        print(email)
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = email
        msg['Subject'] = "West Duke Piano Room Available"
        msg.attach(MIMEText(message_template, "plain"))
        text = msg.as_string()

        try:
            print('sending mail to ', email)
            s.sendmail(username, email, text)

        except ValueError:
            print(str("error"))


if __name__ == '__main__':
    send_mail()
