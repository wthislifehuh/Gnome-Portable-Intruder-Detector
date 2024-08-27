# MongoDB database  =================================================================
from pymongo import MongoClient
from bson.objectid import ObjectId

# Replace with your MongoDB connection string
MONGO_URI = 'mongodb+srv://2103160:zSdnikf6JsDJRy15@gnome.kaqdi.mongodb.net/?retryWrites=true&w=majority&appName=Gnome'
DB_NAME = 'subscriptions_db'

def initialize_database():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Ensure indexes for unique fields
    db.subscriptions.create_index('subscription_code', unique=True)
    db.chat_ids.create_index('chat_id', unique=True)
    
    client.close()

class SubscriptionManager:
    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def add_subscription(self, subscription_code):
        try:
            self.db.subscriptions.insert_one({
                'subscription_code': subscription_code,
                'livefeed': None
            })
        except Exception as e:
            print(f"Error adding subscription: {e}")

    def delete_subscription(self, subscription_code):
        self.db.subscriptions.delete_one({
            'subscription_code': subscription_code
        })
        self.db.chat_ids.delete_many({
            'subscription_code': subscription_code
        })

    def add_chat_id(self, subscription_code, chat_id):
        subscription = self.db.subscriptions.find_one({
            'subscription_code': subscription_code
        })

        if subscription:
            try:
                self.db.chat_ids.insert_one({
                    'subscription_code': subscription_code,
                    'chat_id': chat_id
                })
            except Exception as e:
                print(f"Error adding chat ID: {e}")
        else:
            print(f"Subscription code {subscription_code} does not exist.")

    def delete_chat_id(self, chat_id):
        self.db.chat_ids.delete_one({
            'chat_id': chat_id
        })

    def verify_subscription_code(self, subscription_code):
        result = self.db.subscriptions.find_one({
            'subscription_code': subscription_code
        })
        return result is not None

    def verify_chat_id(self, chat_id):
        result = self.db.chat_ids.find_one({
            'chat_id': chat_id
        })
        return result is not None

    def get_all_chat_ids(self):
        chat_ids = self.db.chat_ids.find({}, {'chat_id': 1})
        return [chat['chat_id'] for chat in chat_ids]

    def get_all_subscription_ids(self):
        subscriptions = self.db.subscriptions.find({}, {'subscription_code': 1})
        return [subscription['subscription_code'] for subscription in subscriptions]

    def get_subscription_code_by_chat_id(self, chat_id):
        chat = self.db.chat_ids.find_one({
            'chat_id': chat_id
        })
        return chat['subscription_code'] if chat else None

    def add_livefeed(self, subscription_code, livefeed_url):
        self.db.subscriptions.update_one(
            {'subscription_code': subscription_code},
            {'$set': {'livefeed': livefeed_url}}
        )

    def get_livefeed(self, subscription_code):
        subscription = self.db.subscriptions.find_one({
            'subscription_code': subscription_code
        })
        return subscription['livefeed'] if subscription else None

    def get_all(self):
        result = []
        subscriptions = self.db.subscriptions.find()

        for idx, subscription in enumerate(subscriptions, start=1):
            subscription_code = subscription['subscription_code']
            livefeed = subscription.get('livefeed', 'No livefeed')

            result.append(f"{idx}. {subscription_code} | {livefeed}")

            chat_ids = self.db.chat_ids.find({
                'subscription_code': subscription_code
            })

            for chat_id in chat_ids:
                result.append(f"- {chat_id['chat_id']}")

        # Join all lines into a single string with new lines separating each entry
        return "\n".join(result)

    def __del__(self):
        self.client.close()
