from numpy import save
from script.iptv import download_schedule, login_and_get_token
from script.infosite import download_infosite_data, get_league_names
from utils.processing import processing_iptv, merge_data_to_excel, processing_iptv_json
import asyncio

start_date = "2025-11-03"
end_date = "2025-11-04"

# asyncio.run(download_schedule(start_date, end_date))


async def main():
    token, device_uuid = await login_and_get_token()
    df = await download_schedule(start_date, end_date, token, device_uuid)
    df = await processing_iptv_json(df)
    print(type(df))


# ✅ 只呼叫一次 asyncio.run
if __name__ == "__main__":
    asyncio.run(main())
