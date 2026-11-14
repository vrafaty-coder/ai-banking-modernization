
# Import the four retrieved COBOL contexts
from rag_retriever import rag_contexts

# Prepare each context for rule extraction
for paragraph, context in rag_contexts.items():
    print(f"{paragraph}: {len(context)} characters")

# Select one context for the first Gemini test
context = rag_contexts["ROLLBACK-ACCOUNT"]

print(f"Selected context: {len(context)} characters")