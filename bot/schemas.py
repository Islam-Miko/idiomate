from pydantic import BaseModel


class QuizModelSchema(BaseModel):
    id: int
    current_question: int
    correct_answers: int
    user_id: int
    questions: str

    model_config = {"from_attributes": True}
