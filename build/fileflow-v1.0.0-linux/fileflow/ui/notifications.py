import subprocess

def send_notification(title, message):
    try:
        subprocess.run([
            'notify-send',
            '--app-name=SELO FileFlow',
            title,
            message
        ], check=False)
    except Exception as e:
        print(f"Notification error: {e}")
