from openai import OpenAI
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# =====================================================
#  CLIENTE OPENAI (instância única)
# =====================================================
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ ERRO: Variável OPENAI_API_KEY não encontrada no .env")

client = OpenAI(api_key=api_key)


# =====================================================
#  FUNÇÃO PARA GERAR EMBEDDINGS (normalizados)
# =====================================================
def gerar_embedding(texto: str):
    """
    Gera embedding normalizado para uso no PGVECTOR.
    Sempre retorna lista de floats normalizados.
    """

    if not texto or not texto.strip():
        # Retorna vetor zero quando texto é vazio para não quebrar o RAG
        return [0.0] * 1536

    try:
        resposta = client.embeddings.create(
            model="text-embedding-3-small",
            input=texto.strip()
        )

        vetor = np.array(resposta.data[0].embedding, dtype=float)
        norma = np.linalg.norm(vetor)

        # Normaliza (evita divisão por zero)
        vetor_norm = vetor / norma if norma != 0 else vetor

        return vetor_norm.tolist()

    except Exception as e:
        print("❌ Erro ao gerar embedding:", e)
        # Evitar quebra total caso a API falhe
        return [0.0] * 1536


# =====================================================
#  FUNÇÃO PARA OBTER O CLIENTE DE CHAT
# =====================================================
def get_client():
    """
    Retorna a instância do cliente OpenAI.
    Útil para abstrair implementações futuras.
    """
    return client
