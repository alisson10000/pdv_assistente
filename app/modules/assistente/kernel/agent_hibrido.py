# app/modules/assistente/kernel/agent_hibrido.py

from app.modules.assistente.kernel.agent_sql import criar_agente_sql
from app.core.openai_client import client


# ================================================================
# 🔵 AGENTE HÍBRIDO — RAG + SQL + LLM (com logs ANSI)
# ================================================================
def agente_hibrido(db_ia, vendedor_id: int, pergunta: str, recuperar_contexto_rag):

    print("\n\033[94m==============================================================")
    print("🔵 [HÍBRIDO][INIT] Iniciando agente híbrido")
    print(f"🔵 [HÍBRIDO][INPUT] Pergunta: {pergunta}")
    print("==============================================================\033[0m")

    # ============================================================
    # 1) RAG
    # ============================================================
    print("\n\033[95m🟣 [HÍBRIDO][RAG] Executando RAG...\033[0m")

    try:
        contexto_rag = recuperar_contexto_rag(db_ia, vendedor_id, pergunta)
        print(f"\033[95m🟣 [HÍBRIDO][RAG-OK] Contexto retornado:\033[0m\n{contexto_rag}")

    except Exception as e:
        print(f"\033[91m❌ [HÍBRIDO][RAG-ERRO] Falha ao gerar contexto RAG: {e}\033[0m")
        contexto_rag = "(erro ao gerar contexto RAG)"

    # ============================================================
    # 2) SQL Agent
    # ============================================================
    print("\n\033[93m🟠 [HÍBRIDO][SQL] Chamando SQL Agent...\033[0m")

    try:
        agente_sql = criar_agente_sql()
    except Exception as e:
        print(f"\033[91m❌ [HÍBRIDO][SQL-ERRO] Falha ao inicializar SQL Agent: {e}\033[0m")
        agente_sql = None

    sql_result = {"success": False, "error": "Agente SQL indisponível"}

    if agente_sql:
        try:
            sql_result = agente_sql(pergunta)
            print(f"\033[93m🟠 [HÍBRIDO][SQL-OK] Resultado bruto:\033[0m {sql_result}")
        except Exception as e:
            print(f"\033[91m❌ [HÍBRIDO][SQL-EXEC-ERRO] {e}\033[0m")
            sql_result = {"success": False, "error": str(e)}

    # ============================================================
    # 2.1 Normalização dos dados SQL
    # ============================================================
    if not sql_result.get("success"):
        print(f"\033[93m🟠 [HÍBRIDO][SQL] SQL retornou erro. Continuando...\033[0m")

        intent = None
        cliente_nome = None
        dados_sql = f"(ERRO SQL) {sql_result.get('error')}"

    else:
        intent = sql_result.get("intent")
        cliente_nome = sql_result.get("cliente_nome")
        rows = sql_result.get("rows")

        if isinstance(rows, str):
            dados_sql = rows

        elif isinstance(rows, list):
            dados_sql = "\n".join(
                " | ".join(str(col) for col in linha)
                for linha in rows
            )

        else:
            dados_sql = "(nenhum dado retornado)"

    print("\n\033[93m🟠 [HÍBRIDO][SQL-FORMATADO] Dados SQL normalizados:\033[0m")
    print(dados_sql)

    # ============================================================
    # 3) Construção do prompt final
    # ============================================================
    print("\n\033[94m🟦 [HÍBRIDO][PROMPT] Construindo prompt final...\033[0m")

    prompt = f"""
Você é um assistente especializado em vendedores de PDV.

===================== CONTEXTO RAG =====================
{contexto_rag}

===================== INTENÇÃO DETECTADA ==============
{intent}

===================== CLIENTE DETECTADO ===============
{cliente_nome}

===================== DADOS DO SISTEMA (SQL) ==========
{dados_sql}

===================== PERGUNTA ORIGINAL ===============
{pergunta}

===================== REGRAS ==========================
- Priorize sempre dados SQL.
- Use RAG apenas como memória contextual.
- Não invente informações.
- Não exponha SQL, tabelas, colunas ou consultas internas.
- Responda sempre de maneira simples, útil e objetiva.
"""

    # ============================================================
    # 4) Execução do LLM
    # ============================================================
    print("\n\033[92m🟢 [HÍBRIDO][LLM] Chamando modelo LLM...\033[0m")

    try:
        resposta_llm = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        resposta_final = resposta_llm.choices[0].message.content
        print("\033[92m🟢 [HÍBRIDO][LLM-OK] Resposta gerada com sucesso.\033[0m")

    except Exception as e:
        print(f"\033[91m❌ [HÍBRIDO][LLM-ERRO] Falha ao chamar modelo LLM: {e}\033[0m")
        resposta_final = "Ocorreu um erro ao gerar a resposta do assistente."

    print("\n\033[92m🏁 [HÍBRIDO][FIM] Finalizado.\033[0m")

    return resposta_final
