import os
import csv
from flask import Flask, render_template, request
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# 1. Load configuration
load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

SENDGRID_API_KEY = os.getenv('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')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')


# 2. Define the email sending function
def send_single_email(to_email, name, subject, message_body):
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=f"Hello {name},\n\n{message_body}"
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return True
    except Exception as e:
        print(f"Error sending to {to_email}: {e}")
        return False


# 3. Define Web Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send', methods=['POST'])
def handle_send():
    subject = request.form.get('subject')
    message_text = request.form.get('message')
    file = request.files.get('file')

    results = []

    if file:
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)

        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row['email'].strip()
                name = row['name'].strip()

                status = send_single_email(email, name, subject, message_text)
                results.append({"email": email, "name": name, "status": "Sent" if status else "Failed"})

    # Instead of plain text, we send the data to a new template
    return render_template('results.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)