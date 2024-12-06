import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from jinja2 import Template

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("EMAIL_USERNAME")
SMTP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

def get_html_template():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                background-color: #F5F7FA;
            }
        </style>
    </head>
    <body>
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #F5F7FA;">
            <tr>
                <td align="center" style="padding: 20px;">
                    <!-- Main Container -->
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td align="center" style="background-color: #4A90E2; padding: 40px 20px; color: white;">
                                <h1 style="margin: 0; font-size: 2.5em; font-weight: 300; letter-spacing: 2px;">禁煙 (Kinen)</h1>
                                <p style="margin: 10px 0 0; font-size: 1.1em; opacity: 0.9;">Your Daily Progress Report</p>
                            </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px;">
                                <!-- Greeting -->
                                <p style="font-size: 1.2em; color: #2C3E50; margin-bottom: 30px;">Hello {{ username }},</p>

                                <!-- KPI Cards - Row 1 -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <!-- Cigarettes Card -->
                                        <td width="50%" style="padding: 10px;">
                                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 12px; border: 1px solid #E5E7EB; overflow: hidden;">
                                                <tr>
                                                    <td style="padding: 20px; text-align: center;">
                                                        <div style="font-size: 2em; margin-bottom: 10px;">🚬</div>
                                                        <div style="font-size: 0.9em; color: #64748B; text-transform: uppercase; letter-spacing: 1px;">Cigarettes Today</div>
                                                        <div style="font-size: 2.5em; font-weight: bold; color: #4A90E2; margin: 10px 0;">{{ cigarettes_smoked }}</div>
                                                        <div style="font-size: 0.9em; color: #64748B;">Target: {{ target_cigarettes }}</div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>

                                        <!-- Cravings Card -->
                                        <td width="50%" style="padding: 10px;">
                                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 12px; border: 1px solid #E5E7EB; overflow: hidden;">
                                                <tr>
                                                    <td style="padding: 20px; text-align: center;">
                                                        <div style="font-size: 2em; margin-bottom: 10px;">💪</div>
                                                        <div style="font-size: 0.9em; color: #64748B; text-transform: uppercase; letter-spacing: 1px;">Cravings Resisted</div>
                                                        <div style="font-size: 2.5em; font-weight: bold; color: #4A90E2; margin: 10px 0;">{{ cravings_resisted }}</div>
                                                        <div style="font-size: 0.9em; color: #64748B;">Success Rate: {{ success_rate }}%</div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>

                                <!-- KPI Cards - Row 2 -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <!-- Streak Card -->
                                        <td width="50%" style="padding: 10px;">
                                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 12px; border: 1px solid #E5E7EB; overflow: hidden;">
                                                <tr>
                                                    <td style="padding: 20px; text-align: center;">
                                                        <div style="font-size: 2em; margin-bottom: 10px;">📅</div>
                                                        <div style="font-size: 0.9em; color: #64748B; text-transform: uppercase; letter-spacing: 1px;">Smoke-Free Streak</div>
                                                        <div style="font-size: 2.5em; font-weight: bold; color: #4A90E2; margin: 10px 0;">{{ streak }}</div>
                                                        <div style="font-size: 0.9em; color: #64748B;">Days Strong</div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>

                                        <!-- Trigger Card -->
                                        <td width="50%" style="padding: 10px;">
                                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 12px; border: 1px solid #E5E7EB; overflow: hidden;">
                                                <tr>
                                                    <td style="padding: 20px; text-align: center;">
                                                        <div style="font-size: 2em; margin-bottom: 10px;">📍</div>
                                                        <div style="font-size: 0.9em; color: #64748B; text-transform: uppercase; letter-spacing: 1px;">Top Trigger</div>
                                                        <div style="font-size: 1.5em; font-weight: bold; color: #4A90E2; margin: 10px 0;">{{ common_trigger }}</div>
                                                        <div style="font-size: 0.9em; color: #64748B;">Be mindful here</div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>

                                <!-- Money Saved Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                    <tr>
                                        <td style="background-color: #27AE60; padding: 30px; border-radius: 12px; text-align: center; color: white;">
                                            <div style="text-transform: uppercase; letter-spacing: 2px; font-size: 0.9em; opacity: 0.9;">Total Money Saved</div>
                                            <div style="font-size: 3em; font-weight: bold; margin: 10px 0;">{{ currency }} {{ money_saved }}</div>
                                            <div style="font-size: 1.1em;">Keep going! That's real progress. 🎯</div>
                                        </td>
                                    </tr>
                                </table>

                                <!-- Inspiration Quote -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                    <tr>
                                        <td style="text-align: center; padding: 20px; color: #2C3E50; font-style: italic; border-top: 1px solid #E5E7EB; border-bottom: 1px solid #E5E7EB;">
                                            "Small steps today, big changes tomorrow. You're doing great!"
                                        </td>
                                    </tr>
                                </table>

                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center" style="padding: 20px;">
                                            <a href="http://localhost:5000/" style="display: inline-block; padding: 15px 30px; background-color: #4A90E2; color: white; text-decoration: none; border-radius: 25px; font-weight: 500;">View Full Progress</a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding: 30px; text-align: center; color: #64748B; font-size: 0.9em;">
                                <p style="margin: 0;">This email was sent by Kinen - Your Mindful Smoking Cessation Companion</p>
                                <p style="margin: 5px 0 0;">To manage your email preferences, visit your app settings.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def send_daily_report(user, stats):
    if not all([SMTP_USERNAME, SMTP_PASSWORD]):
        raise ValueError("Email credentials not configured")

    template = Template(get_html_template())
    html_content = template.render(
        username=user.username,
        cigarettes_smoked=stats['cigarettes_smoked'],
        target_cigarettes=stats['target_cigarettes'],
        cravings_resisted=stats['cravings_resisted'],
        currency=stats['currency'],
        money_saved=stats['money_saved'],
        streak=stats['streak'],
        common_trigger=stats['common_trigger'],
        success_rate=stats['success_rate']
    )

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Your Mindful Journey Update - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = SMTP_USERNAME
    msg['To'] = user.email

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
