class KanbanLogException(Exception):
    def __init__(self):
        super().__init__("Kanban log in didn't work out")

class loginException(Exception):
    def __init__(self):
        super().__init__("Couldn't log in")