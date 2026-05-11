from extensions import db
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'receita' ou 'despesa'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    is_confirmed = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='confirmado')  # 'confirmado', 'pendente', 'cancelado'
    is_mei_transaction = db.Column(db.Boolean, default=False)  # Flag para transação MEI
    has_invoice = db.Column(db.Boolean, default=False)  # Flag para indicar se tem nota fiscal
    installment_group_id = db.Column(db.String(36), nullable=True)  # Agrupa parcelas da mesma compra/conta
    installment_number = db.Column(db.Integer, nullable=True)  # Número da parcela atual
    installment_total = db.Column(db.Integer, nullable=True)  # Total de parcelas
    is_salary_deductible = db.Column(db.Boolean, default=False)  # Indica se deve ser planejada para desconto no salário
    salary_deduction_day = db.Column(db.Integer, nullable=True)  # Dia do mês usado como vencimento/desconto
    is_deleted = db.Column(db.Boolean, default=False)  # Soft-delete flag
    deleted_at = db.Column(db.DateTime, nullable=True)  # Timestamp de exclusão
    
    def __repr__(self):
        return f'<Transaction {self.description} ({self.amount})>'
