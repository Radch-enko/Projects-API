from typing import List, Optional
from sqlalchemy.orm import Session
from src.db import models
from src.db.get_db import get_db
from src.models.schemas import Comments, CreateDiscussion, DetailDiscussion, Discussion, DiscussionTopicCreate, Project, ProjectCreate, ProjectSchema, ProjectUpdate, TopicCreate, UserCreate, User, UserUpdate
from fastapi import UploadFile, Depends, HTTPException, status
import cloudinary
import cloudinary.uploader
import cloudinary.api
from src.core.security import hash_password, decode_access_token, JWTBearer, OptionalJWTBearer
from datetime import datetime
from src.image_uploading_config import *
import secrets
from sqlalchemy import cast, Date, desc
import validators

def get_db_projects(db: Session, cursor: int = 0, page_size: int = 10, day: datetime.date = None, makerId: Optional[int] = None, topicId: Optional[int] = None, searchQuery: Optional[str] = None) -> List[Project]:

    list: List[Project] = db.query(models.Project)

    filters = []
    if day != None:
        filters.append(cast(models.Project.createdDate, Date) == day)
    
    if makerId != None:
        filters.append(models.Project.maker_id == makerId)

    if topicId != None:
        filters.append(models.Project.topics.any(id = topicId))

    
    if searchQuery != None:
        print("searchQuery = " + searchQuery)
        filters.append((models.Project.name.contains(searchQuery)) |
         (models.Project.tagline.contains(searchQuery)))
    
    list = list.filter(*filters).offset(cursor).limit(page_size).all()

    for item in list:
        votesCount = db.query(models.ProjectUserVote).filter(models.ProjectUserVote.project_id == item.id).count()

        if votesCount != None:
            item.votesCount = votesCount

    if list != None:
        newlist = sorted(list, key=lambda x: x.votesCount, reverse=True)
        return newlist
    else:
        return []

def get_extra_projects(db: Session, voter: User, cursor: int = 0, page_size: int = 10, day: Optional[Date] = None, makerId: Optional[int] = None, topicId: Optional[int] = None, searchQuery: Optional[str] = None):
    list = get_db_projects(db, cursor, page_size, day, makerId, topicId, searchQuery)
    
    if list != None:
        if voter != None:
            for item in list:
                
                record = db.query(models.ProjectUserVote).filter((models.ProjectUserVote.project_id == item.id) & (models.ProjectUserVote.user_id == voter.id)).count()

                if record == 0:
                    item.isVoted = False
                else:
                    item.isVoted = True

    return list

def castToDb(db: Session, list: List[TopicCreate]):
    topics = []
    for item in list:
        topics.append(db.query(models.Topic).get(item.topicId))
    return topics

def addMedia(db: Session, file: str):
    if file != None:
        if validators.url(file) :
            db_media_item = models.Media(
                url = file
            )
            db.add(db_media_item)
            db.commit()
            db.refresh(db_media_item)
            
            return db_media_item
        else:
            filename = secrets.token_hex(nbytes=4)
            cloudinary.uploader.upload(file, public_id = filename)
            db_media_item = models.Media(
                url = "https://res.cloudinary.com/dsxnslqc8/image/upload/" + filename + ".jpeg"
            )
            db.add(db_media_item)
            db.commit()
            db.refresh(db_media_item)

            return db_media_item
    else : pass

def addProjectMedia(db: Session, links: List[str]):
    list = []
    if links != None:
        for link in links:
            list.append(addMedia(db, link))
    return list

def create_db_project(db: Session, projectCreate: ProjectCreate, maker: User):
    new_project = models.Project(
        name = projectCreate.name,
        tagline= projectCreate.tagline,
        description = projectCreate.description,
        ownerLink = projectCreate.ownerLink,
        media = addProjectMedia(db, projectCreate.media),
        createdDate = datetime.now().astimezone(),
        topics = castToDb(db, projectCreate.topics),
        maker_id = maker.id
    )
    avatar = addMedia(db, projectCreate.thumbnail)
    if avatar != None:
        new_project.thumbnail = avatar.url
        
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


async def update_db_project(db: Session, project_id: int, projectUpdate: ProjectUpdate, user: User)-> ProjectSchema:
    old: ProjectSchema = get_db_project(db, project_id)

    if user.id == old.maker.id:
        if projectUpdate.name != None:
            old.name =projectUpdate.name
        if projectUpdate.tagline != None:
            old.tagline = projectUpdate.tagline
        if projectUpdate.description != None:
            old.description = projectUpdate.description
        if projectUpdate.ownerLink != None:
            old.ownerLink = projectUpdate.ownerLink
        if projectUpdate.thumbnail != None:
            old.thumbnail = addMedia(db,projectUpdate.thumbnail).url
        if projectUpdate.media != None:
            old.media = addProjectMedia(db, projectUpdate.media)
        if projectUpdate.topics != None:
            old.topics = castToDb(db, projectUpdate.topics)

        db.commit()
    else:
        raise HTTPException(status_code=401)
    db.refresh(old)
    return old

def get_db_project(db: Session, project_id: int) -> ProjectSchema:
    return db.query(models.Project).get(project_id)

def get_extra_project(db: Session, project_id: int, voter: User) -> ProjectSchema:
    project = get_db_project(db, project_id)
    votesCount = db.query(models.ProjectUserVote).filter(models.ProjectUserVote.project_id == project.id).count()

    if votesCount != None:
        project.votesCount = votesCount

    if voter is None:
        return project
    else:
        record = db.query(models.ProjectUserVote).filter((models.ProjectUserVote.project_id == project.id) & (models.ProjectUserVote.user_id == voter.id)).count()

        if record == 0: 
            project.isVoted = False
        else:
            project.isVoted = True

        for comment in project.comments:
            isReported = db.query(models.CommentReport).filter((models.CommentReport.user_id == voter.id) & (models.CommentReport.comment_id == comment.id)).count() == 1
            comment.isReported = isReported

        return project

def get_db_topics(db: Session):
    return db.query(models.Topic).all()

def get_db_all_users(cursor: int, page_size: int, db: Session, searchQuery: Optional[str] = None):
    filters = []
    if searchQuery != None:
        filters.append(models.User.username.contains(searchQuery))

    return db.query(models.User).filter(*filters).offset(cursor).limit(page_size).all()

def create_db_user(userCreate: UserCreate, db: Session):
    if(db.query(models.User).filter(models.User.username == userCreate.username).first() != None):
        raise HTTPException(status_code=422, detail = "User already exists")
    new_user = models.User(
        name = userCreate.name,
        username = userCreate.username,
        headline = userCreate.headline,
        Hashed_password=hash_password(userCreate.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_db_user(userUpdate: UserUpdate, user: User, db: Session):
    if userUpdate.name != None:
        user.name = userUpdate.name

    if userUpdate.headline != None:
        user.headline = userUpdate.headline

    if userUpdate.profileImage != None:
        user.profileImage = addMedia(db, userUpdate.profileImage).url,
    
    if userUpdate.coverImage != None:
        user.coverImage = addMedia(db, userUpdate.coverImage).url

    db.commit()
    db.refresh(user)

    return user

def update_profile_image_db(db: Session, file: UploadFile, user: User):
    user.profileImage = addMedia(db, file).url
    db.commit()
    db.refresh(user)

    return user

def update_cover_image_db( db: Session,file: UploadFile, user: User,):
    user.coverImage = addMedia(db, file).url
    db.commit()
    db.refresh(user)

    return user

async def get_current_user(
    token: str = Depends(JWTBearer()),
    db: Session = Depends(get_db)
) -> User:
    cred_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Credentials are not valid")
    payload = decode_access_token(token)
    if payload is None:
        raise cred_exception
    username: str = payload.get("sub")
    if username is None:
        raise cred_exception
    user = get_user_by_username(username, db)
    if user is None:
        return cred_exception
    return user


async def get_current_user_nullable(
    token: str = Depends(OptionalJWTBearer()),
    db: Session = Depends(get_db)
) -> User:
    if token is None:
        return None
    payload = decode_access_token(token)
    if payload is None:
        return None
    username: str = payload.get("sub")
    if username is None:
        return None
    user = get_user_by_username(username, db)
    return user

def get_user_by_username(username: str, db: Session) -> models.User:
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, id: int) -> models.User:
    return db.query(models.User).get(id)

async def vote_for_post(db: Session, project_id: int, voter: User):
    record = db.query(models.ProjectUserVote).filter((models.ProjectUserVote.project_id == project_id) & (models.ProjectUserVote.user_id == voter.id)).first()


    if record == None:
        votation = models.ProjectUserVote(project_id = project_id, user_id = voter.id)
        db.add(votation)
    else:
        db.delete(record)
    
    db.commit()
    

    return {"success": "true"}


async def comment_for_post(db: Session, project_id: int, text: str, commenter: User):
    comment = models.Comments(
        text= text,
        user_id=commenter.id,
        project_id=project_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return get_extra_project(db, project_id, commenter)

def delete_db_project(db: Session, project_id: int, deleter: User):
    project: ProjectSchema = get_db_project(db, project_id)
    if project.maker.id == deleter.id:
        db.delete(project)
        db.commit()
    else:
        raise HTTPException(status_code=403)
    
    return {"success": "true"}

def get_db_discussions(cursor: int, page_size: int, searchQuery: Optional[str] = None, db: Session = Depends(get_db)):
    list: List[Discussion] = db.query(models.Discussion)

    filters = []

    if searchQuery != None:
        print("searchQuery = " + searchQuery)
        filters.append(models.Discussion.title.contains(searchQuery))

    result: List[Discussion] = list.filter(*filters).order_by(desc(models.Discussion.createdDate)).offset(cursor).limit(page_size).all()

    for item in result:
        replies = db.query(models.DiscussionComments).filter(models.DiscussionComments.discussion_id == item.id).count()

        if replies != None:
            item.replies = replies

    return result

def get_db_discussions_topics(db: Session = Depends(get_db)):
    return db.query(models.DiscussionTopic).all()

def castToDiscussionTopicsDb(db: Session, list: List[DiscussionTopicCreate]):
    topics = []
    for item in list:
        topics.append(db.query(models.DiscussionTopic).get(item.topicId))
    return topics

def create_db_discussion(createDiscussion: CreateDiscussion, maker: User, db: Session):
    discussion = models.Discussion(
        title = createDiscussion.title,
        description = createDiscussion.description,
        createdDate = datetime.now().astimezone(),
        topics = castToDiscussionTopicsDb(db, createDiscussion.topics),
        maker_id = maker.id
    )
    db.add(discussion)
    db.commit()
    db.refresh(discussion)
    return discussion

def get_db_discussion_by_id(discussionId: int, user: User, db: Session):

    discussion: DetailDiscussion = db.query(models.Discussion).get(discussionId)

    replies = db.query(models.DiscussionComments).filter(models.DiscussionComments.discussion_id == discussionId).count()

    if replies != None:
        discussion.replies = replies

    if user != None:
        for comment in discussion.comments:
            isReported = db.query(models.DiscussionCommentReport).filter((models.DiscussionCommentReport.user_id == user.id) & (models.DiscussionCommentReport.comment_id == comment.id)).count() == 1
            comment.isReported = isReported

    return discussion

async def comment_for_discussion(db: Session, discussion_id: int, text: str, commenter: User):
    comment = models.DiscussionComments(
        text= text,
        user_id=commenter.id,
        discussion_id=discussion_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return get_db_discussion_by_id(discussion_id, commenter, db)

def report_db_comment(commentId: int, isDiscussionComment: bool, user: User, db: Session):
    
    if isDiscussionComment:
        report = models.DiscussionCommentReport(
            user_id = user.id,
            comment_id = commentId
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        reportsCount = db.query(models.DiscussionCommentReport).filter(models.DiscussionCommentReport.comment_id == commentId).count()
        print("DiscussionCommentReportCount = " + str(reportsCount))
        if reportsCount >= 5:

            reports = db.query(models.DiscussionCommentReport).filter(models.DiscussionCommentReport.comment_id == commentId).all()

            for item in reports:
                db.delete(item)
                db.commit()

            reportedComment: models.DiscussionComments = db.query(models.DiscussionComments).get(commentId)
            print("DiscussionCommentsReported = " + reportedComment.text)
            db.delete(reportedComment)
            db.commit()
    else:
        report = models.CommentReport(
            user_id = user.id,
            comment_id = commentId
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        reportsCount = db.query(models.CommentReport).filter(models.CommentReport.comment_id == commentId).count()
        print("reportsCount = " + str(reportsCount))
        if reportsCount >= 5:

            reports = db.query(models.CommentReport).filter(models.CommentReport.comment_id == commentId).all()

            for item in reports:
                db.delete(item)
                db.commit()

            reportedComment: Comments = db.query(models.Comments).get(commentId)
            print("reportedComment = " + reportedComment.text)
            db.delete(reportedComment)
            db.commit()

    return {"success": "true"}