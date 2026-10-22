from dotenv import load_dotenv
load_dotenv()
import random
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")
llm_with_tools = llm.bind_tools([multiply])

result = llm_with_tools.invoke([HumanMessage(content="What is 2 multiplied by 3?", name="Lance")])
print(result)
# 1. STATE: the shared object passed between nodes
class State(TypedDict):
    graph_state: str

# 2. NODES: plain functions that read state and return updates 
def node_1(state):
    print("---Node 1-------")
    return {"graph_state": state["graph_state"] +  " I am"}
def node_2(state):
    print("---Node 2---")
    return {"graph_state": state["graph_state"] + " happy!"}
def node_3(state):
    print("---Node 3---")
    return {"graph_state": state["graph_state"] + " sad!"}

# 3. CONDITIONAL EDGE: a function that returns the NAME of the next node
def decide_mood(state) -> Literal["node_2", "node_3"]:
    return "node_2" if random.random() < 0.5 else "node_3"

# 4. BUILD THE GRAPH
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

builder.add_edge(START, "node_1")                       # normal edge
builder.add_conditional_edges("node_1", decide_mood)    # conditional edge
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

graph = builder.compile()

# 5. RUN IT
print(graph.invoke({"graph_state": "Hi, this is Lance."}))