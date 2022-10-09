import constants
import parser
import database as db
import formatter as ft
import printer as pt
from aiogram import Bot,Dispatcher,executor
from aiogram.types import Message
import asyncio
import requests
import os 

url = 'https://cabinet.amursu.ru/public_api/groups'
r = requests.get(url)
id_name = {
    x.get('id') : x.get('name') for x in r.json()['groups']
}

for_iteration = list(id_name.items())

formatter = ft.Formatter()
database = db.Database()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


def chunk(lst):
    for i in range(0,len(lst),25):
        yield lst[i:i+25]

def find_index(lst,dub):
    result = []
    for i in dub:
        result.append(lst.index(i))
    return result

def find_not_equal(lst,lst2):
    result = []
    for c,v in enumerate(lst):
        if v != lst2[c]:
            result.append(v)
    return result

chunked = list(chunk(for_iteration))

async def infinite_checker():

    while True:

        for circle in chunked:

            for group in circle:
                week_sc = list(parser.get_schedule(str(group[0]))[1].values())
                format_week_sc = list(formatter.format_week(week_sc))
                database_sc = list(database.get_schedule(str(group[0])))
                is_same = database_sc[1:]==format_week_sc
                print(group,is_same)

                if not is_same:
                    differ = find_not_equal(format_week_sc,database_sc[1:])
                    indexes = find_index(format_week_sc,differ)
                    print(indexes)
                    for index in indexes:

                        printer = pt.Printer(
                            group_id = id_name[group[0]],
                            new_schedule = week_sc[index],
                            weekday = constants.WEEKDAYS[index]
                         )
                        await bot.send_message('-1001852462962', printer.telegram_message())
                        database.update(str(group[0]), format_week_sc)
                        # await bot.send_message('-1001852462962', "база данных обновлена")
                        await asyncio.sleep(2.5)
                print('sleeping for 5 sec.')

                await asyncio.sleep(5)
        print('sleeping for 30min.')
        await asyncio.sleep(1800)
                        
if __name__ == "__main__":
    loop.run_until_complete(infinite_checker())




