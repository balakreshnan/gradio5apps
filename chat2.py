import gradio as gr
import time
from openai import AzureOpenAI, OpenAI
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


def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)


def add_message(history, message):
    for x in message["files"]:
        history.append({"role": "user", "content": {"path": x}})
    if message["text"] is not None:
        history.append({"role": "user", "content": message["text"]})
    return history, gr.MultimodalTextbox(value=None, interactive=False)


def bot(history: list):
    #response = "**That's cool!**"
    history.append({"role": "assistant", "content": ""})
    #for character in response:
    #    history[-1]["content"] += character
    #    time.sleep(0.05)

    #print(history)

    # record the time before the request is sent
    start_time = time.time()

    response = client.chat.completions.create(
        model= os.getenv("AZURE_OPENAI_DEPLOYMENT"), #"gpt-4-turbo", # model = "deployment_name".
        messages=history,
        temperature=0.0,
        top_p=0.0,
        seed=105,
        stream=True
    )
    #print(response)
    partial_message = ""

    # create variables to collect the stream of chunks
    collected_chunks = []
    collected_messages = []
    # iterate through the stream of events
    for chunk in response:
        chunk_time = time.time() - start_time  # calculate the time delay of the chunk
        collected_chunks.append(chunk)  # save the event response
        #print(chunk)
        #print('')
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content)
            chunk_message = chunk.choices[0].delta.content  # extract the message
            collected_messages.append(chunk_message)  # save the message
            print(f"Message received {chunk_time:.2f} seconds after request: {chunk_message}")  # print the delay and text
            print(f"Message received {chunk_time:.2f} seconds after request: {chunk.choices[0].delta.content}")  # print the delay and text
            history[-1]["content"] += chunk.choices[0].delta.content


    # print the time delay and text received
    print(f"Full response received {chunk_time:.2f} seconds after request")
    # clean None in collected_messages
    collected_messages = [m for m in collected_messages if m is not None]
    full_reply_content = ''.join(collected_messages)
    print(f"Full conversation received: {full_reply_content}")
    #for chunk in response:
    #    if 'choices' in chunk:
    #        history[-1]["content"] += chunk['choices'][0]['delta'].get('content', '')
    #for chunk in response:
    #    print(chunk)
    #    print(chunk.choices[0].delta.content)
    #    print("****************")
    #    history[-1]["content"] += chunk.choices[0].delta.content
    
    yield history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(elem_id="chatbot", bubble_full_width=False, type="messages", height=800)

    chat_input = gr.MultimodalTextbox(
        interactive=True,
        file_count="multiple",
        placeholder="Enter message or upload file...",
        show_label=False,
    )

    chat_msg = chat_input.submit(
        add_message, [chatbot, chat_input], [chatbot, chat_input]
    )
    bot_msg = chat_msg.then(bot, chatbot, chatbot, api_name="bot_response")
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

    chatbot.like(print_like_dislike, None, None, like_user_message=True)

demo.launch()