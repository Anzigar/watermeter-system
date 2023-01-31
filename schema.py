from config import ma
from config import *

#user schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_instance = True

# Initialize schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

#Transaction schema
class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        include_fk = True
        load_instance = True

#Initialize transaction schema
transaction_schema = TransactionSchema()
transaction_schemas = TransactionSchema(many=True)

#Meter schema
class MeterShema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Meter
        include_fk = True
        load_instance = True

#meter schema initialization
meter_chema = MeterShema()
meters_schema = MeterShema(many=True)


#Reading schema
class ReadingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reading
        include_fk = True
        load_instance = True

#Reading initialized
reading_schema = ReadingSchema()
readings_schema = ReadingSchema(many=True)