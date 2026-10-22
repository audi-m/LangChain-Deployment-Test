from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
import langgraph_api.logging
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


# Node 1: the LLM decides whether to call a tool
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")
llm_with_tools = llm.bind_tools([multiply])
memory = MemorySaver()
# build the graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([multiply]))     # Node 2: runs the tool
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",
    tools_condition,     # routes to "tools" if there's a tool call, otherwise to END
)
builder.add_edge("tools", END)
graph = builder.compile()
config = {"configurable": {"thread_id": "1"}}

# First turn
out = graph.invoke({"messages": [HumanMessage(content="Add 3 and 4.")]}, config)
out["messages"][-1].pretty_print()
# → "The sum of 3 and 4 is 7."

# Second turn, same thread
out = graph.invoke({"messages": [HumanMessage(content="Multiply that by 2.")]}, config)
out["messages"][-1].pretty_print()


# Second turn, same thread
out = graph.invoke({"messages": [HumanMessage(content="minus 2.")]}, config)
for m in out["messages"]:
    m.pretty_print()
