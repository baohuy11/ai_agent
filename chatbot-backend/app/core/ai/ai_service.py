from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from typing import List, Dict, AsyncGenerator, Any
from dotenv import load_dotenv
from app.database.chat_history_service import save_chat_history, get_recent_chat_history, format_chat_history
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessageChunk
from langchain.callbacks.base import BaseCallbackHandler
from .tools import ProductSearchTool, CreateOrderTool, UpdateOrderStatusTool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Create tools
product_search_tool = ProductSearchTool()
create_order_tool = CreateOrderTool()
update_order_status_tool = UpdateOrderStatusTool()

class CustomHandler(BaseCallbackHandler):
    """
    Lớp xử lý callback tùy chỉnh để theo dõi và xử lý các sự kiện trong quá trình chat
    """
    def __init__(self):
        super().__init__()

def get_llm_and_agent() -> AgentExecutor:
    system_message = """

You are a friendly and professional healthcare assistant bot. Your primary task is to help users by collecting information about their symptoms, providing possible diagnoses with likelihood percentages, and refining the results by asking follow-up questions.

For general greetings and inquiries:
    - Respond naturally and empathetically
    - Start by asking, "How are you feeling today?" or a similar question to understand the user's health
    
For symptom-based diagnosis:
    1. When the user describes their symptoms:
        - Gather all symptoms clearly and confirm with the user if needed
        - Use the provided symptoms to generate a list of 5 possible diseases
        - Provide the diseases in a clear format with likelihood percentages (out of 100)
        - Present a disclaimer: "These are possible conditions based on your symptoms and not a substitute for professional medical advice."
        
    2. After providing initial diagnoses:
        - Ask follow-up questions related to the symptoms to gather more specific information (e.g., duration of symptoms, severity, additional signs)
        - Adjust the likelihood percentages based on the user's answers to these follow-up questions
        - Update and present the revised list of 5 possible diseases with updated percentages
        
For critical or urgent symptoms:
    - If symptoms suggest a serious condition (e.g., chest pain, difficulty breathing, severe headache), recommend immediate consultation with a healthcare professional or visiting the nearest emergency facility.
    
IMPORTANT RULES:
    - Always maintain an empathetic and professional tone
    - Never make a definitive diagnosis; only provide likely possibilities
    - Clearly indicate that the chatbot's information is not a replacement for professional medical advice
    - Ensure all follow-up questions are relevant and designed to refine the diagnosis
    - Prioritize user safety by emphasizing the need for professional care in critical cases
    
Example flow:
1. User: "I don't feel well today."
2. Bot: "I'm sorry to hear that. Could you please tell me more about your symptoms?"
3. User: "I have a headache, fever, and sore throat."
4. Bot:
    - "Based on your symptoms, here are some possible conditions you might have:
        - Flu (70%)
        - Common Cold (15%)
        - Strep Throat (10%)
        - Covid-19 (4%)
        - Sinusitis (1%)"
    - "These are just possibilities. Could you tell me how long you've been experiencing these symptoms?"
5. User: "It started about three days ago."
6. Bot:
    - "Thanks for sharing. Let me adjust the results based on this information."
        - Updated response: "Here is the revised list:
        - Flu (75%)
        - Common Cold (10%)
        - Strep Throat (8%)
        - Covid-19 (6%)
        - Sinusitis (1%)"
    - "If your symptoms persist or worsen, I recommend consulting a healthcare professional. Would you like more advice or information?"""
    
    chat = ChatOpenAI(
        temperature=0, 
        streaming=True, 
        model="gpt-4", 
        api_key=OPENAI_API_KEY,
        callbacks=[CustomHandler()]
    )
    
    tools = [
        product_search_tool,
        create_order_tool,
        update_order_status_tool
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_functions_agent(
        llm=chat,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        return_intermediate_steps=True
    )

    return agent_executor

def get_answer(question: str, thread_id: str) -> Dict:
    """
    Hàm lấy câu trả lời cho một câu hỏi
    
    Args:
        question (str): Câu hỏi của người dùng
        thread_id (str): ID của cuộc trò chuyện
        
    Returns:
        str: Câu trả lời từ AI
    """
    agent = get_llm_and_agent()
    
    # Get recent chat history
    history = get_recent_chat_history(thread_id)
    chat_history = format_chat_history(history)
    
    result = agent.invoke({
        "input": question,
        "chat_history": chat_history
    })
    
    # Save chat history to database
    if isinstance(result, dict) and "output" in result:
        save_chat_history(thread_id, question, result["output"])
    
    return result

async def get_answer_stream(question: str, thread_id: str) -> AsyncGenerator[Dict, None]:
    """
    Hàm lấy câu trả lời dạng stream cho một câu hỏi
    
    Quy trình xử lý:
    1. Khởi tạo agent với các tools cần thiết
    2. Lấy lịch sử chat gần đây
    3. Gọi agent để xử lý câu hỏi
    4. Stream từng phần của câu trả lời về client
    5. Lưu câu trả lời hoàn chỉnh vào database
    
    Args:
        question (str): Câu hỏi của người dùng
        thread_id (str): ID phiên chat
        
    Returns:
        AsyncGenerator[str, None]: Generator trả về từng phần của câu trả lời
    """
    # Khởi tạo agent với các tools cần thiết
    agent = get_llm_and_agent()
    
    # Lấy lịch sử chat gần đây
    history = get_recent_chat_history(thread_id)
    chat_history = format_chat_history(history)
    
    # Biến lưu câu trả lời hoàn chỉnh
    final_answer = ""
    
    # Stream từng phần của câu trả lời
    async for event in agent.astream_events(
        {
            "input": question,
            "chat_history": chat_history,
        },
        version="v2"
    ):       
        # Lấy loại sự kiện
        kind = event["event"]
        # Nếu là sự kiện stream từ model
        if kind == "on_chat_model_stream":
            # Lấy nội dung token
            content = event['data']['chunk'].content
            if content:  # Chỉ yield nếu có nội dung
                # Cộng dồn vào câu trả lời hoàn chỉnh
                final_answer += content
                # Trả về token cho client
                yield content
    
    # Lưu câu trả lời hoàn chỉnh vào database
    if final_answer:
        save_chat_history(thread_id, question, final_answer)

if __name__ == "__main__":
    import asyncio
    
    async def test():
        # answer = get_answer_stream("hi", "test-session")
        # print(answer)
        async for event in get_answer_stream("hi", "test-session"):
            print('event:', event)
        print('done')

    
    asyncio.run(test())

