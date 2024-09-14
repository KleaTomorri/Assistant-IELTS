from flask_app.config.mysqlconnection import connectToMySQL


class Question:
    DB = "ielts"

    def __init__(self, data):
        self.id = data.get('id')
        self.passage = data.get('passage')
        self.question_text = data.get('question_text')
        self.correct_answer = data.get('correct_answer')
        self.options = data.get('options')

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO questions (passage, question_text, correct_answer, options)
        VALUES (%(passage)s, %(question_text)s, %(correct_answer)s, %(options)s);
        """
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_by_id(cls, question_id):
        query = "SELECT * FROM questions WHERE id = %(id)s;"
        result = connectToMySQL(cls.DB).query_db({'id': question_id})
        return cls(result[0]) if result else None

    @classmethod
    def get_id_by_text(cls, question_text):
        query = """
        SELECT id FROM questions WHERE question_text = %(question_text)s;
        """
        result = connectToMySQL(cls.DB).query_db({'question_text': question_text})
        return result[0]['id'] if result else None


class UserAnswer:
    DB = "ielts"

    def __init__(self, data):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.question_id = data.get('question_id')
        self.user_answer = data.get('user_answer')
        self.is_correct = data.get('is_correct')

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO user_answers (user_id, question_id, user_answer, is_correct)
        VALUES (%(user_id)s, %(question_id)s, %(user_answer)s, %(is_correct)s);
        """
        return connectToMySQL(cls.DB).query_db(query, data)


class UserProgress:
    DB = "ielts"

    def __init__(self, data):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.total_questions = data.get('total_questions')
        self.correct_answers = data.get('correct_answers')
        self.score = data.get('score')
        self.last_updated = data.get('last_updated')

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO user_progress (user_id, total_questions, correct_answers, score)
        VALUES (%(user_id)s, %(total_questions)s, %(correct_answers)s, %(score)s);
        """
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_by_user_id(cls, user_id):
        query = "SELECT * FROM user_progress WHERE user_id = %(user_id)s;"
        result = connectToMySQL(cls.DB).query_db({'user_id': user_id})
        return cls(result[0]) if result else None

    @classmethod
    def update(cls, user_id, total_questions, correct_answers):
        query = """
        UPDATE user_progress
        SET total_questions = total_questions + %(total_questions)s,
            correct_answers = correct_answers + %(correct_answers)s,
            score = ((correct_answers + %(correct_answers)s) / (total_questions + %(total_questions)s)) * 100,
            last_updated = CURRENT_TIMESTAMP
        WHERE user_id = %(user_id)s;
        """
        data = {
            'user_id': user_id,
            'total_questions': total_questions,
            'correct_answers': correct_answers
        }
        connectToMySQL(cls.DB).query_db(query, data)
