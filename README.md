# LLama-Powered Pharmacy Chatbot

An advanced, LLama- pharmacy assistant chatbot designed with **FastAPI**, **LangChain**, **FAISS**, and **SQLite** to provide personalized, up-to-date medication information. This chatbot can help users with medication inquiries, including details on usage, pricing, and availability. Each user session is tracked with a unique **UUID**, ensuring isolated, secure conversations and personalized interaction histories. The chatbot utilizes **FAISS** for rapid retrieval of relevant information and leverages **LLama 3** via **LangChain** to generate intelligent, contextually aware responses.

## Features

- **Pharmacy Assistance**: Supplies information on medications, suggests over-the-counter options for common symptoms, and answers general drug-related queries.
- **Efficient Document Retrieval**: Uses **FAISS** for optimized retrieval of medication descriptions and relevant information.
- **Contextual Response Generation**: Powered by **LLama 3** and **LangChain** for understanding and responding accurately to user questions.
- **Session-Based Storage**: Employs **SQLite** to store chat histories per session, allowing users to continue previous conversations seamlessly.
- **Unique Session Tracking**: Each user interaction is tagged with a **UUID**, ensuring that all chat histories are maintained separately and securely.
- **RESTful API with FastAPI**: Provides accessible endpoints for chatbot interaction, session management, and data retrieval.

## Technologies Used

- **FastAPI**: A high-performance web framework for building RESTful APIs.
- **LangChain**: A powerful framework for handling large language models (LLMs) and designing effective prompts.
- **FAISS**: An indexing library for fast similarity search, used to retrieve accurate medication details.
- **LLama 3 (ChatGroq)**: Large Language Model (LLM) used for generating accurate, conversational responses.
- **SQLite**: Lightweight database for storing user interactions and session data.
- **Python**: Core programming language for development.
- **UUID**: Ensures unique identification of each user session for privacy and organization.

## Setup and Installation

Follow the steps below to set up and install the AI-powered pharmacy chatbot locally:

### 1. Clone the repository
First, clone the repository to your local machine 

### 2. Create a virtual environment (optional but recommended)

It's recommended to create a virtual environment to manage dependencies:


### 3. Install the required dependencies

Install the required dependencies using pip: pip install -r requirements.txt


### 4. Setup the SQLite database

The chatbot stores user session data in an SQLite database. To set up the database: python setup_db.py

### 5. Run the FastAPI server

uvicorn app.main:app --reload

This will start the API locally at `http://127.0.0.1:8000`. The chatbot will be ready to interact via the provided endpoints.

### 6. Access the API Documentation

FastAPI automatically generates interactive API documentation using Swagger UI. You can access it by navigating to: http://127.0.0.1:8000/docs



## Endpoints

The API offers several endpoints for chatbot interactions and session management:

- **POST /chat/{user_id}**: Send a query to the chatbot and receive a response.
- **GET /session/{user_id}**: Retrieve the chat history of a specific user session.
- **POST /session**: Create a new user session with a unique UUID.
- **DELETE /session/{user_id}**: End a user session and clear the stored data.


## Contributing

Contributions to the project are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Commit your changes and push them to your fork.
4. Open a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **FastAPI**: For building the API framework.
- **LangChain**: For handling large language models and prompt management.
- **FAISS**: For fast similarity search capabilities.
- **SQLite**: For lightweight session storage.
- **LLama 3 (ChatGroq)**: For generating conversational AI responses.
