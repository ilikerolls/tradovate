import os

# Set environment variable
os.environ['TO_ENV'] = 'DEMO'
os.environ['TO_NAME'] = 'egluzman'
os.environ['TO_PASSWORD'] = 'Trader6427@!'
os.environ['TO_APPID'] = '0.0.1'
os.environ['TO_CID'] = '1802'
os.environ['TO_SEC'] = '386346b9-bcbe-4ad5-99e6-e21fa2feb34f'
os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PORT'] = '6379'

# Let's debug this
host = os.environ.get("REDIS_HOST", "redis")
port = int(os.environ.get("REDIS_PORT", "6379"))