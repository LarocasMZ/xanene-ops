from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
import enum
from ..core.database import Base


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskCategory(str, enum.Enum):
    # Operações de Campo (Coleta)
    COLETA_RESIDUOS = "coleta_residuos"
    ROTA_COLETA = "rota_coleta"
    VISITA_TECNICA = "visita_tecnica"
    VISTORIA_CONTENTORES = "vistoria_conteineres"
    LIMPEZA_PONTOS_COLETA = "limpeza_pontos_coleta"
    
    # Produção (BSF - Black Soldier Fly)
    ALIMENTACAO_LARVAS = "alimentacao_larvas"
    CONTROLE_TEMPERATURA = "controle_temperatura"
    COLHEITA_LARVAS = "colheita_larvas"
    PROCESSAMENTO_SUBSTRATO = "processamento_substrato"
    MONITORAMENTO_POSTURA = "monitoramento_postura"
    MANEJO_PUPAS = "manejo_pupas"
    
    # Logística e Entrega
    ENTREGA_PRODUTO = "entrega_produto"
    DISTRIBUICAO_ADUBO = "distribuicao_adubo"
    TRANSPORTE_RESIDUOS = "transporte_residuos"
    CONTROLE_FROTA = "controle_frota"
    MANUTENCAO_VEICULOS = "manutencao_veiculos"
    
    # Comercial e Vendas
    PROSPECCAO_CLIENTES = "prospeccao_clientes"
    REUNIAO_PARCEIROS = "reuniao_parceiros"
    FOLLOW_UP_PROPOSTAS = "follow_up_propostas"
    VISITA_COMERCIAL = "visita_comercial"
    APRESENTACAO_INSTITUCIONAL = "apresentacao_institucional"
    NEGOCIACAO_CONTRATOS = "negociacao_contratos"
    
    # Recursos Humanos
    TREINAMENTO_EQUIPE = "treinamento_equipe"
    INTEGRACAO_FUNCIONARIOS = "integracao_funcionarios"
    AVALIACAO_DESEMPENHO = "avaliacao_desempenho"
    REUNIAO_EQUIPE = "reuniao_equipe"
    PLANEJAMENTO_ESCALA = "planejamento_escala"
    
    # Manutenção e Infraestrutura
    MANUTENCAO_PREVENTIVA = "manutencao_preventiva"
    REPARO_INSTALACOES = "reparo_instalacoes"
    LIMPEZA_GERAL = "limpeza_geral"
    CONTROLE_ESTOQUE = "controle_estoque"
    COMPRA_SUPRIMENTOS = "compra_suprimentos"
    
    # Administrativo e Financeiro
    FECHAMENTO_MENSAL = "fechamento_mensal"
    EMISSAO_NOTAS = "emissao_notas"
    CONTAS_PAGAR_RECEBER = "contas_pagar_receber"
    RELATORIO_PRODUCAO = "relatorio_producao"
    CONTROLE_INDICADORES = "controle_indicadores"
    REUNIAO_DIRETORIA = "reuniao_diretoria"
    
    # Sustentabilidade e Qualidade
    AUDITORIA_PROCESSOS = "auditoria_processos"
    CONTROLE_QUALIDADE = "controle_qualidade"
    MONITORAMENTO_AMBIENTAL = "monitoramento_ambiental"
    CERTIFICACOES = "certificacoes"
    PESQUISA_DESENVOLVIMENTO = "pesquisa_desenvolvimento"
    
    # Marketing e Comunicação
    GESTAO_REDES_SOCIAIS = "gestao_redes_sociais"
    CRIACAO_CONTEUDO = "criacao_conteudo"
    EVENTOS_INSTITUCIONAIS = "eventos_institucionais"
    MATERIAL_PROMOCIONAL = "material_promocional"
    RELACIONAMENTO_IMPRENSA = "relacionamento_imprensa"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    category = Column(Enum(TaskCategory), nullable=False)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assignee = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")
    creator = relationship("User", foreign_keys=[created_by_id], back_populates="created_tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
