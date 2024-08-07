
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.config.mysqlconnection import MySQLConnection

class Answer:
    DB = "ielts"

    def __init__(self, data):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.question_id = data.get('question_id')
        self.answer = data.get('answer')
        self.is_correct = data.get('is_correct')

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO answers (user_id, question_id, answer, is_correct)
        VALUES (%(user_id)s, %(question_id)s, %(answer)s, %(is_correct)s);
        """
        return connectToMySQL(cls.DB).query_db(query, data)
