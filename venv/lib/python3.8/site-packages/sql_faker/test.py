from . sql_faker import Faker, DataType, DBHelper, Values
import random

DBHelper.db_setting('python-sql-faker37')

class EnglishNameRandom:
    def create(self):
        return random.choice(['Jack', 'Andy', 'Sam'])

Faker.table_name("user")\
    .param("id", DataType.ID)\
    .param("name", EnglishNameRandom)\
    .param("age", Values.of_int_range(20, 28))\
    .insert_count(5)\
    .execute()