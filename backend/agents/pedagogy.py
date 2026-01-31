def pedagogy_agent(level, user_text):
    if level in ["A1", "A2"]:
        return "Focus on simple present, basic vocabulary."
    if level in ["B1", "B2"]:
        return "Focus on fluency and common errors."
    return "Focus on nuance and style."
