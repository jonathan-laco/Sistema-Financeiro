from datetime import datetime

from extensions import db


class TelegramToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    request_status = db.Column(db.String(20), default='none', nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=True)
    expires_days = db.Column(db.Integer, default=30, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    requested_at = db.Column(db.DateTime, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    telegram_chat_id = db.Column(db.String(64), nullable=True, unique=True)
    telegram_username = db.Column(db.String(120), nullable=True)
    admin_note = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('telegram_token', uselist=False))

    @property
    def is_valid(self):
        if self.request_status != 'approved' or not self.token or not self.expires_at:
            return False
        return self.expires_at > datetime.utcnow()

    @property
    def is_connected(self):
        return bool(self.telegram_chat_id)

    def __repr__(self):
        return f'<TelegramToken user_id={self.user_id} status={self.request_status}>'
