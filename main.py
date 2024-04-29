from typing import Union
from fastapi import FastAPI,HTTPException
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()

# Replace the connection string with your MongoDB Atlas connection string
connection_string = "mongodb+srv://ramkumar:Ys9DnjTKnxkH0mXM@cluster0.gd6hvr9.mongodb.net/"

# Create a MongoClient instance
client = MongoClient(connection_string)

# Access your database
db = client.mydatabase  # Replace "mydatabase" with your database name
collection = db['mycollection']


class user(BaseModel):
    name: str
    id: str

@app.post("/mongodata/")
def mongodata(name: str, id: str):
    user = {"name": name, "id": id}
    inserted_document = collection.insert_one(user)
    print("Inserted document ID:", inserted_document.inserted_id)


@app.delete("/mongodatadelete/{document_id}")
def delete_document(document_id: str):
    # Find the document with the specified ID
    result = collection.delete_one({"id": document_id})

    # Check if the document was found and deleted
    if result.deleted_count == 1:
        return {"message": f"Document with ID {document_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": "hi man"}


def calculate_sum_of_digits(number: int) -> int:
    total = 0
    # Extract individual digits and sum them
    while number:
        total += number % 10
        number //= 10
    return total


@app.get("/calculate-sum/{numbers}")
def calculate_sum(numbers: int):
    result = calculate_sum_of_digits(numbers)
    return {"sum": result}
