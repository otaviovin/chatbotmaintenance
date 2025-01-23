import os
from langchain_openai import OpenAIEmbeddings 
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import traceback
from dotenv import load_dotenv

# Load the .env file containing the API key (dotenv package)
load_dotenv()
print(f"Loading API key...")
# Retrieve the OpenAI API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
# If the API key is successfully found, show the first 5 characters; otherwise, print a message
print(f"API Key loaded: {openai_api_key[:5]}..." if openai_api_key else "API Key not found!")

def load_documents(data_dir='data'):
    """
    Load text documents from the specified directory.
    Reads all '.txt' files from the given folder and returns their contents as a list of strings.
    """
    documents = []
    if not os.path.exists(data_dir):
        print(f"Directory '{data_dir}' not found.")  # If the folder doesn't exist, raise an error
        raise ValueError(f"Directory '{data_dir}' not found.")
    
    # Loop through all files in the directory and load text files
    for file_name in os.listdir(data_dir):
        if file_name.endswith('.txt'):  # Only process text files
            file_path = os.path.join(data_dir, file_name)
            print("File path found!")  # Log message indicating the file path is found
            with open(file_path, 'r', encoding='utf-8') as txt_file:
                text = txt_file.read()  # Read the file content
                documents.append(text)  # Append the content to the documents list
                print("File opened!")  # Log message indicating the file is opened
    return documents  # Return the list of document contents


def initialize_qa_chain():
    """
    Initializes the question-answer chain using LangChain and OpenAI.
    This function loads documents, processes them, and sets up the QA chain with a vector store.
    """
    documents = load_documents()  # Load the documents from the data directory
    if not documents:
        print("No '.txt' files found in the 'data' folder.")  # If no documents found, raise an error
        raise ValueError("No '.txt' files found in the 'data' folder.")

    # Use RecursiveCharacterTextSplitter to better control the text chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = []
    for doc in documents:
        chunks = text_splitter.split_text(doc)  # Split the document into smaller chunks
        if chunks:
            texts.extend(chunks)  # Add the chunks to the texts list

    if not texts:
        print("No text generated after splitting documents.")  # If no chunks were generated, raise an error
        raise ValueError("No text generated after splitting documents.")
    
    # Retrieve the OpenAI API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("OpenAI API key not found.")  # If API key is not found, raise an error
        raise ValueError("OpenAI API key not found.")
    print(f"API Key loaded: {openai_api_key[:5]}...")  # Show the first 5 characters of the key for confirmation

    # Initialize OpenAI embeddings using the API key
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    # Create a Chroma vector store from the text chunks
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        persist_directory="chroma_storage"  # Directory where the vector store will be saved
    )
    print("Using embeddings")

    # Initialize the ChatOpenAI model with GPT-3.5
    llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)
    # Create the QA chain using the vector store and the language model
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        return_source_documents=True  # Return the source documents along with the answer
    )
    print("Using LLM (Language Model)")
    return qa_chain  # Return the initialized QA chain


def ask_question(question):
    """
    Processes a question by passing it to the QA chain and returning the answer.
    Handles errors and logs detailed error information if something goes wrong.
    """
    try:
        qa_chain = initialize_qa_chain()  # Initialize the QA chain
        result = qa_chain({"query": question})  # Ask the question and get the result
        answer = result.get("result", "No answer found.")  # Get the answer from the result
        return {'answer': answer}  # Return the answer in a dictionary
    except Exception as e:
        error_details = traceback.format_exc()  # Capture the full traceback for error logging
        print(f"Error processing the question: {error_details}")  # Print detailed error information
        return {'error': f"An error occurred while processing the question: {str(e)}"}  # Return the error in a dictionary


# Example usage of the QA system
if __name__ == "__main__":
    question = "What is the purpose of this system?"  # Example question
    response = ask_question(question)  # Ask the question and get the response
    print(response)  # Print the response
