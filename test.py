from script.iptv import download_schedule
from script.infosite import download_infosite_data
from utils.processing import processing_iptv, merge_data_to_excel
import asyncio

# start_date = "17/09/2025"
# end_date = "18/09/2025"
# filename = "schedule12.csv"

# asyncio.run(download_schedule(start_date, end_date, filename))

# asyncio.run(process_schedule(filename, start_date, end_date))
# filename = "schedule12"
# asyncio.run(
#     merge_data_to_excel(
#         iptv_path=f"./data/iptv/processed/processed_{filename}.csv",
#         infosite_path=f"./data/infosite/EvtSched-2025-09-16 - 2025-09-17.xls",
#         output_filename=f"{filename}_merged",
#     )
# )

asyncio.run(
    download_infosite_data(
        start_time="2025-09-16",
        end_time="2025-09-17",
    )
)
