from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pymysql
from passlib.context import CryptContext

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# **Database Connection**
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="123456789",
        database="Agrocure",
        cursorclass=pymysql.cursors.DictCursor
    )

# **User Models**
class UserRegister(BaseModel):
    name: str
    phone: str
    password: str

class LoginModel(BaseModel):
    phone: str
    password: str

class UpdateUserRequest(BaseModel):
    phone: str
    name: str
    password: str

# **Register User**
@router.post("/register")
async def register(user: UserRegister):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE Phone = %s", (user.phone,))
        existing_user = cursor.fetchone()
        if existing_user:
            return {"error": "User already exists"}

        # Hash the password
        hashed_password = pwd_context.hash(user.password)

        # Insert into database
        cursor.execute("INSERT INTO users (Name, Phone, password) VALUES (%s, %s, %s)",
                       (user.name, user.phone, hashed_password))
        db.commit()
        return {"message": "User registered successfully"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

# **User Login**
@router.post("/login")
async def login(data: LoginModel):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE Phone = %s", (data.phone,))
        user = cursor.fetchone()

        if user and pwd_context.verify(data.password, user["password"]):
            return {"message": "Login successful", "Name": user["Name"], "Phone": user["Phone"]}
        else:
            raise HTTPException(status_code=400, detail="Invalid credentials")

    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

# **Fetch Logged-in User Details**
@router.get("/user/{phone}")
def get_user(phone: str):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT Name, Phone FROM users WHERE Phone = %s", (phone,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {"name": user["Name"], "phone": user["Phone"]}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

# **Update User Details**
@router.post("/update_user")
def update_user(update_request: UpdateUserRequest):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Check how many accounts exist with the given phone number
        cursor.execute("SELECT COUNT(*) AS count FROM users WHERE Phone = %s", (update_request.phone,))
        user_count = cursor.fetchone()["count"]

        if user_count > 1:
            raise HTTPException(status_code=400, detail="Phone number already exists in multiple accounts")

        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE password = %s", (update_request.password,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify the existing password before updating
        if not pwd_context.verify(update_request.password, user["password"]):
            raise HTTPException(status_code=400, detail="Incorrect password")
        
        # If the password is being updated, hash the new password
        hashed_password = pwd_context.hash(update_request.password)

        # Update user details, including the password if needed
        cursor.execute("UPDATE users SET Name = %s, password = %s WHERE Phone = %s",
                       (update_request.name, hashed_password, update_request.phone))
        db.commit()

        return {
            "message": "User updated successfully",
            "user": {"name": update_request.name, "phone": update_request.phone},
            "count": user_count
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()