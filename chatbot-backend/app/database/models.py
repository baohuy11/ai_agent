from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic_core import CoreSchema, core_schema
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetJsonSchemaHandler,
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.is_instance_schema(ObjectId),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x) if isinstance(x, ObjectId) else x
            ),
        )

class PatientInformation(BaseModel):
    full_name: str
    date_of_birth: datetime
    age: int
    gender: str
    occupation: str

class Disease(BaseModel):
    name: str
    
class Symptom(BaseModel):
    name: str
    
class Medicine(BaseModel):
    name: str
    
class Allergy(BaseModel):
    name: str
    
class Person(BaseModel):
    family: str
    diseases: List[Disease]

class AlcoholConsumption(BaseModel):
    alcohol: bool
    frequency: str
    duration: str

class SmokingHabits(BaseModel):
    smoking: bool
    frequency: str
    duration: str
    
class LivingSituation(BaseModel):
    living_situation: str
    
class DailyActivities(BaseModel):
    daily_activities: str
    
class RecentTravelHistory(BaseModel):
    recent_travel: str

class SocialInformation(BaseModel):
    alcohol: AlcoholConsumption
    smoking: SmokingHabits
    living_situation: LivingSituation
    daily_activities: DailyActivities
    recent_travel: RecentTravelHistory
    more_description: str

class MedicalRecord(BaseModel):
    patient_information: PatientInformation
    past_diseases_history: List[Disease]
    current_medications: List[Medicine]
    allergies: List[Allergy]
    family_diseases_history: List[Person]
    social_information: SocialInformation
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

class SymptomsProgression(BaseModel):
    description: str

class DiseasePrediction(BaseModel):
    name: Disease
    percent: str

class Question(BaseModel):
    id: int
    question: str
    description: str
    answer: str

class ChatbotLog(BaseModel):
    symptoms_progression: SymptomsProgression
    patient_symptoms: List[Symptom]
    disease_prediction: List[DiseasePrediction]
    questions: List[Question]
    created_at: datetime = Field(default_factory=datetime.now)
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")