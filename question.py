
class Question():
    def __init__(self, question, user_asked):
        self.question = question
        self.user_asked = user_asked
        self.user_reply = None
        self.to_be_asked = None
        self.answered = False
        self.chatting = None

    def __repr__(self):
        return self.question

    def __str__(self):
        return self.question
