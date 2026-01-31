# 📝 CHANGELOG - LingoMate AI

Toutes les modifications notables apportées au projet **LingoMate AI** sont documentées dans ce fichier.

## [1.2.0] - 2024-05-20

### ✨ Ajout de l'Intelligence Agentique & RAG

* **Implémentation du Multi-Agent Pipeline :** Migration d'un appel LLM unique vers un système orchestré (`orchestrator.py`) séparant les responsabilités (Pédagogie, Grammaire, Conversation).
* **Moteur RAG (Retrieval-Augmented Generation) :** Intégration d'une base de connaissances vectorisée dans `rag_index/` pour fournir des corrections grammaticales basées sur des sources éducatives fiables.
* **Outil de Détection de Niveau :** Création de `level_detector.py` utilisant un LLM pour classifier le niveau CEFR (A1-C2) de l'utilisateur en temps réel.

## [1.1.0] - 2024-05-10

### 🎙️ Capacités Multimodales

* **Intégration Speech-to-Text (STT) :** Support de la saisie vocale via l'API Google Speech Recognition côté backend.
* **Intégration Text-to-Speech (TTS) :** Synthèse vocale des réponses du coach avec la bibliothèque `gTTS`.
* **Optimisation Frontend :** Ajout de services RxJS dans Angular pour gérer les flux audio asynchrones.

## [1.0.0] - 2024-05-01

### 🚀 Lancement de la Version Initiale (MVP)

* **Architecture Base :** Connexion entre le frontend Angular 18 et le backend FastAPI.
* **Intégration NVIDIA NIM :** Configuration de l'accès aux modèles Llama-3.1 via l'infrastructure NVIDIA.
* **Conteneurisation :** Création du `Dockerfile` pour le déploiement standardisé du backend.
