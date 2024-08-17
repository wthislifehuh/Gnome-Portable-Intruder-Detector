import requests

class TelegramNotifier:
    def __init__(self, chat_id):
        self.token = "7333024088:AAHgT9nWtrz7En_2hIii0Bc_RHkb6NZmT4I"
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, message):
        url = f"{self.base_url}/sendMessage"
        params = {"chat_id": self.chat_id, "text": message}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
        return response
    
    def send_video(self, video):
        url = f"{self.base_url}/sendVideo"
        params = {"chat_id": self.chat_id, "video": video}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("Video sent successfully.")
        else:
            print(f"Failed to send video. Status code: {response.status_code}")
        return response

if __name__ == "__main__":
    chat_id = "1116943112"
    
    notifier = TelegramNotifier(chat_id)
    response = notifier.send_message("Intruder Detected! \nView the live feeds here:")