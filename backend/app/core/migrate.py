"""
Database Migration Script
Runs automatically on app startup to update database schema
"""

import os
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

def run_migrations() -> bool:
    """
    Run database migrations using psycopg2 directly.
    """
    try:
        import psycopg2
        print("=" * 50)
        print("🔧 RUNNING DATABASE MIGRATIONS...")
        print("=" * 50)
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        print(f"📡 DATABASE_URL found: {bool(database_url)}")
        
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            return False
        
        # Convert Railway DB URL format if needed
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgres://", 1)
        
        print(f"🔗 Connecting to database...")
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        print(f"✅ Database connected!")
        
        # Drop old constraint
        try:
            print(f"🔨 Dropping old constraint...")
            cur.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS valid_category")
            print("✅ Dropped old category constraint")
        except Exception as e:
            print(f"⚠️ Could not drop constraint: {e}")
        
        # Build and execute new constraint
        categories_str = ', '.join([f"'{c}'" for c in NEW_CATEGORIES])
        sql = f"ALTER TABLE tasks ADD CONSTRAINT valid_category CHECK (category IN ({categories_str}))"
        
        print(f"🔨 Adding new constraint with {len(NEW_CATEGORIES)} categories...")
        cur.execute(sql)
        print(f"✅ Database migrations completed! Added {len(NEW_CATEGORIES)} categories")
        print("=" * 50)
        
        cur.close()
        conn.close()
        return True
        
    except ImportError as e:
        print(f"❌ psycopg2 not installed: {e}")
        print("⚠️ Skipping migrations, app may fail on category validation")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {type(e).__name__}: {e}")
        print("⚠️ Continuing without migrations")
        return False
