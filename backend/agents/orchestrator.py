import logging
import asyncio
from typing import Dict, Any
from agents.grammar import grammar_agent
from agents.conversation import conversation_agent
from agents.pedagogy import pedagogy_agent
from rag.retriever import retrieve_context

# Configure professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

async def run_pipeline(user_text: str, level: str) -> str:
    """
    Main orchestration logic using a sequential agentic workflow.
    """
    # Initialize the "Shared State"
    state: Dict[str, Any] = {
        "user_text": user_text,
        "level": level,
        "pedagogy_plan": None,
        "rag_context": "",
        "correction": None,
        "final_response": ""
    }

    try:
        # STEP 1: Pedagogy Strategy
        logger.info(f"Step 1: Planning pedagogy for level {level}")
        state["pedagogy_plan"] = pedagogy_agent(level, user_text)

        # STEP 2: Contextual Retrieval (RAG)
        logger.info("Step 2: Retrieving RAG context")
        search_query = f"{user_text} {state['pedagogy_plan'].get('grammar_focus', '')}"
        state["rag_context"] = retrieve_context(search_query)

        # STEP 3: Grammar Audit
        logger.info("Step 3: Running Grammar Agent")
        state["correction"] = await grammar_agent(
            state["user_text"], 
            state["rag_context"], 
            state["pedagogy_plan"]
        )

        # STEP 4: Conversational Synthesis
        logger.info("Step 4: Running Conversation Agent")
        state["final_response"] = await conversation_agent(
            state["user_text"], 
            state["correction"], 
            state["pedagogy_plan"]
        )

        return state["final_response"]

    except Exception as e:
        logger.error(f"❌ Orchestrator Error: {str(e)}", exc_info=True)
        return "I'm sorry, I encountered a technical hiccup. Let's try that again!"