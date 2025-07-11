from langgraph.graph import StateGraph,MessagesState, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, Literal, TypedDict
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from LLMS.groqllm import LLM1
from Models.models import parser
from tools.tools import get_store_stock,buy_from_store,update_inventory,transfer_item_between_stores
from tools.inventory_tools import get_inventory_stock
from tools.recipe_tools import mealdb_recipe_search
from Vector_Store.rag_stuff import retriever_tool
from typing import Dict, Any, Literal
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
class Budget_Friendly_Chatbot:
    def __init__(self):
        self.llm=LLM1
    def call_tool(self):
        tools=[get_inventory_stock]
        self.tool_node=ToolNode(tools=[get_inventory_stock])
        self.llm_with_tool=self.llm.bind_tools(tools)
    def call_model(self,state:MessagesState):
        messages=state['messages']
        response=self.llm_with_tool.invoke(messages)
        return {"messages":[response]}
    def router_function(self,state:MessagesState)->Literal["tools", END]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
    def generate_shopping_node(self,state:MessagesState):
        messages=state['messages']
        last_tool_response=messages[-1].content
        prompt = f"""
        You are a budget-friendly shopping assistant.
        Your task is to help the user maximize their shopping within a given budget.
        
        Instructions:
        - Carefully read the user's request to determine the total amount (budget) they want to spend.
        - Use the inventory data provided (including product name, brand, price, and description).
        - Generate a list of all possible grocery items the user can buy such that the total combined price does not exceed the specified budget.
        - Try to maximize the number and variety of items within the budget.
        - For each item, list the brand, product name, price, and description.
        - If there are multiple combinations, choose the one that includes the most items, or the best value for the user.
        - If the user specifies a category (e.g., dairy, snacks), only include items from that category.
        - If the user does not specify a category, consider all items in the inventory.
        - Present the list in a clear tabular format.
        - when your presenting the result you should mention brand name and quantity of item 
        - At the end, show the total price of the selected items.

        Example:
        User: "I want to buy groceries under 200 rupees."
        Output:
         Brand,
         product
         quantity of product
         price of product
         sample_syntax=2 litres of amul, 1packet of 500 gram amul cheese
        Now, based on the user's latest message and the inventory data, generate the complete list of items the user can buy within their specified budget.
    """
    def __call__(self):
        self.call_tool()
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("shop", self.generate_shopping_node) 
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent",self.router_function,{"tools": "tools", END: END})
        workflow.add_edge("tools", 'shop')
        workflow.add_edge("shop","agent")
        self.app = workflow.compile()
        return self.app    
    
class Stock_Analyzer_chatbot:
    def __init__(self):
        self.llm=LLM1
    def call_tool(self):
        tools=[get_store_stock,buy_from_store,update_inventory,transfer_item_between_stores]
        self.tool_node=ToolNode(tools=[get_store_stock,buy_from_store,update_inventory,transfer_item_between_stores])
        self.llm_with_tool=self.llm.bind_tools(tools)

    def call_model(self,state:MessagesState):
        messages=state['messages']
        response=self.llm_with_tool.invoke(messages)
        return {"messages":[response]}
    def router_function(self,state:MessagesState)->Literal["tools", END]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
    def generate_invoice_node(self,state:MessagesState):
        messages=state['messages']
        last_tool_response=messages[-1].content
        prompt=f"""
           You are an assistant that generates detailed invoice reports based on tool activity.
           Extract structured invoice info from the following transaction summary:
           Respond in this format:
           {parser.get_format_instructions()}
        """
    def __call__(self):
        self.call_tool()
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("invoice", self.generate_invoice_node) 
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent",self.router_function,{"tools": "tools", END: END})
        workflow.add_edge("tools", 'invoice')
        workflow.add_edge("invoice","agent")
        self.app = workflow.compile()
        return self.app
class Recipe_Generator_Chatbot:
    def __init__(self):
        self.llm = LLM1
        # Initialize memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
    def call_tool(self):
        tools = [mealdb_recipe_search, retriever_tool]
        self.tool_node = ToolNode(tools=[mealdb_recipe_search, retriever_tool])
        self.llm_with_tool = self.llm.bind_tools(tools)
        
    def call_model(self, state: Dict[str, Any]):
        # Get messages from state and add memory
        messages = state['messages']
        
        # Add chat history from memory
        chat_history = self.memory.load_memory_variables({})['chat_history']
        full_conversation = chat_history + messages
        
        # Generate response
        response = self.llm_with_tool.invoke(full_conversation)
        
        # Update memory
        for message in messages:
            if isinstance(message, HumanMessage):
                self.memory.chat_memory.add_user_message(message.content)
        if isinstance(response, AIMessage):
            self.memory.chat_memory.add_ai_message(response.content)
            
        return {"messages": [response]}
        
    def router_function(self, state: Dict[str, Any]) -> Literal["tools", END]:
        messages = state['messages']
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return END
        
    def __call__(self):
        self.call_tool()
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)
        
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            self.router_function,
            {"tools": "tools", END: END}
        )
        workflow.add_edge("tools", "agent")
        
        self.app = workflow.compile()
        return self.app
        
    def clear_memory(self):
        """Clear the conversation memory"""
        self.memory.clear()
    def __init__(self):
        self.llm=LLM1
    def call_tool(self):
        tools=[mealdb_recipe_search,retriever_tool]
        self.tool_node=ToolNode(tools=[mealdb_recipe_search,retriever_tool])
        self.llm_with_tool=self.llm.bind_tools(tools)
    def call_model(self,state:MessagesState):
        messages=state['messages']
        response=self.llm_with_tool.invoke(messages)
        return {"messages":[response]}
    def router_function(self,state:MessagesState)->Literal["tools",END]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
    def __call__(self):
        self.call_tool()
        workflow=StateGraph(MessagesState)
        workflow.add_node("agent",self.call_model)
        workflow.add_node("tools",self.tool_node)
        workflow.add_edge(START,"agent")
        workflow.add_conditional_edges("agent",self.router_function,{"tools": "tools", END: END})
        workflow.add_edge("tools","agent")
        self.app=workflow.compile()
        return self.app
class UnifiedChatbot:
    def __init__(self):
        self.budget_bot = Budget_Friendly_Chatbot()()
        self.stock_bot = Stock_Analyzer_chatbot()()
        self.recipe_bot = Recipe_Generator_Chatbot()()  
    def router_function(self, state: MessagesState) -> Literal["budget", "stock", "recipe"]:
        last_msg = state['messages'][-1].content.lower()
        if any(word in last_msg for word in ["buy", "grocery", "shopping", "budget"]):
            return "budget"
        elif any(word in last_msg for word in ["stock", "store", "inventory", "transfer", "invoice"]):
            return "stock"
        elif any(word in last_msg for word in ["recipe", "cook", "meal", "ingredients"]):
            return "recipe"
        return "budget"
    def __call__(self):
       workflow = StateGraph(MessagesState)
       workflow.add_node("budget", self.budget_bot)
       workflow.add_node("stock", self.stock_bot)
       workflow.add_node("recipe", self.recipe_bot)
       workflow.add_conditional_edges(START, self.router_function, {
        "budget": "budget",
        "stock": "stock",
        "recipe": "recipe"
       })
       workflow.add_edge("budget", END)
       workflow.add_edge("stock", END)
       workflow.add_edge("recipe", END)
       return workflow.compile()
if __name__=="__main__":
    # mybot=chatbot()
    # workflow=mybot()
    # response=workflow.invoke({"messages":["Check the stock details of store1 and store2 and also do some analysis"]})
    # print(response["messages"][-1].content)
    unified_bot = UnifiedChatbot()
    workflow = unified_bot()
    response=workflow.invoke({"messages":[HumanMessage("show me the recipe of dal fry")]})
    print(response["messages"][-1].content)
