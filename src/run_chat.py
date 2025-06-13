from qa_bot.core.agent import generate_response

def main():
    print("Welcome to the GEO Help Guide Chatbot!")
    print("Type 'exit' to end the session.\n")

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ['exit', 'quit']:
            print("Exiting chat. Goodbye!")
            break

        try:
            response = generate_response(user_input)
            print(f"Bot: {response}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()