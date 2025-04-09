from pymongo import MongoClient
from typing import Optional, List
import os
from dotenv import load_dotenv
from models import Roadmap, Quiz, Resource
from bson import ObjectId
from pymongo.operations import SearchIndexModel
from sentence_transformers import SentenceTransformer

load_dotenv()
