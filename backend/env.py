from dotenv import load_dotenv
import os
load_dotenv()
db_user=os.environ.get("db_user")
db_pass = os.environ.get("db_pass")