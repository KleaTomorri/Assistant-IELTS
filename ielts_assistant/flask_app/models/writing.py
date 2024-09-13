from flask_app.config.mysqlconnection import connectToMySQL
from datetime import datetime

class WritingResponse:
    DB = "ielts"
    
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.module = data.get('module')
        self.task_number = data.get('task_number')
        self.response = data.get('response')
        self.created_at = data.get('created_at', datetime.now())
        self.updated_at = data.get('updated_at', datetime.now())

    @classmethod
    def save_response(cls, data: dict) -> int:
        
        query = """
        INSERT INTO writing_responses (user_id, module, task_number, response)
        VALUES (%(user_id)s, %(module)s, %(task_number)s, %(response)s);
        """
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result  

    @classmethod
    def get_responses_by_user(cls, user_id: int) -> list:
        
        query = "SELECT * FROM writing_responses WHERE user_id = %(user_id)s;"
        results = connectToMySQL(cls.DB).query_db(query, {"user_id": user_id})
        responses = [cls(row) for row in results]
        return responses
class WritingFeedback:
        DB = "ielts"
    
        def __init__(self, data: dict):
            self.id = data.get('id')
            self.response_id = data.get('response_id')
            self.feedback = data.get('feedback')
            self.created_at = data.get('created_at', datetime.now())
            self.updated_at = data.get('updated_at', datetime.now())

        @classmethod
        def save_feedback(cls, data: dict) -> int:
            """
            Saves feedback for a response to the database.
            Returns the ID of the newly inserted row.
            """
            query = """
            INSERT INTO writing_feedback (response_id, feedback)
            VALUES (%(response_id)s, %(feedback)s);
            """
            result = connectToMySQL(cls.DB).query_db(query, data)
            return result  

        @staticmethod
        def get_feedback(response_id: int):
            query = "SELECT feedback FROM writing_feedback WHERE response_id = %(response_id)s;"
            result = connectToMySQL(WritingFeedback.DB).query_db(query, {"response_id": response_id})
            if result:
                return result[0]['feedback']
            return None
