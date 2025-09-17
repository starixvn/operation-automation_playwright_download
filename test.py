from script.iptv import download_schedule
from utils.processing import process_schedule
import asyncio

start_date = "17/09/2025"
end_date = "18/09/2025"
filename = "schedule12.csv"

# asyncio.run(download_schedule(start_date, end_date, filename))

asyncio.run(process_schedule(filename, start_date, end_date))
