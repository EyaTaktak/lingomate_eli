from llm.nvidia_client import call_llm

def grammar_agent(user_text, context, explain=False):
    system = f"""
You are a grammar correction agent.
Correct the sentence only if it is false.
Do NOT explain or give extra details unless asked.
Use this context if needed:
{context}
"""
    if explain:
        system += "\nIf the user asks, provide brief pedagogical explanations."

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_text}
    ]

    return call_llm(messages)
