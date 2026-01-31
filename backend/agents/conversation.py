from llm.nvidia_client import call_llm

def conversation_agent(user_text, correction):
    system = """
You are a friendly English conversation teacher.
Encourage the learner and continue the discussion.
"""
    messages = [
        {"role": "system", "content": system},
        {"role": "assistant", "content": correction},
        {"role": "user", "content": user_text}
    ]

    return call_llm(messages, temperature=0.4)
