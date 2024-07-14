import requests


def send_ifttt_notification(event):
    ifttt_event_url = (
        f"https://maker.ifttt.com/trigger/{event}/with/key/cf0NKWg7jttMyiesm2FDw_"
    )
    response = requests.post(ifttt_event_url)
    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print("Failed to send notification:", response.status_code)


# Example call
send_ifttt_notification("intruder_detected")
