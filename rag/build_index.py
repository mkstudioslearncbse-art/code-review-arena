# rag/build_index.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.retriever import retriever
retriever.build_index()
print("Index built successfully.")