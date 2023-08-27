from starchaos import db


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"Like(user_id={self.user_id}, post_id={self.post_id})"


