from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlite3 import connect
from random import choice

app = FastAPI()


class Turn(BaseModel):
    tile: str


@app.post("/new_game")
def create_new_game():
    with connect('database.db') as connection:
        cur = connection.cursor()
        cur.execute('INSERT INTO "game" ("id") VALUES (NULL);')
        game_id = cur.lastrowid
        connection.commit()
    return {"game_id": game_id}


@app.post("/game/{id}/turn/")
def make_turn(id, turn: Turn ):
    tile = turn.tile


    if not right_tile(tile):
        raise HTTPException(status_code=400, detail="Неверный формат поля")
    
    with connect('database.db') as connection:
        cur = connection.cursor()

        # Проверка на существование игры(id)
        cur.execute('SELECT * FROM "game" WHERE "id" = ?;', (id,))
        game = cur.fetchone()
        if not game:  #Если game пуста
            raise HTTPException(status_code=404, detail="Такой игры нет!")       

        # Проверяет свободна ли плитка
        cur.execute(f'SELECT "{tile}" FROM "game" WHERE "id" = ?;', (id,))
        result = cur.fetchone()
        if result[0] != None:
            raise HTTPException(status_code=400, detail="Это место уже занято!")

        # Заполняет клетку 0
        cur.execute(f'UPDATE "game" SET "{tile}" = ? WHERE "id" = ?;', (0, id))  #пользователь ходит ноликами
        connection.commit()

        # Ход бота
        bot_tile = make_bot_step(cur, id)

        # Проверка победы бота
        if check_win(cur, id, 1):
            return {"Бот выиграл!"}
        
        # Обновленное состояние игры после хода бота
        cur.execute(f'SELECT * FROM "game" WHERE "id" = ?;', (id,))
        game_data = cur.fetchone()
        
        # Проверка на победу игрока
        if check_win(game_data, 0):
            return {"Игрок выиграл!!"}

        # Возврат обновленной матрицы   
        return game_data

# Проверка, что поле имеет правильный формат (A1 и тд)
def right_tile(tile: str):
    return len(tile) == 2 and tile[0].isalpha() and tile[1].isdigit()


def make_bot_step(cur, id):                     
    cur.execute(f'SELECT * FROM "game" WHERE "id" = ?;', (id,))
    game_data = cur.fetchone()
    
    # Список доступных полей
    possible_tiles = []
    for tile_name in game_data.keys():
        if  tile_name != "id" and  game_data[tile_name] == None:  #проверка что поле доступно
            possible_tiles.append(tile_name)

    # Рандомная выбока места для хода бота
    bot_tile = choice(possible_tiles)   #choise -из модуля random выбирает из списка рандомное поле



    # Заполнение поля
    cur.execute(f'UPDATE "game" SET "{bot_tile}" = ? WHERE "id" = ?;', (1, id))
    cur.connection.commit()

    # Обновление состояния игры после хода бота
    cur.execute(f'SELECT * FROM "game" WHERE "id" = ?;', (id,))
    game_data = cur.fetchone()
    return game_data

#Проверка на выигрыш
def check_win(game_data, symbol):

    #Возможные комбинации выигрыша
    win_option = [
        # Горизонталь
        ["A1", "A2", "A3"],
        ["B1", "B2", "B3"],
        ["C1", "C2", "C3"],
        # Вертикаль
        ["A1", "B1", "C1"],
        ["A2", "B2", "C2"],
        ["A3", "B3", "C3"],
        # Диагональ
        ["A1", "B2", "C3"],
        ["A3", "B2", "C1"]
    ]

    for option in win_option:
        if all(game_data[tile] == symbol for tile in option):
            return True

    return False
#Проверить чтобы пользователь правильно вводил A1,B3 и т.д