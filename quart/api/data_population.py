import json
import sqlite3

def correct_json():
    with open("correct.json", 'r') as f:
        data = json.load(f)
    return data

def valid_json():
    with open("valid.json", 'r') as f:
        data = json.load(f)
    return list(data)

def populate_valid_words():
    
    conn = sqlite3.connect('wordle.db')
    c = conn.cursor()

    
    data = valid_json()+correct_json()
    k = 1
    value = []
    for i in range(len(data)):
        tmp = []
        tmp.append(k)
        tmp.append(data[i])
        value.append(tuple(tmp))
        k+=1
        tmp.clear()
    print(value)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          

    #insert multiple records in a single query
    c.executemany('INSERT INTO ValidSecretWords VALUES(?,?);',value)

    print('We have inserted', c.rowcount, 'records to the table.')

    conn.commit()
    #close the connection
    conn.close()


def populate_correct_words():
        
    conn = sqlite3.connect('wordle.db')
    c = conn.cursor()

    
    data = correct_json()
    k = 1
    value = []
    for i in range(len(data)):
        tmp = []
        tmp.append(k)
        tmp.append(data[i])
        value.append(tuple(tmp))
        k+=1
        tmp.clear()
    print(value)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          

    #insert multiple records in a single query
    c.executemany('INSERT INTO SecretWords VALUES(?,?);',value)

    print('We have inserted', c.rowcount, 'records to the table.')

    conn.commit()
    #close the connection
    conn.close()

populate_valid_words()
populate_correct_words()
