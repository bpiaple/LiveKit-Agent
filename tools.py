import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import requests
from langchain_community.tools import DuckDuckGoSearchRun
from livekit.agents import RunContext, function_tool


@function_tool
async def get_weather(context: RunContext, city: str) -> str:
    """
    Fetches the current weather for a given city using the wttr.in service.
    """

    logging.info(f"Fetching weather data for {city}")
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather in {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(
                f"Failed to fetch weather data for {city}: {response.status_code}"
            )
            return "Sorry, I couldn't fetch the weather information right now."
    except Exception as e:
        logging.error(f"Error fetching weather data for {city}: {e}")
        return "Sorry, I couldn't fetch the weather information right now."


@function_tool
async def web_search(context: RunContext, query: str) -> str:
    """
    Performs a web search using DuckDuckGo and returns the top result.
    """

    logging.info(f"Performing web search for query: {query}")
    try:
        search_tool = DuckDuckGoSearchRun()
        results = search_tool.run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return f"Search results for '{query}': {results}"
    
    except Exception as e:
        logging.error(f"Error performing web search for '{query}': {e}")
        return "Sorry, I couldn't perform the web search right now."


@function_tool
async def send_email(
    context: RunContext,
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None,
) -> str:
    """
    Send an email through Gmail SMTP

    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        message (str): The body of the email.
        cc_email (Optional[str]): The CC email address.

    Returns:
        str: A message indicating the result of the email sending operation.
    """

    try:
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Get credentials from environment variables
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Use App Password, not regular password
        
        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials not found in environment variables")
            return "Email sending failed: Gmail credentials not configured."
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add CC if provided
        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)
        
        # Attach message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(gmail_user, gmail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, recipients, text)
        server.quit()
        
        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"
        
    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"
    
