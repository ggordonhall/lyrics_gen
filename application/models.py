from application import db

class SourceText(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(), index=True, unique=True)
    file_text = db.Column(db.String(), index=True, unique=True)

    def __repr__(self):
        return self.file_text.decode('utf-8')

class SourceRhymes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(), index=True, unique=True)
    file_text = db.Column(db.String(), index=True, unique=True)

    def __repr__(self):
        return self.file_text.decode('utf-8')
