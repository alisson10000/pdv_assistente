from sqlalchemy import text
from app.core.database_ia import engine_ia

print("\n🔍 Testando conexão com o banco IA...\n")

with engine_ia.connect() as conn:
    try:
        port = conn.execute(text("SELECT inet_server_port();")).scalar()
        dbname = conn.execute(text("SELECT current_database();")).scalar()
        version = conn.execute(text("SELECT version();")).scalar()

        print("====================================")
        print("🟢 CONECTADO!")
        print(f"📌 PORTA: {port}")
        print(f"📌 BANCO: {dbname}")
        print(f"📌 VERSION: {version}")
        print("====================================")

    except Exception as e:
        print("\n❌ ERRO AO EXECUTAR QUERY:")
        print(e)
        print("====================================")
