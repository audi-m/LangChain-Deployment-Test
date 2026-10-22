from langgraph_sdk import get_sync_client

client = get_sync_client(url="http://127.0.0.1:13519")

# 1. Create a conversation thread on the server
thread = client.threads.create()

# 2. Helper: send a message and print the final reply
def ask(text):
    result = client.runs.wait(
        thread["thread_id"],
        "agent",                                     # name from langgraph.json
        input={"messages": [{"role": "user", "content": text}]},
    )
    print("AI:", result["messages"][-1]["content"])

ask("Add 3 and 4.")
ask("Multiply that by 2.")