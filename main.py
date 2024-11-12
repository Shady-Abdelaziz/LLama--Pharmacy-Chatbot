from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dp import get_chat_history_from_db, clear_user_chat
from chatbot import generate
from utils import create_new_session, log_event
from dotenv import load_dotenv
import logging

user_sessions = {}

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.INFO)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(
    user_id: int = Form(...),
    question: str = Form(None),
    is_image: bool = Form(False),
    image: UploadFile = File(None)
):
    print(f"user_id: {user_id}, question: {question}, is_image: {is_image}, image: {image}")
    
    if user_id not in user_sessions:
        user_sessions[user_id] = create_new_session()
    session_id = user_sessions[user_id]

    log_event(f"Session {session_id} started for user {user_id}")

    try:
        if is_image and not image:
            raise HTTPException(status_code=400, detail="Image is required if 'is_image' is set to true.")
        elif not is_image and not question:
            raise HTTPException(status_code=400, detail="Please provide either a question or an image.")
        
        if is_image and image:
            image_data = await image.read()
            response = generate(input_data=image_data, user_id=user_id, session_id=session_id, is_image=True)
        else:
            response = generate(input_data=question, user_id=user_id, session_id=session_id, is_image=False)
        
        log_event(f"User {user_id} asked: {'[Image]' if is_image else question}")
        log_event(f"Assistant responded: {response}")
        
        return {"session_id": session_id, "response": response}
        
    except Exception as e:
        log_event(f"Error during chat generation for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating chat response")


@app.get("/chat_history")
async def chat_history(user_id: int):
    try:
        history = get_chat_history_from_db(user_id)
        log_event(f"Chat history retrieved for user {user_id}")
        return {"chat_history": history}
    except Exception as e:
        log_event(f"Error retrieving chat history for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving chat history")


@app.delete("/clear_chat_history")
async def clear_chat_history(user_id: int):
    try:
        clear_user_chat(user_id)
        log_event(f"Chat history for user {user_id} has been cleared.")
        return {"message": f"Chat history for user {user_id} has been cleared."}
    except Exception as e:
        log_event(f"Error clearing chat history for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error clearing chat history")
