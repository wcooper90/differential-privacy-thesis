"""
MBox objects for serverside processing.
"""
import email
from email.policy import default


class MboxReader:
    def __init__(self, filename):
        self.filename = filename + '/' + filename
        self.length = self.calculate_length()
        self.handle = open(self.filename, 'rb')
        # sometimes the first line of an mbox file begins with a line break
        # assert first_line.startswith(b'From ') or first_line.startswith('\n')

    # calculate number of emails in this mbox file for tqdm
    def calculate_length(self):
        self.handle = open(self.filename, 'rb')
        length = 0
        while True:
            line = self.handle.readline()
            if line == b'' or line.startswith(b'From '):
                if line == b'':
                    break
                length += 1
                lines = []
                continue
        self.exit()
        return length

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.handle.close()

    def exit(self):
        self.handle.close()

    def __iter__(self):
        return iter(self.__next__())

    def __next__(self):
        lines = []
        while True:
            line = self.handle.readline()
            if line == b'' or line.startswith(b'From '):
                try:
                    yield email.message_from_bytes(b''.join(lines), policy=default)
                except:
                    yield -1
                if line == b'':
                    break
                lines = []
                continue
            lines.append(line)


class MessageObject():
    def __init__(self):
        self.to = None
        self.from_ = None
        self.subject = None
        self.date = None
        self.content = None
        self.id = None

        self.valid_message = True
        self.parent_id = None


    def dictify(self):
        self.content = self.content.replace('\n', ':|:')
        return {"id": self.id, "to": self.to, "from": self.from_, "subject": self.subject,
                "date": self.date, "content": self.content, "parent-id": self.parent_id}


    def __repr__(self):
        return str({"id": self.id, "to": self.to, "from": self.from_, "subject": self.subject,
                "date": self.date, "content": self.content, "parent-id": self.parent_id})
