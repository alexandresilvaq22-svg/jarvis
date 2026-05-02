from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine("sqlite:///jarvis_memory.db")
Session = sessionmaker(bind=engine)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    role = Column(String(20))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)

def save_message(role: str, content: str):
    session = Session()
    msg = Conversation(role=role, content=content)
    session.add(msg)
    session.commit()
    session.close()

def get_recent_history(limit: int = 10):
    session = Session()
    msgs = session.query(Conversation)\
        .order_by(Conversation.id.desc())\
        .limit(limit).all()
    session.close()
    return [{"role": m.role, "content": m.content} for m in reversed(msgs)]

def save_memory(key: str, value: str):
    session = Session()
    mem = session.query(Memory).filter_by(key=key).first()
    if mem:
        mem.value = value
        mem.updated_at = datetime.now()
    else:
        mem = Memory(key=key, value=value)
        session.add(mem)
    session.commit()
    session.close()

def get_all_memories():
    session = Session()
    mems = session.query(Memory).all()
    session.close()
    return {m.key: m.value for m in mems}