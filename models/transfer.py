from datetime import datetime

from extensions import db


class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    from_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=False)
    to_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    is_confirmed = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='confirmado')
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    from_account = db.relationship(
        'BankAccount',
        foreign_keys=[from_account_id],
        backref='outgoing_transfers',
        lazy=True
    )
    to_account = db.relationship(
        'BankAccount',
        foreign_keys=[to_account_id],
        backref='incoming_transfers',
        lazy=True
    )

    def __repr__(self):
        return f'<Transfer {self.from_account_id} -> {self.to_account_id} ({self.amount})>'
