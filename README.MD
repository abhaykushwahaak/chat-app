<h1 align="center">✨ Full-Stack Real-Time Chat App (FastAPI & React) ✨</h1>

## 🚀 Highlights

- 🔐 **Custom JWT Authentication** (HttpOnly cookies)
- ⚡ **Real-time Messaging** via Python Socket.IO
- 🟢 **Online/Offline Presence Indicators**
- 🔔 **Notification & Typing Sounds** (with toggle)
- 📨 **Welcome Emails on Signup** (Resend SDK)
- 🗂️ **Image Uploads** (Cloudinary)
- 🐍 **Asynchronous REST API** powered by **Python FastAPI** & Uvicorn
- 🧱 **MongoDB** with **Beanie ODM** (Motor driver) for async data persistence
- 🚦 **API Rate-Limiting** powered by **SlowAPI**
- 🎨 **Beautiful UI** built with React, Tailwind CSS & DaisyUI
- 🧠 **Zustand** for global state management
- 📖 **Auto-generated API Docs** via Swagger UI (`/docs`) & ReDoc (`/redoc`)

---

## 🛠️ Project Structure

```text
chatify/
├── backend/            # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py     # FastAPI & Socket.IO ASGI app entry point
│   │   ├── lib/        # DB, env, JWT, Cloudinary, Resend, Socket setup
│   │   ├── models/     # Beanie ODM models & Pydantic schemas
│   │   ├── middleware/ # Auth dependencies & SlowAPI rate limiting
│   │   ├── routers/    # Auth & Message route handlers
│   │   └── emails/     # Welcome email templates & handlers
│   ├── requirements.txt
│   └── .env.example
├── frontend/           # React + Vite Frontend
└── README.MD
```

---

## 🧪 Environment Variables (`backend/.env`)

Create a `.env` file inside the `backend/` directory:

```env
PORT=8000
MONGO_URI=your_mongodb_connection_string
DB_NAME=chatify

NODE_ENV=development

JWT_SECRET=your_jwt_secret

RESEND_API_KEY=your_resend_api_key
EMAIL_FROM=your_email_from_address
EMAIL_FROM_NAME=Chatify

CLIENT_URL=http://localhost:5173

CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

---

## 🔧 Run the Backend (FastAPI)

Ensure you are using **Python 3.13**.

```bash
cd backend

# 1. Create a virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows (PowerShell):
venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the FastAPI dev server
uvicorn app.main:app --reload --port 8000
```

> 💡 Interactive API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 💻 Run the Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at `http://localhost:5173`.
