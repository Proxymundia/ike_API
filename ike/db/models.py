from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    
    downloads = relationship('Download', back_populates='source')

class Download(Base):
    __tablename__ = 'downloads'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'))
    url = Column(String, nullable=False)  # Updated field name to 'url'
    
    source = relationship('Source', back_populates='downloads')
    documents = relationship('Document', back_populates='download')

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    download_id = Column(Integer, ForeignKey('downloads.id'))
    
    download = relationship('Download', back_populates='documents')
    chunks = relationship('Chunk', back_populates='document')

class Chunk(Base):
    __tablename__ = 'chunks'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    document_id = Column(Integer, ForeignKey('documents.id'))
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    
    document = relationship('Document', back_populates='chunks')
