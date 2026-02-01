from llm.nvidia_client import call_llm

def conversation_agent(user_text, correction):
    system = """
Your name is Lin.
You are a friendly English conversation teacher .
Encourage the learner and continue the discussion.
At the end of your response, include a question to keep the conversation going.
"""
    messages = [
        {"role": "system", "content": system},
        {"role": "assistant", "content": correction},
        {"role": "user", "content": user_text}
    ]

    return call_llm(messages, temperature=0.4)
