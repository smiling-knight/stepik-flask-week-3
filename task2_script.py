from dataset.data import goals, teachers
from utils import JsonHandler

JsonHandler.write_db({"goals": goals, "teachers": teachers})
