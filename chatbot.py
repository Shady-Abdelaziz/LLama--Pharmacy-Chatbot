from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from dp import save_to_db, get_chat_history_from_db
from utils import create_new_session, log_event
from langchain_community.vectorstores import FAISS
from langchain.load import dumps, loads
import pytesseract
from PIL import Image
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_PROJECT'] = 'advanced-rag'
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")

if not os.getenv("LANGCHAIN_API_KEY") or not os.getenv("GROQ_API_KEY"):
    raise EnvironmentError("API keys are missing. Please set them in the .env file.")

doc_path = "/mnt/d/data science/pharmacy/drug_descriptions2.txt"
with open(doc_path, 'r', encoding='utf-8') as file:
    text = file.read()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
chunks = text_splitter.split_text(text)

model_name = "BAAI/bge-small-en"
hf_embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={"device": "cpu"}, encode_kwargs={"normalize_embeddings": True})
sample_chunk = chunks[:1000]

vectorstore = FAISS.from_texts(texts=sample_chunk, embedding=hf_embeddings)
retriever = vectorstore.as_retriever()

llm = ChatGroq(model="llama3-70b-8192", temperature=0.5)

template = """
You are a pharmacy assistant chatbot. You can:
1. Provide information about medications, including their uses and prices, but only based on the available data provided.
2. Suggest over-the-counter medications for common symptoms, like headaches or allergies, only if relevant information is found in the provided context.
3. Check the availability of products in the pharmacy's inventory. If the information is not available in the context, reply with 'It's not available right now.'
4. Do not generate any information that is not directly provided in the available data. If the context does not contain the answer, respond with 'I don't have that information right now.'

The available information is: {context}

The question is: {question}
"""
prompt = PromptTemplate(input_variables=["question", "context"], template=template)
output_parser = StrOutputParser()

def photo_text(image_path):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    image = Image.open(image_path)
    return pytesseract.image_to_string(image, lang='eng').strip()

def reciprocal_rank_fusion(results: list[list], k=60):
    fused_scores = {}
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            fused_scores[doc_str] = fused_scores.get(doc_str, 0) + 1 / (rank + k)

    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]
    return reranked_results[:3]


def generate(input_data, user_id, session_id, is_image=False):
    log_event(f"Session {session_id} started for user {user_id}")
    if is_image:
        question = photo_text(input_data)
        if not question:
            log_event("No text detected in the image.")
            return "No question provided in the image."
    else:
        question = input_data
    
    log_event(f"User {user_id} question: {question}")

    try:
        chat_history = get_chat_history_from_db(user_id)
        log_event(f"Retrieved chat history for user {user_id}")
        log_event(f"Chat History Content: {chat_history}")
    except Exception as e:
        log_event(f"Error retrieving chat history for user {user_id}: {str(e)}")
        return "Error retrieving chat history."

    try:
        docs = retriever.get_relevant_documents(question)
        log_event(f"Retrieved {len(docs)} relevant documents for user {user_id}")
    except Exception as e:
        log_event(f"Error retrieving documents for question '{question}': {str(e)}")
        return "Error retrieving relevant documents."

    try:
        reranked_docs = reciprocal_rank_fusion([docs])
        log_event(f"Reranked documents for user {user_id}")
        log_event(f"Reranked Docs Content: {reranked_docs}")
    except Exception as e:
        log_event(f"Error during reranking documents: {str(e)}")
        return "Error processing document ranking."

    try:
        context_docs = "\n".join([doc[0].page_content for doc in reranked_docs if doc[0].page_content]) if reranked_docs else "No relevant data available."
        
        previous_conversations = "\n".join([f"User: {msg['user_message']}\nAssistant: {msg['assistant_response']}" for msg in chat_history if msg['user_message'] and msg['assistant_response']])
        
        context = f"{previous_conversations}\n\n{context_docs}" if previous_conversations else context_docs
        log_event(f"Context for response prepared for user {user_id}")
    except Exception as e:
        log_event(f"Error preparing context for user {user_id}: {str(e)}")
        return "Error preparing response context."

    try:
        full_input = prompt.format(question=question, context=context)
        message = HumanMessage(content=full_input)
        log_event(f"Prompt created for user {user_id}")
    except Exception as e:
        log_event(f"Error creating prompt for user {user_id}: {str(e)}")
        return "Error creating prompt."
    try:
        response = llm([message])
        parsed_response = output_parser.parse(response.content)
        log_event(f"Response generated for user {user_id}")
    except Exception as e:
        log_event(f"Error generating response from LLM for user {user_id}: {str(e)}")
        return "Error generating response from language model."

    try:
        save_to_db(user_id, question, parsed_response, session_id=session_id)
        log_event(f"Saved chat history for user {user_id}")
    except Exception as e:
        log_event(f"Error saving chat history for user {user_id}: {str(e)}")
        return "Error saving chat history."

    return parsed_response


