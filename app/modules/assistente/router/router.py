from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database_ia import get_db_ia
from app.core.database_pdv import get_db_pdv  # 🔵 precisa existir
from app.modules.assistente.schemas.schema import ChatRequest, ChatResponse
from app.modules.assistente.services.service import processar_mensagem

# 🔵 pipeline de sincronização PDV → IA
from app.modules.assistente.pipeline.sync_pdv_ia import sincronizar_pdv_ia  

router = APIRouter(
    prefix="/assistente",
    tags=["Assistente"],
)


# =====================================================
#  ROTA PRINCIPAL DO ASSISTENTE
# =====================================================
@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Envia uma mensagem ao assistente inteligente"
)
def chat(req: ChatRequest, db_ia: Session = Depends(get_db_ia)):
    """
    Fluxo completo:
    1. Registrar mensagem → chat_messages
    2. RAG
    3. SQL Agent (consultas ao PDV)
    4. LLM gera resposta final
    5. Registro de interações
    6. Preferências do cliente e recomendações
    """

    print("\n==========================================================")
    print("🟦 [ROUTER] Requisição recebida na rota /assistente/chat")
    print(f"🟦 [ROUTER] Vendedor ID: {req.vendedor_id}")
    print(f"🟦 [ROUTER] Mensagem: {req.mensagem}")
    print("==========================================================")

    try:
        resposta = processar_mensagem(
            vendedor_id=req.vendedor_id,
            mensagem=req.mensagem,
            db_ia=db_ia
        )

        print("🟢 [ROUTER] Resposta gerada com sucesso.")
        print(f"🟢 [ROUTER] Resposta: {resposta}")
        print("==========================================================\n")

        return ChatResponse(resposta=resposta)

    except HTTPException:
        raise

    except Exception as e:
        print("❌ [ROUTER] Erro ao processar mensagem:", e)
        print("==========================================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar a mensagem: {str(e)}"
        )


# =====================================================
#  🔥 NOVA ROTA — SINCRONIZAÇÃO PDV → IA
# =====================================================
@router.post(
    "/sincronizar",
    summary="Sincroniza o banco PDV com o banco IA",
)
def sincronizar(
    db_ia: Session = Depends(get_db_ia),
    db_pdv: Session = Depends(get_db_pdv)
):
    """
    Executa a sincronização completa:
        - Clientes → clientes_ia
        - Produtos → produtos_ia
        - Geração de Embeddings
        - Atualização de timestamps
    """

    print("\n==========================================================")
    print("🟦 [ROUTER] Iniciando sincronização PDV → IA")
    print("==========================================================")

    try:
        resultado = sincronizar_pdv_ia(db_pdv, db_ia)

        print("🟢 [ROUTER] Sincronização concluída com sucesso.")
        print(f"🟢 [ROUTER] {resultado}")
        print("==========================================================\n")

        return {"status": "ok", "detalhe": resultado}

    except Exception as e:
        print("❌ [ROUTER] Erro durante sincronização:", e)
        print("==========================================================\n")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao sincronizar dados: {str(e)}"
        )
