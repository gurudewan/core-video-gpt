# receive an email address, and send the magic link
import smtplib
import ssl
import email.message
import logging

from .templates import login_email

import consts

from consts import APP_ENV, VIDEOGPT_APP_URL

email_address = "flowmushin@gmail.com"
email_password = "haefiuvrowtnfcez"


def send_magic_link(email_addr, magic_token):
    try:
        context = ssl.create_default_context()
        port = 465  # for SSL

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            msg = email.message.Message()
            msg["Subject"] = "Log in to flow"
            msg["From"] = email_address
            msg["To"] = email_addr
            msg.add_header("Content-Type", "text/html")
            magic_link = f"{VIDEOGPT_APP_URL}/auth?magic_token={magic_token}"
            email_content = login_email.email_content.replace(
                "magic_link_insert_here", magic_link
            )

            logging.info("The magic link is " + magic_link)
            msg.set_payload(email_content)

            server.login(email_address, email_password)

            server.sendmail(msg["From"], [msg["To"]], msg.as_string())

        return True
    except Exception as e:
        logging.error("An error occured while sending the email to {email_addr}")
        logging.error(e)
        return False


if __name__ == "__main__":
    email_addr = "gauravdewan@live.com"

    send_magic_link(email_addr, "")
