from flask_app.config.mysqlconnection import connectToMySQL

class ListeningPassage:
    DB = "ielts"

    def __init__(self, data):
        self.id = data.get('id')
        self.topic = data.get('topic')
        self.passage_text = data.get('passage_text')
        self.audio_url = data.get('audio_url')

    @classmethod
    def save(cls, data):
        query = "INSERT INTO listening_passages (topic, passage_text, audio_url) VALUES (%(topic)s, %(passage_text)s, %(audio_url)s);"
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_by_id(cls, data):
        query = "SELECT * FROM listening_passages WHERE id = %(id)s;"
        result = connectToMySQL(cls.DB).query_db(query, data)
        return cls(result[0]) if result else None

class ListeningQuestion:
    DB = "ielts"

    def __init__(self, data):
        self.id = data.get('id')
        self.passage_id = data.get('passage_id')
        self.question_text = data.get('question_text')

    @classmethod
    def save(cls, data):
        query = "INSERT INTO listening_questions (passage_id, question_text) VALUES (%(passage_id)s, %(question_text)s);"
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_by_passage_id(cls, data):
        query = "SELECT * FROM listening_questions WHERE passage_id = %(passage_id)s;"
        results = connectToMySQL(cls.DB).query_db(query, data)
        return [cls(result) for result in results]

class ListeningAnswer:
    DB = "ielts"

    def __init__(self, data):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.question_id = data.get('question_id')
        self.answer = data.get('answer')
        self.is_correct = data.get('is_correct')

    @classmethod
    def save(cls, data):
        query = "INSERT INTO listening_answers (user_id, question_id, answer, is_correct) VALUES (%(user_id)s, %(question_id)s, %(answer)s, %(is_correct)s);"
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_by_user_id(cls, data):
        query = "SELECT * FROM listening_answers WHERE user_id = %(user_id)s;"
        results = connectToMySQL(cls.DB).query_db(query, data)
        return [cls(result) for result in results]
