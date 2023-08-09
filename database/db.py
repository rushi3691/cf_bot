import asyncio
from databases import Database
import aiohttp
import psycopg2.extras
import psycopg2
from utils.logger import logger
from pprint import pprint
# from utils.logger import logger
# from tabulate import tabulate
import os

# db_name = os.getenv('DB_NAME')
db = Database(os.getenv('DATABASE_URL'), min_size=3, max_size=5)


async def disconn_db():
    """disconnect from database"""
    await db.disconnect()

async def connect_db():
    """connect to database"""
    await db.connect()
    
async def fetch_problems():
    url = 'https://codeforces.com/api/problemset.problems'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            err = resp.status
            data = await resp.json()
            # print("fetched data",data)
            return data, err

async def create_Questions_table():
    if not db.is_connected:
        await db.connect()

    query = """ 
      DROP TABLE IF EXISTS Questions
    """
    await db.execute(query=query)

    # creating questions table
    query = """ 
      CREATE TABLE Questions (
      id SERIAL PRIMARY KEY, 
      qid VARCHAR(10) NOT NULL UNIQUE,
      contestId INTEGER,
      qindex VARCHAR(10),
      name VARCHAR(100) NOT NULL,
      rating INTEGER,
      type VARCHAR(100)
    )
    """
    await db.execute(query=query)    
    logger.info("Created Questions table")

async def create_Questions_User_Done_table():

    if not db.is_connected:
        await db.connect()

    query = """ 
      DROP TABLE IF EXISTS Questions_User_Done
    """
    await db.execute(query=query)

    query  = """ 
      CREATE TABLE Questions_User_Done (
      id SERIAL PRIMARY KEY,
      user_id INTEGER,
      question_id VARCHAR(10) NOT NULL
    )
    """
    #   CONSTRAINT fk_question 
    #     FOREIGN KEY(question_id) 
    #       REFERENCES Questions(qid) 
    await db.execute(query=query)
    logger.info("Created Questions_User_Done table!")

async def create_table():
    await create_Questions_table()
    await create_Questions_User_Done_table()
    logger.info("Migration Done!")

def _batch_insert_psycopg(values: list):
    connection = psycopg2.connect(
        host = os.getenv('DB_HOST'),
        database = os.getenv('DB_NAME'),
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD'),
    )
    connection.autocommit = True
    with connection:
      with connection.cursor() as cursor:
          psycopg2.extras.execute_batch(cursor, """
              INSERT INTO Questions 
              (qid,contestId,qindex,name,rating,type) 
              VALUES (
                  %(qid)s,
                  %(contestId)s,
                  %(qindex)s,
                  %(name)s,
                  %(rating)s,
                  %(type)s
              );""", values, page_size = 1000)
    connection.close()

async def batch_insert_psycopg(values: list):
    if db.is_connected:
        await db.disconnect()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _batch_insert_psycopg, values)
     

async def get_fillable_data():
    data, _ = await fetch_problems()
    values = []
    for i in data['result']['problems']:
        try:
            problem = {
                'qid': f"{i['contestId']}{i['index']}",
                'contestId': i.get('contestId'),
                'qindex': i.get('index'),
                'name': i.get('name'),
                'rating': i.get('rating'),
                'type': i.get('type')
            }
            values.append(problem)
        except Exception as e:
            logger.warning(f"error occured at {i}")
    return values

async def update_questions():
    logger.info("Updating Questions Database!")
    await create_Questions_table()

    values = await get_fillable_data()
    await batch_insert_psycopg(values)

    logger.info("Questions Database Updated!")   

async def insert_questions():
    logger.info("inserting Questions Data...")

    values = await get_fillable_data()
    await batch_insert_psycopg(values)

    logger.info("Questions inserted successfully!")

async def mark_done_many(done_list: list, user_id: int):
    if not db.is_connected:
        await db.connect()
    logger.info(f"user {user_id}")
    query = f"""
      INSERT INTO Questions_User_Done
      (user_id, question_id)
      VALUES 
      ({user_id}, :question_id)
    """
    # logger.info(query)
    await db.execute_many(query=query,values=done_list)
    logger.info(f"user: {user_id} marked questions as done")

async def reset_p(user_id):
    if not db.is_connected:
        await db.connect()

    query = f"""
      DELETE 
      FROM Questions_User_Done 
      WHERE user_id={user_id} 
    """
    await db.execute(query=query)
    logger.info(f"progress of user: {user_id} reseted")

def qgen_helper(count, min_rating, user_id):
    return f""" 
        SELECT Q.*
        FROM Questions as Q
        WHERE Q.qid NOT IN (
            SELECT B.question_id
            FROM Questions_User_Done as B
            WHERE B.user_id={user_id}
        ) AND rating>={min_rating} and rating<={min_rating+100}
        LIMIT {count}
    """

async def get_randqs(min_rating: int, user_id: int, user_config: dict):
    if not db.is_connected:
        await db.connect()

    easy_lim = user_config[user_id]['easy_count']
    med_lim = user_config[user_id]['medium_count']
    hard_lim = user_config[user_id]['hard_count']

    query = f"""SELECT * FROM ({qgen_helper(easy_lim, min_rating, user_id)}) as a
        UNION
        SELECT * FROM ({qgen_helper(med_lim, min_rating + 200, user_id)}) as b
        UNION
        SELECT * FROM ({qgen_helper(hard_lim, min_rating + 400, user_id)}) as c
        """
    # logger.info(f"get_randqs: {query}")
    data = await db.fetch_all(query=query)
    return data 

async def show_p(user_id, level=None):
    if not db.is_connected:
        await db.connect()

    if not level:
        query = f""" 
          SELECT COUNT(*) 
          FROM Questions_User_Done as D
          WHERE D.user_id={user_id}
        """
        x = await db.fetch_val(query=query)
        ans = ["all",x]
        return ans
    if level:
        query = f"""
          SELECT COUNT(*)
          FROM (
              SELECT * 
              FROM Questions_User_Done as D
              WHERE D.user_id={user_id}
          ) as SQ
          INNER JOIN Questions as Q 
            ON SQ.question_id=Q.qid
          WHERE Q.rating={level}
        """
        x = await db.fetch_val(query=query)
        ans = [level,x]
        return ans
