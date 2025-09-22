from numpy import save
from script.iptv import download_schedule
from script.infosite import download_infosite_data, get_league_names
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

leagues_groups = [
    "Soccerway",
    "IMG",
    "Virtual",
    "RB Upload",
    "RTS Upload",
    "BG Upload",
    "BETRADAR Upload",
]
start_time = "2025-09-18"
end_time = "2025-09-19"
result = asyncio.run(
    get_league_names(
        start_time=start_time,
        end_time=end_time,
        leagues_groups=leagues_groups,
    )
)
result = [label for label in result if "-" not in label]
print(len(result))
# leagues = result[:300]

asyncio.run(
    download_infosite_data(
        start_time=start_time,
        end_time=end_time,
        filename=f"{start_time}_{end_time}",
        leagues=result,
        league_groups=leagues_groups,
        sports=["Soccer"],
        batch_size=50,
    )
)
