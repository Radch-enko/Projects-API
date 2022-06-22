from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from src.db.database import Base


class ProjectTopic(Base):
    __tablename__ = 'project_topics'
    project_id = Column(ForeignKey('projects.id'), primary_key=True)
    topic_id = Column(ForeignKey('topics.id'), primary_key=True)

class ProjectUserVote(Base):
    __tablename__ = 'project_user_votes'
    project_id = Column(ForeignKey('projects.id'), primary_key=True)
    user_id = Column(ForeignKey('users.id'), primary_key=True)


class  Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique= True)
    name_ru = Column(String, unique= True)
    image = Column(String)
    description = Column(String)
    description_ru = Column(String)
    projects = relationship("Project", secondary = "project_topics", back_populates="topics")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    username = Column(String, unique = True)
    headline = Column(String, nullable=True)
    coverImage = Column(String, nullable=True)
    profileImage = Column(String, nullable=True)
    Hashed_password = Column(String)
    votedPosts = relationship("Project", secondary = "project_user_votes", back_populates="voters")
    comments = relationship("Comments", back_populates="user")
    discussionComments = relationship("DiscussionComments", back_populates="user")
    reports = relationship("CommentReport", backref = "users")
    discussionReports = relationship("DiscussionCommentReport", backref = "users")
    createdProjects = relationship("Project", backref="users")
    createdDiscussions = relationship("Discussion", backref="users")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    tagline = Column(String)
    description = Column(String)
    ownerLink = Column(String, nullable=True)
    thumbnail = Column(String)
    media = relationship("Media", backref="projects")
    createdDate = Column(DateTime)
    topics = relationship("Topic", secondary = "project_topics", back_populates="projects")
    voters = relationship("User", secondary = "project_user_votes", back_populates="votedPosts")
    maker = relationship("User", back_populates="createdProjects")
    maker_id = Column(Integer, ForeignKey("users.id"))
    comments = relationship("Comments", back_populates="project")


class Media(Base):
    __tablename__ = "Medias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String)
    parent_id = Column(Integer, ForeignKey('projects.id'))

class Comments(Base):
    __tablename__ = "Comments"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="comments")
    project = relationship("Project", back_populates="comments")


# Discussion section

class Discussion(Base):
    __tablename__ = "discussions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    createdDate = Column(DateTime)
    topics = relationship("DiscussionTopic", secondary = "discussions_topics", back_populates="discussions")
    maker = relationship("User", back_populates="createdDiscussions")
    maker_id = Column(Integer, ForeignKey("users.id"))
    comments = relationship("DiscussionComments", back_populates="discussion")


class DiscussionTopic(Base):
    __tablename__ = "discussionTopic"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique= True)
    name_ru = Column(String, unique= True)
    image = Column(String)
    description = Column(String)
    description_ru = Column(String)
    discussions = relationship("Discussion", secondary = "discussions_topics", back_populates="topics")


class DiscussionsTopics(Base):
    __tablename__ = 'discussions_topics'
    discussion_id = Column(ForeignKey('discussions.id'), primary_key=True)
    topic_id = Column(ForeignKey('discussionTopic.id'), primary_key=True)

class DiscussionComments(Base):
    __tablename__ = "DiscussionComments"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    discussion_id = Column(Integer, ForeignKey("discussions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="discussionComments")
    discussion = relationship("Discussion", back_populates="comments")

class CommentReport(Base):
    __tablename__ = "CommentReport"
    comment_id = Column(ForeignKey("Comments.id"), primary_key=True)
    user_id = Column(ForeignKey('users.id'), primary_key=True)

class DiscussionCommentReport(Base):
    __tablename__ = "DiscussionCommentReport"
    comment_id = Column(ForeignKey("DiscussionComments.id"), primary_key=True)
    user_id = Column(ForeignKey('users.id'), primary_key=True)

