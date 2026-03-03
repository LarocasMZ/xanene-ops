"""
Database Migration Script
Runs automatically on app startup to update database schema
"""

from sqlalchemy import text, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import Pool
import logging

logger = logging.getLogger(__name__)

# New task categories list
NEW_CATEGORIES = [
    'coleta_residuos', 'rota_coleta', 'visita_tecnica', 'vistoria_conteineres', 'limpeza_pontos_coleta',
    'alimentacao_larvas', 'controle_temperatura', 'colheita_larvas', 'processamento_substrato', 'monitoramento_postura', 'manejo_pupas',
    'entrega_produto', 'distribuicao_adubo', 'transporte_residuos', 'controle_frota', 'manutencao_veiculos',
    'prospeccao_clientes', 'reuniao_parceiros', 'follow_up_propostas', 'visita_comercial', 'apresentacao_institucional', 'negociacao_contratos',
    'treinamento_equipe', 'integracao_funcionarios', 'avaliacao_desempenho', 'reuniao_equipe', 'planejamento_escala',
    'manutencao_preventiva', 'reparo_instalacoes', 'limpeza_geral', 'controle_estoque', 'compra_suprimentos',
    'fechamento_mensal', 'emissao_notas', 'contas_pagar_receber', 'relatorio_producao', 'controle_indicadores', 'reuniao_diretoria',
    'auditoria_processos', 'controle_qualidade', 'monitoramento_ambiental', 'certificacoes', 'pesquisa_desenvolvimento',
    'gestao_redes_sociais', 'criacao_conteudo', 'eventos_institucionais', 'material_promocional', 'relacionamento_imprensa'
]

def run_migrations(db: Session) -> bool:
    """
    Run database migrations using raw connection.
    """
    try:
        print("🔄 Running database migrations...")
        
        # Get raw connection
        conn = db.connection()
        raw_conn = conn.connection.connection
        
        # Drop old constraint
        try:
            raw_conn.cursor().execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS valid_category")
            raw_conn.commit()
            print("✅ Dropped old category constraint")
        except Exception as e:
            print(f"⚠️ Could not drop constraint: {e}")
        
        # Build and execute new constraint
        categories_str = ', '.join([f"'{c}'" for c in NEW_CATEGORIES])
        sql = f"ALTER TABLE tasks ADD CONSTRAINT valid_category CHECK (category IN ({categories_str}))"
        
        raw_conn.cursor().execute(sql)
        raw_conn.commit()
        
        print(f"✅ Database migrations completed! Added {len(NEW_CATEGORIES)} categories")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        try:
            db.rollback()
        except:
            pass
        return False
