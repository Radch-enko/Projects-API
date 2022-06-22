from pydantic import BaseModel, BaseConfig, validator, constr, Field
from typing import List, Optional
from datetime import datetime


BaseConfig.arbitrary_types_allowed = True

class Topic(BaseModel):
    id: int
    name: str
    name_ru: str
    image: str
    description: str
    description_ru: str

    class Config:
        orm_mode = True


class Project(BaseModel):
    id: int
    name: str
    tagline: Optional[str] = None
    thumbnail: Optional[str] = None
    isVoted: Optional[bool] = False
    votesCount: int = 0
    topics: List[Topic]

    class Config:
        orm_mode = True

class Media(BaseModel):
    url: str

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    name: str
    username: str
    headline: Optional[str] = None
    coverImage: Optional[str] = None
    profileImage: Optional[str] = None

    class Config:
        orm_mode = True



class CommentsBase(BaseModel):
    id: int
    text: str

class Comments(CommentsBase):
    user: Optional[User]
    createdDate: datetime = datetime.now().astimezone()
    isReported: Optional[bool] = False

    class Config:
        orm_mode = True

class CreateComment(BaseModel):
    project_id: int
    text: str

class CreateDiscussionComment(BaseModel):
    discussion_id: int
    text: str

class ProjectSchema(Project):
    description: Optional[str] = None
    maker: User
    media: Optional[List[Media]] = None
    comments: Optional[List[Comments]] = None
    ownerLink: Optional[str] = None
    createdDate: datetime = datetime.now().astimezone()

    class Config:
        orm_mode = True
        
        
class UserSchema(User):
    createdProjects : Optional[List[Project]] = None
    class Config:
        orm_mode = True


class TopicCreate(BaseModel):
    topicId: int

class ProjectCreate(BaseModel):
    name: str
    tagline: str
    description: str
    ownerLink: str
    thumbnail: Optional[str] = None
    media: Optional[List[str]] = None
    topics: List[TopicCreate]

    class Config:
        orm_mode = True


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    ownerLink: Optional[str] = None
    thumbnail: Optional[str] = None
    media: Optional[List[str]] = None
    topics: Optional[List[TopicCreate]] = None

    class Config:
        orm_mode = True
    

class UserCreate(BaseModel):
    name: str
    username: str
    headline:  Optional[str] = None
    password: constr(min_length=5)
    password2: str

    @validator("password2")
    def password_mathc(cls, v, values, **kwargs):
        if 'password' in values and v != values["password"]:
            raise ValueError("passwords dont match")
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    headline:  Optional[str] = None
    profileImage: Optional[str] = None
    coverImage: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class Login(BaseModel):
    username: str
    password: str


# Discussion flow

class DiscussionTopic(BaseModel):
    id: int
    name: str
    name_ru: str
    image: str
    description: str
    description_ru: str

    class Config:
        orm_mode = True

class Discussion(BaseModel):
    id: int
    title: str
    topics: List[DiscussionTopic]
    maker: User
    createdDate: datetime = datetime.now().astimezone()
    replies : Optional[int] = 0

    class Config:
        orm_mode = True


class DiscussionTopicCreate(BaseModel):
    topicId: int

class CreateDiscussion(BaseModel):
    title: str
    description: str
    topics: List[DiscussionTopicCreate]

    class Config:
        orm_mode = True

class DetailDiscussion(Discussion):
    description: str
    comments: Optional[List[Comments]] = None

    class Config:
        orm_mode = True

class CommentReport(BaseModel):
    commentId: int
    user: User
    
    class Config:
        orm_mode = True

class DiscussionCommentReport(BaseModel):
    commentId: int
    user: User
    isReported: Optional[bool] = False

    
    class Config:
        orm_mode = True