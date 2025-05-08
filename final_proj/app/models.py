from . import db
from flask_login import UserMixin
from datetime import datetime

# ----------------------------
# User Model
# ----------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'student', 'teacher', 'admin'

    # Relationships
    posts = db.relationship('Post', back_populates='author', lazy= 'dynamic', cascade='all, delete-orphan')
    replies = db.relationship('Reply', back_populates='author', lazy= 'dynamic', cascade='all, delete-orphan')
    votes = db.relationship('Vote', back_populates='author', lazy= 'dynamic', cascade='all, delete-orphan')

    def __str__(self):
        return f'<User {self.username}>'
    
# ----------------------------
# Topic
# ----------------------------
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(250), nullable=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)           ###
    posts = db.relationship('Post', back_populates='topic', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'
    
# ----------------------------
# Post (thread/question)
# ----------------------------
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utc.now)  ### 
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topicID = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    media_url = db.Column(db.String(250), nullable=True)

    author = db.relationship('User', back_populates='posts')
    topic = db.relationship('Topic', back_populates='posts')
    replies = db.relationship('Reply', back_populates = 'post', lazy='dynamic', cascade='all, delete-orphan')
    votes = db.relationship('Vote', back_populates = 'post', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def upvotes(self):
        return Vote.query.filter_by(post_id=self.id, vote_type = 'upvote').count()
    @property
    def downvotes(self):
        return Vote.query.filter_by(post_id=self.id, vote_type = 'downvote').count()
    @property
    def score(self):
        return self.upvotes - self.downvotes

    def __repr__(self):
        return f'<Post {self.title}>'


# ----------------------------
# Reply (answer/comment)
# ----------------------------
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utc.now)  ###
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topicID = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    media_url = db.Column(db.String(250), nullable=True)

    author = db.relationship('User', back_populates='replies')
    post = db.relationship('Post', back_populates='replies')
    votes = db.relationship('Vote', back_populates='reply', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def upvotes(self):
        return Vote.query.filter_by(post_id=self.id, vote_type='upvote').count()

    @property
    def downvotes(self):
        return Vote.query.filter_by(post_id=self.id, vote_type='downvote').count()

    @property
    def score(self):
        return self.upvotes - self.downvotes

    def __repr__(self):
        return f'<Reply {self.id} to Post {self.topicID}>'

# ----------------------------
# Vote (up/down-votes)
# ----------------------------
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utc.now)  ###
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topicID = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    replyID = db.Column(db.Integer, db.ForeignKey('reply.id'), nullable=True)
    vote_type = db.Column(db.String(10), nullable=False)

    user = db.relationship('User', back_populates='votes')
    post = db.relationship('Post', back_populates='votes')
    reply = db.relationship('Reply', back_populates='votes')

    #ensures each user can only have 1 concurrent vote on both a post or reply
    __table_args__ = (
        db.UniqueConstraint('userID', 'topicID', 'vote_type', name='unique_userID_topicID_vote_type'),
        db.UniqueConstraint('userID', 'replyID', 'vote_type', name='unique_userID_replyID_vote_type'),
    )

    def __repr__(self):
        item_id = self.topicID if self.topicID else self.replyID
        item_type = "Post" if self.post else "Reply"

        return f'<Vote {self.vote_type} by User {self.userID} for {item_type} {item_id}>'