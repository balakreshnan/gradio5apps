from openai import AzureOpenAI, OpenAI
import gradio as gr
from dotenv import load_dotenv
import os
from gradio import ChatMessage

#api_key = "sk-..."  # Replace with your key
#client = OpenAI(api_key=api_key)

# Load .env file
load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2024-05-01-preview"
)

def chat_function(message, history):
    history.append(ChatMessage(role="user", content=message))
    history.append(ChatMessage(role="assistant", content="Hello, how can I help you?"))
    return history

def predict(message, history):
    history_openai_format = []
    for msg in history:
        history_openai_format.append(msg)
    history_openai_format.append(message)
  
    #response = client.chat.completions.create(model='gpt-3.5-turbo',
    #messages= history_openai_format,
    #temperature=1.0,
    #stream=True)

    print(history_openai_format)

    response = client.chat.completions.create(
        model= os.getenv("AZURE_OPENAI_DEPLOYMENT"), #"gpt-4-turbo", # model = "deployment_name".
        messages=history_openai_format,
        temperature=0.0,
        top_p=0.0,
        seed=105,
        stream=True
    )

    partial_message = ""

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
              partial_message = partial_message + chunk.choices[0].delta.content
              yield partial_message

gr.ChatInterface(predict, type="messages").launch()