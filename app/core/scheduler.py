"""
Background scheduler para tarefas periódicas
"""
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.supabase_client import get_supabase_client
from app.services.pedido_service import expirar_pedidos_antigos


def expirar_pedidos_job():
    """Job que roda a cada 10 segundos para expirar pedidos antigos"""
    try:
        supabase_client = get_supabase_client()
        count = expirar_pedidos_antigos(supabase_client)
        if count > 0:
            print(f"✅ {count} pedido(s) expirado(s)")
    except Exception as e:
        print(f"❌ Erro no job de expiração: {e}")


def start_scheduler():
    """Inicia o scheduler"""
    scheduler = BackgroundScheduler()

    # Job de expiração a cada 10 segundos
    scheduler.add_job(
        expirar_pedidos_job,
        'interval',
        seconds=10,
        id='expirar_pedidos',
        replace_existing=True
    )

    scheduler.start()
    print("🕐 Scheduler iniciado - Job de expiração ativo")

    return scheduler
