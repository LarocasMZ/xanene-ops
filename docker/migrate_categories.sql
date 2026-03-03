-- Migration: Update task categories to new comprehensive list
-- Run this on existing database to update the CHECK constraint

-- Drop old constraint
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS valid_category;

-- Add new constraint with all categories
ALTER TABLE tasks ADD CONSTRAINT valid_category CHECK (category IN (
    -- Operações de Campo (Coleta)
    'coleta_residuos', 'rota_coleta', 'visita_tecnica', 'vistoria_conteineres', 'limpeza_pontos_coleta',
    -- Produção (BSF)
    'alimentacao_larvas', 'controle_temperatura', 'colheita_larvas', 'processamento_substrato', 'monitoramento_postura', 'manejo_pupas',
    -- Logística e Entrega
    'entrega_produto', 'distribuicao_adubo', 'transporte_residuos', 'controle_frota', 'manutencao_veiculos',
    -- Comercial e Vendas
    'prospeccao_clientes', 'reuniao_parceiros', 'follow_up_propostas', 'visita_comercial', 'apresentacao_institucional', 'negociacao_contratos',
    -- Recursos Humanos
    'treinamento_equipe', 'integracao_funcionarios', 'avaliacao_desempenho', 'reuniao_equipe', 'planejamento_escala',
    -- Manutenção e Infraestrutura
    'manutencao_preventiva', 'reparo_instalacoes', 'limpeza_geral', 'controle_estoque', 'compra_suprimentos',
    -- Administrativo e Financeiro
    'fechamento_mensal', 'emissao_notas', 'contas_pagar_receber', 'relatorio_producao', 'controle_indicadores', 'reuniao_diretoria',
    -- Sustentabilidade e Qualidade
    'auditoria_processos', 'controle_qualidade', 'monitoramento_ambiental', 'certificacoes', 'pesquisa_desenvolvimento',
    -- Marketing e Comunicação
    'gestao_redes_sociais', 'criacao_conteudo', 'eventos_institucionais', 'material_promocional', 'relacionamento_imprensa'
));
