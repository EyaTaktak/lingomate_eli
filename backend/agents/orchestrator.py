from rag.retriever import retrieve_context
from agents.grammar import grammar_agent
from agents.conversation import conversation_agent
from agents.pedagogy import pedagogy_agent

def run_pipeline(user_text, level):
    pedagogy_plan = pedagogy_agent(level, user_text)
    rag_context = retrieve_context(user_text + " " + pedagogy_plan)
    correction = grammar_agent(user_text, rag_context)
    final_response = conversation_agent(user_text, correction)

    return final_response
