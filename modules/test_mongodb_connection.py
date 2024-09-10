from pymongo import MongoClient

# MongoDB connection URI
MONGO_URI = 'mongodb+srv://2103160:zSdnikf6JsDJRy15@gnome.kaqdi.mongodb.net/?retryWrites=true&w=majority&appName=Gnome&tls=true'

try:
    # Create a MongoClient object
    client = MongoClient(MONGO_URI)
    
    # Perform a ping command to test the connection
    client.admin.command('ping')
    
    print("Connection successful!")
    
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
