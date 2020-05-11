import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)

    #loop to read line from file and insert into db
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", #pylint: disable=no-member
                    {"isbn": isbn, "title": title, "author": author, "year": year})   
    db.commit() #pylint: disable=no-member
    print("Added books to database.")


"""DB schema:
    users:
        username
        useremail
        pwdhash
    books:
        isbn    CHAR primary key
        title   VARCHAR
        author  VARCHAR
        year    CHAR
    reviews:
        rev_id  SERIAL Primary Key
        isbn    CHAR foreign key -> books.isbn
        username    VARCHAR foreign key -> users.username
        rev_rating  integer (1-5)
        rev_text    VARCHAR

"""



if __name__ == "__main__":
    main()
