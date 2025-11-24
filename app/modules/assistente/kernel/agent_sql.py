# app/modules/assistente/kernel/agent_sql.py

from sqlalchemy import text
import traceback
from app.core.openai_client import client
from app.core.database_pdv import engine_pdv

# ============================================================
#  ANSI COLORS
# ============================================================
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
PURPLE = "\033[95m"
RESET  = "\033[0m"


def log_info(msg):     print(f"{BLUE}[SQL][INFO]{RESET} {msg}")
def log_warn(msg):     print(f"{YELLOW}[SQL][WARN]{RESET} {msg}")
def log_success(msg):  print(f"{GREEN}[SQL][OK]{RESET} {msg}")
def log_error(msg):    print(f"{RED}[SQL][ERRO]{RESET} {msg}")


# ==================================================================
#   SQL AGENT — cria uma função callable
# ==================================================================
def criar_agente_sql():

    log_info("Inicializando SQL Agent")
    log_info(f"Conectando ao PDV: {engine_pdv.url}")

    # ==================================================================
    #  FUNÇÃO INTERNA — o verdadeiro agente SQL
    # ==================================================================
    def agente_sql(pergunta: str):

        print("\n" + BLUE + "--------------------------------------------------------")
        print(f"[SQL][CALL] Pergunta recebida: {pergunta}")
        print("--------------------------------------------------------" + RESET)

        try:
            # ==================================================================
            # 1) Extrair nome do cliente
            # ==================================================================
            nome_detectado = (
                pergunta.lower()
                .replace("dados de", "")
                .replace("informações de", "")
                .replace("compras de", "")
                .replace("cliente", "")
                .replace("compra", "")
                .strip()
            )

            if nome_detectado:
                log_warn(f"[SQL][NOME] Nome detectado via heurística: {nome_detectado}")

            # ==================================================================
            # 2) Intent via LLM
            # ==================================================================
            intent_prompt = f"""
Você é um especialista em SQL para um banco de PDV.
Com base na pergunta do vendedor, responda apenas com a intenção principal:

Pergunta: "{pergunta}"

Intenções possíveis:
- dados_cliente
- compras_cliente
- endereco_cliente
- telefones_cliente
- produtos_cliente
- status_pedido

Responda apenas com UMA palavra da lista acima.
"""

            intent_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": intent_prompt}]
            )
            intent = intent_resp.choices[0].message.content.strip()

            log_info(f"[SQL][INTENÇÃO] {intent}")

            # ==================================================================
            # 3) Gerar SQL via LLM
            # ==================================================================
            sql_prompt = f"""
Gere uma consulta SQL **válida para PostgreSQL**, SEM usar SELECT *.

NUNCA use blocos Markdown.
NÃO use ```sql ou ```.

Pergunta: "{pergunta}"
Intenção: {intent}
Cliente identificado: {nome_detectado}

Tabelas disponíveis:
- cliente(id, nome, cpf, email, numero, telefone, endereco_id, complemento)
- pedido(id, data_pedido, id_cliente, status)
- itens_pedido(id, id_pedido, id_produto, quantidade, valor_venda, desconto)
- produto(id, nome, descricao, preco, categoria_id)

Responda SOMENTE com a SQL pura.
"""

            sql_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": sql_prompt}]
            )

            sql_text = sql_resp.choices[0].message.content.strip()

            # ==================================================================
            # 4) Remover ``` e lixo do modelo (CORREÇÃO CRÍTICA)
            # ==================================================================
            sql_text = (
                sql_text.replace("```sql", "")
                        .replace("```", "")
                        .strip()
            )

            log_success("[SQL][GERAR-OK] SQL gerada limpa:")
            print(sql_text)

            # Anti SELECT *
            if "select *" in sql_text.lower():
                raise Exception("SELECT * proibido.")

            # ==================================================================
            # 5) Executar SQL no Postgres
            # ==================================================================
            with engine_pdv.connect() as conn:
                try:
                    log_info("[SQL][EXEC] Executando SQL...")
                    result = conn.execute(text(sql_text)).fetchall()
                    log_success("[SQL][EXEC-OK] Resultado retornado.")
                except Exception as e:
                    log_error(f"Erro no SQL: {e}")
                    return {
                        "success": False,
                        "error": str(e)
                    }

            rows = [tuple(r) for r in result] if result else []

            return {
                "success": True,
                "intent": intent,
                "cliente_nome": nome_detectado,
                "sql_text": sql_text,
                "rows": rows
            }

        except Exception as e:
            log_error(f"Erro inesperado no agente SQL: {e}")
            print(RED + traceback.format_exc() + RESET)

            return {
                "success": False,
                "error": str(e)
            }

    return agente_sql
