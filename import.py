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
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})   
    db.commit()
    print("Added books to database.")


"""
DB schema should be:
    users:
        username
        useremail
        pwdhash
    books:
        isbn    primary key
        title
        author
        year
    reviews:
        rev_id  primary key integer and autoinc
        isbn    foreign key -> books.isbn
        username    foreign key -> users.username
        rev_rating  integer (1-5)
        rev_text    free text

"""



if __name__ == "__main__":
    main()
