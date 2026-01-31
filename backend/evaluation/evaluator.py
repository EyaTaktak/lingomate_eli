import json
from sentence_transformers import SentenceTransformer, util
import sys
from pathlib import Path

# Ajouter le dossier parent (backend) au sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Maintenant on peut importer

from agents.orchestrator import run_pipeline

# Charger le modèle d'embeddings pour la similarité
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Charger le dataset de test
with open("test_dataset.json", "r", encoding="utf-8") as f:
    test_data = json.load(f)

def evaluate():
    total = len(test_data)
    semantic_scores = []

    for item in test_data:
        question = item["question"]
        expected = item["expected_answer"]
        level = "beginner"  # Niveau par défaut

        # Générer la réponse via ton pipeline
        generated_answer = run_pipeline(question, level) 

        # Calculer la similarité cosine
        score = util.cos_sim(
            embed_model.encode(expected),
            embed_model.encode(generated_answer)
        ).item()
        semantic_scores.append(score)

        print(f"Q: {question}")
        print(f"Expected: {expected}")
        print(f"Generated: {generated_answer}")
        print(f"Similarity Score: {score:.3f}\n")

    # Score moyen
    mean_score = sum(semantic_scores) / total
    print(f"=== Average Semantic Similarity: {mean_score:.3f} ===")

if __name__ == "__main__":
    evaluate()
