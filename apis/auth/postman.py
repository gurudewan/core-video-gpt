# receive an email address, and send the magic link
import smtplib
import ssl
import email.message
import logging

from .templates import login_email

from consts import Consts

consts = Consts()

email_address = "flowmushin@gmail.com"
email_password = "haefiuvrowtnfcez"


def send_magic_link(email_addr, magic_link):
    try:
        context = ssl.create_default_context()
        port = 465  # for SSL

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            msg = email.message.Message()
            msg["Subject"] = "welcome to videoGPT"
            msg["From"] = email_address
            msg["To"] = email_addr
            msg.add_header("Content-Type", "text/html")
            email_content = login_email.email_content.replace(
                "magic_link_insert_here", magic_link
            )

            email_content = email_content.encode("utf-8")

            logging.info("The magic link is " + magic_link)
            msg.set_payload(email_content)

            server.login(email_address, email_password)

            server.sendmail(
                msg["From"], [msg["To"]], msg.as_string(policy=email.policy.SMTPUTF8)
            )

    except Exception as e:
        logging.error(f"An error occurred while sending the email to {email_addr}")
        logging.error(e)
        raise e


if __name__ == "__main__":
    email_addr = "gauravdewan@live.com"

    send_magic_link(email_addr, "")
