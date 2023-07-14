from fastapi import FastAPI
from pydantic import BaseModel 
from sqlite3 import connect
from random import randint

app=FastAPI()

class Step(BaseModel):
    tile: str


@app.post("/new_game")
def create_new_game():
    with connect('database.db') as connection:
        cur = connection.cursor()
        cur.execute('INSERT INTO "game" ("id") VALUES (NULL) ;')
        game_id=cur.lastrowid       #Получает id только что созданной игры 
        connection.commit()
    return game_id

@app.post("game/{id}/turn/")
def make_step(id, step: Step): 
    tile=step.tile  
    with connect('database.db') as connection:
        cur = connection.cursor()
        cur.execute(f'UPDATE "game" SET "{tile}" = "False" WHERE id = {id};')
        connection.commit()
    
    return {"message": "Turn successfully made."}
        
