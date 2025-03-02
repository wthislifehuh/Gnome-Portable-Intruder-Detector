# MongoDB database  =================================================================
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# MongoDB connection string
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

    # =============== Subscription =============== 
    def add_subscription(self, subscription_code, password):
        try:
            # Hash the password before storing it
            hashed_password = generate_password_hash(password)
            self.db.subscriptions.insert_one({
                'subscription_code': subscription_code,
                'password': hashed_password,  
                'livefeed': 'http://192.168.1.5:5000'
            })
        except Exception as e:
            print(f"Error adding subscription: {e}")

    def update_password(self, subscription_code, new_password):
        try:
            # Hash the new password before updating it
            hashed_password = generate_password_hash(new_password)
            result = self.db.subscriptions.update_one(
                {'subscription_code': subscription_code},
                {'$set': {'password': hashed_password}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating password: {e}")
            return False

    def verify_password(self, subscription_code, password):
        subscription = self.db.subscriptions.find_one({'subscription_code': subscription_code})
        if subscription:
            return check_password_hash(subscription['password'], password)
        return False

    def delete_subscription(self, subscription_code):
        self.db.subscriptions.delete_one({
            'subscription_code': subscription_code
        })
        self.db.chat_ids.delete_many({
            'subscription_code': subscription_code
        })

    def verify_subscription_code(self, subscription_code):
        result = self.db.subscriptions.find_one({
            'subscription_code': subscription_code
        })
        return result is not None
    
    def get_subscription_code_by_chat_id(self, chat_id):
        chat = self.db.chat_ids.find_one({
            'chat_id': chat_id
        })
        return chat['subscription_code'] if chat else None
    
    def get_all_subscription_ids(self):
        subscriptions = self.db.subscriptions.find({}, {'subscription_code': 1})
        return [subscription['subscription_code'] for subscription in subscriptions]
    
    # =============== Chat ID and Phone Number =============== 
    def add_chat_id(self, subscription_code, chat_id, phone_num=None):
        """
        Add a chat ID to a subscription with an optional phone number.
        """
        subscription = self.db.subscriptions.find_one({
            'subscription_code': subscription_code
        })

        if subscription:
            # Check if chat_id already exists
            if self.verify_chat_id(subscription_code, chat_id):
                print(f"Chat ID {chat_id} already exists.")
                return False

            try:
                # Insert the chat_id and associated phone_num (set to None if not provided)
                self.db.chat_ids.insert_one({
                    'subscription_code': subscription_code,
                    'chat_id': chat_id,
                    'phone_num': phone_num  # Will be None if not provided
                })
                return True
            except Exception as e:
                print(f"Error adding chat ID: {e}")
        else:
            print(f"Subscription code {subscription_code} does not exist.")
        return False

    def update_phone_num_for_chat_id(self, subscription_code, chat_id, phone_num):
        """
        Update the phone number associated with a chat ID.
        """
        try:
            result = self.db.chat_ids.update_one(
                {'subscription_code': subscription_code, 'chat_id': chat_id},
                {'$set': {'phone_num': phone_num}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating phone number for chat ID {chat_id}: {e}")
            return False

    def delete_chat_id(self, subscription_code, chat_id):
        """
        Delete a chat ID and its associated phone number.
        """
        try:
            result = self.db.chat_ids.delete_one({
                'subscription_code': subscription_code,
                'chat_id': chat_id
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting chat ID: {e}")
            return False
    
    # Return true if chatID and phone number exists in database
    def verify_chatID_phoneNum(self, subscription_code, chat_id, phone_num):
        result = self.db.chat_ids.find_one({
            'subscription_code': subscription_code,
            'chat_id': chat_id,
            'phone_num': phone_num
        })
        return result is not None

    def verify_chat_id(self, subscription_code, chat_id):
        """
        Verify if a chat ID exists for a given subscription code.
        """
        result = self.db.chat_ids.find_one({
            'subscription_code': subscription_code,
            'chat_id': chat_id
        })
        return result is not None

    def get_chat_ids_by_subscription_code(self, subscription_code):
        """
        Retrieve all chat IDs and associated phone numbers for the given subscription code.
        """
        chat_ids = self.db.chat_ids.find({'subscription_code': subscription_code}, {'chat_id': 1, 'phone_num': 1, '_id': 0})
        return [{'chat_id': chat['chat_id'], 'phone_num': chat.get('phone_num')} for chat in chat_ids]

    
    # =============== Phone Numbers =============== 
    def get_all_phone_nums(self):
        """
        Retrieve all phone numbers from the database.
        """
        phone_nums = self.db.chat_ids.find({'phone_num': {'$ne': None}}, {'phone_num': 1, '_id': 0})
        return [phone['phone_num'] for phone in phone_nums]

    def get_phone_nums_by_subscription_code(self, subscription_code):
        """
        Retrieve all phone numbers associated with the given subscription code.
        """
        phone_nums = self.db.chat_ids.find({'subscription_code': subscription_code, 'phone_num': {'$ne': None}}, {'phone_num': 1, '_id': 0})
        return [phone['phone_num'] for phone in phone_nums]


    def verify_phone_num(self, subscription_code, phone_num):
        result = self.db.chat_ids.find_one({
            'subscription_code': subscription_code,
            'phone_num': phone_num
        })


        return result is not None

    # =============== Livefeed =============== 
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
