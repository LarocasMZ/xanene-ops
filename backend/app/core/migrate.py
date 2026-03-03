"""
Database Migration Script
Runs automatically on app startup to update database schema
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

MIGRATION_SQL = """
-- Remove old category constraint
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS valid_category;

-- Add new constraint with all 47 categories
ALTER TABLE tasks ADD CONSTRAINT valid_category CHECK (category IN (
    -- Field Operations (Coleta)
    'coleta_residuos', 'rota_coleta', 'visita_tecnica', 'vistoria_conteineres', 'limpeza_pontos_coleta',
    -- Production (BSF)
    'alimentacao_larvas', 'controle_temperatura', 'colheita_larvas', 'processamento_substrato', 'monitoramento_postura', 'manejo_pupas',
    -- Logistics
    'entrega_produto', 'distribuicao_adubo', 'transporte_residuos', 'controle_frota', 'manutencao_veiculos',
    -- Sales
    'prospeccao_clientes', 'reuniao_parceiros', 'follow_up_propostas', 'visita_comercial', 'apresentacao_institucional', 'negociacao_contratos',
    -- HR
    'treinamento_equipe', 'integracao_funcionarios', 'avaliacao_desempenho', 'reuniao_equipe', 'planejamento_escala',
    -- Maintenance
    'manutencao_preventiva', 'reparo_instalacoes', 'limpeza_geral', 'controle_estoque', 'compra_suprimentos',
    -- Admin
    'fechamento_mensal', 'emissao_notas', 'contas_pagar_receber', 'relatorio_producao', 'controle_indicadores', 'reuniao_diretoria',
    -- Quality
    'auditoria_processos', 'controle_qualidade', 'monitoramento_ambiental', 'certificacoes', 'pesquisa_desenvolvimento',
    -- Marketing
    'gestao_redes_sociais', 'criacao_conteudo', 'eventos_institucionais', 'material_promocional', 'relacionamento_imprensa'
));
"""


def run_migrations(db: Session) -> bool:
    """
    Run database migrations.
    Returns True if migrations were successful, False otherwise.
    """
    try:
        logger.info("Running database migrations...")
        
        # Execute migration SQL
        db.execute(text(MIGRATION_SQL))
        db.commit()
        
        logger.info("✅ Database migrations completed successfully!")
        logger.info("✅ Task categories updated to new comprehensive list")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.rollback()
        return False
