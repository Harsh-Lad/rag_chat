import os
from openai import OpenAI
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class ChatUtils:
    def __init__(self):
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.chat_history = []

    def add_to_history(self, role, message):
        self.chat_history.append({"role": role, "content": message})

    def generate_response(self, user_message):
        self.add_to_history("user", user_message)

        if self.is_email_request(user_message):
            email_response = self.send_email(user_message)
            self.add_to_history("assistant", email_response)
            return email_response

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.chat_history,
            max_tokens=150,
        )

        assistant_message = response.choices[0].message.content.strip()
        self.add_to_history("assistant", assistant_message)
        return assistant_message

    def is_email_request(self, message):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in email communication. Please help me determine if the following message is a request to send an email. Answer in a list similar to ['answer', 'email of the recipient', 'subject', 'body']."},
                {"role": "user", "content": f"Is the following message a request to send an email? Answer with 'yes' or 'no'. If yes, also extract the recipient's email, the subject, and the body.\n\nMessage: {message}"}
            ],
            temperature=0
        )

       
        response_content = response.choices[0].message.content
        print(f"API Response: {response_content}")

        email_info = response_content.replace('[', '').replace(']', '').replace("'", '').split(',')
        answer = email_info[0].strip().lower()
        
        if answer == "yes":
            recipient_email = email_info[1].strip()
            subject = email_info[2].strip()
            body = email_info[3].strip()
            return True, recipient_email, subject, body
        else:
            return False, None, None, None

    def send_email(self, user_message):
        try:
           
            is_email, recipient, subject, body = self.is_email_request(user_message)
            
            if not is_email:
                return "The message was not an email request."

           
            smtp_server = os.getenv("SMTP_SERVER")
            smtp_port = int(os.getenv("SMTP_PORT"))
            sender_email = os.getenv("SENDER_EMAIL")
            sender_password = os.getenv("SENDER_PASSWORD")

    
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            return "Email sent successfully."
        except Exception as e:
            return f"Failed to send email: {e}"
