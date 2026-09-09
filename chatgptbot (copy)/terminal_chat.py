from google import genai

client = genai.Client(api_key="YOUR_API_KEY")  # Replace with your actual

MODEL_NAME = "gemini-3.5-flash"
chat = client.chats.create(model=MODEL_NAME)

while True:
    message = input("You: ")

    if message.lower() == "exit":
        print("Goodbye!")
        break

    response = chat.send_message(message)

    print("Gemini: ", response.text)