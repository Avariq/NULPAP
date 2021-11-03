from sqlalchemy import create_engine, engine

engine = create_engine("mysql+pymysql://Admin:16w44z88@localhost/onlinecourses")
engine.connect()

print(engine)