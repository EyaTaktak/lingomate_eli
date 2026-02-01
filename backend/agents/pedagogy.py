def pedagogy_agent(level, user_text):
    """
    The Pedagogy Agent analyzes the user's level and text to create 
    a tailored instructional strategy for the other agents.
    """
    
    # Logic for Level A1-A2 (Beginner)
    if level in ["A1", "A2"]:
        return {
            "strategy": "Scaffolding & Encouragement",
            "vocabulary_limit": "Top 500 most common words",
            "grammar_focus": "Present Simple, basic pronouns, and 'to be'",
            "instructions": (
                "Use very simple sentences. If the user makes a mistake, "
                "correct it gently. Avoid complex idioms or phrasal verbs."
            )
        }
    
    # Logic for Level B1-B2 (Intermediate)
    elif level in ["B1", "B2"]:
        return {
            "strategy": "Expansion & Fluency",
            "vocabulary_limit": "General academic and professional terms",
            "grammar_focus": "Perfect tenses, conditionals, and connectors",
            "instructions": (
                "Encourage the user to extend their answers. Provide "
                "synonyms for common words to help them sound more natural. "
                "Correct errors related to tense consistency."
            )
        }
    
    # Logic for Level C1-C2 (Advanced)
    else:
        return {
            "strategy": "Nuance & Sophistication",
            "vocabulary_limit": "No limit; use advanced collocations",
            "grammar_focus": "Inversion, subjunctive mood, and stylistic flow",
            "instructions": (
                "Focus on 'polishing' their English. Suggest more native-like "
                "expressions. Treat the user as a peer, but keep the coaching "
                "analytical and precise."
            )
        }