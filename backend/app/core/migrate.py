"""
Database Migration Script
Runs automatically on app startup to update database schema
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# New task categories list
NEW_CATEGORIES = [
    # Field Operations (Coleta)
    'coleta_residuos', 'rota_coleta', 'visita_tecnica', 'vistoria_conteineres', 'limpeza_pontos_coleta',
    # Production (BSF)
    'alimentacao_larvas', 'controle_temperatura', 'colheita_larvas', 'processamento_substrato', 'monitoramento_postura', 'manejo_pupas',
    # Logistics
    'entrega_produto', 'distribuicao_adubo', 'transporte_residuos', 'controle_frota', 'manutencao_veiculos',
    # Sales
    'prospeccao_clientes', 'reuniao_parceiros', 'follow_up_propostas', 'visita_comercial', 'apresentacao_institucional', 'negociacao_contratos',
    # HR
    'treinamento_equipe', 'integracao_funcionarios', 'avaliacao_desempenho', 'reuniao_equipe', 'planejamento_escala',
    # Maintenance
    'manutencao_preventiva', 'reparo_instalacoes', 'limpeza_geral', 'controle_estoque', 'compra_suprimentos',
    # Admin
    'fechamento_mensal', 'emissao_notas', 'contas_pagar_receber', 'relatorio_producao', 'controle_indicadores', 'reuniao_diretoria',
    # Quality
    'auditoria_processos', 'controle_qualidade', 'monitoramento_ambiental', 'certificacoes', 'pesquisa_desenvolvimento',
    # Marketing
    'gestao_redes_sociais', 'criacao_conteudo', 'eventos_institucionais', 'material_promocional', 'relacionamento_imprensa'
]

def run_migrations(db: Session) -> bool:
    """
    Run database migrations.
    Returns True if migrations were successful, False otherwise.
    """
    try:
        logger.info("🔄 Running database migrations...")
        
        # Drop old category constraint if exists
        try:
            db.execute(text("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS valid_category"))
            db.commit()
            logger.info("✅ Dropped old category constraint")
        except Exception as e:
            logger.warning(f"Could not drop constraint: {e}")
            db.rollback()
        
        # Build category list SQL
        categories_sql = ', '.join([f"'{cat}'" for cat in NEW_CATEGORIES])
        
        # Add new constraint
        add_constraint_sql = f"""
            ALTER TABLE tasks ADD CONSTRAINT valid_category 
            CHECK (category IN ({categories_sql}))
        """
        
        db.execute(text(add_constraint_sql))
        db.commit()
        
        logger.info(f"✅ Database migrations completed successfully!")
        logger.info(f"✅ Added {len(NEW_CATEGORIES)} task categories")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.rollback()
        # Don't fail the app if migration fails
        logger.warning("Continuing without migrations...")
        return False
