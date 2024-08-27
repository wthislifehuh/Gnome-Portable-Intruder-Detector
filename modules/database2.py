# Cloud Firestore =================================================================
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Determine the path relative to the current file's directory
base_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(base_dir, "firebase-adminsdk.json")

# Initialize Firestore with the dynamic path
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

class SubscriptionManager:
    def __init__(self):
        self.subscriptions_collection = db.collection('subscriptions')
        self.chat_ids_collection = db.collection('chat_ids')

    def add_subscription(self, subscription_code):
        doc_ref = self.subscriptions_collection.document(subscription_code)
        doc_ref.set({
            'subscription_code': subscription_code,
            'livefeed': None
        }, merge=True)

    def delete_subscription(self, subscription_code):
        doc_ref = self.subscriptions_collection.document(subscription_code)
        doc_ref.delete()

    def add_chat_id(self, subscription_code, chat_id):
        doc_ref = self.subscriptions_collection.document(subscription_code)
        subscription_doc = doc_ref.get()

        if subscription_doc.exists:
            chat_ref = self.chat_ids_collection.document(chat_id)
            chat_ref.set({
                'subscription_code': subscription_code
            }, merge=True)
        else:
            print(f"Subscription code {subscription_code} does not exist.")

    def delete_chat_id(self, chat_id):
        chat_ref = self.chat_ids_collection.document(chat_id)
        chat_ref.delete()

    def verify_subscription_code(self, subscription_code):
        doc_ref = self.subscriptions_collection.document(subscription_code)
        return doc_ref.get().exists

    def verify_chat_id(self, chat_id):
        chat_ref = self.chat_ids_collection.document(chat_id)
        return chat_ref.get().exists

    def get_all_chat_ids(self):
        chat_ids = []
        docs = self.chat_ids_collection.stream()
        for doc in docs:
            chat_ids.append(doc.id)
        return chat_ids
    
    def get_all_subscription_ids(self):
        subscriptions = []
        docs = self.subscriptions_collection.stream()
        for doc in docs:
            subscriptions.append(doc.id)
        return subscriptions
    
    def get_subscription_code_by_chat_id(self, chat_id):
        chat_ref = self.chat_ids_collection.document(chat_id)
        chat_doc = chat_ref.get()

        if chat_doc.exists:
            return chat_doc.to_dict().get('subscription_code')
        return None

    def add_livefeed(self, subscription_code, livefeed_url):
        doc_ref = self.subscriptions_collection.document(subscription_code)
        doc_ref.update({
            'livefeed': livefeed_url
        })

    def get_livefeed(self, subscription_code):
        doc_ref = self.subscriptions_collection.document(subscription_code)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict().get('livefeed')
        return None

    def get_all(self):
        result = []

        subscriptions = self.subscriptions_collection.stream()

        for idx, doc in enumerate(subscriptions, start=1):
            subscription_data = doc.to_dict()
            subscription_code = subscription_data.get('subscription_code')
            livefeed = subscription_data.get('livefeed')
            result.append(f"{idx}. {subscription_code} | {livefeed}")

            chat_ids = self.chat_ids_collection.where('subscription_code', '==', subscription_code).stream()
            for chat_doc in chat_ids:
                result.append(f"- {chat_doc.id}")

        return "\n".join(result)