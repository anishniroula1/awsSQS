from dataclasses import dataclass
from typing import Optional
import dacite
import json


@dataclass
class Person:
    count: Optional[int]


@dataclass
class Age:
    number: int


@dataclass
class User(Age, Person):
    name: str

    def multiply_age(self):
        return self.number * 20


json_data = {"name": "John", "age": {"number": 25}, "number": 100, "count": 300}
# data_dict = json.loads(json_data)
user = dacite.from_dict(User, json_data)
print(user.multiply_age())
