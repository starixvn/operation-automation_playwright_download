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
]
start_time = "2025-09-23"
end_time = "2025-09-24"
# result = asyncio.run(
#     get_league_names(
#         start_time=start_time,
#         end_time=end_time,
#         leagues_groups=leagues_groups,
#     )
# )
# print(len(result))
# # result = [label for label in result if "-" not in label]
# # print(len(result))
# # # leagues = result[:300]
# # {
# #     "start_time": "{{ $('Code').item.json.today_ymd }}",
# #     "end_time": "{{ $('Code').item.json.tomorrow_ymd }}",
# #     "filename": "{{ $('Code').item.json.today_ymd }}_{{ $('Code').item.json.tomorrow_ymd }}",
# #     "league_groups": ["Soccerway"],
# #     "sports": ["Soccer"],
# #     "leagues": [
# #         "*ENGLISH PREMIER LEAGUE",
# #         "*GERMANY-BUNDESLIGA",
# #         "*SPAIN PRIMERA LALIGA",
# #         "*ITALY SERIE A",
# #         "FRANCE LIGUE 1",
# #     ],
# #     "save_features": ["website1", "website2", "website3", "website4"],
# #     "batch_size": 50,
# # }

leagues = [
    "*SPAIN PRIMERA LALIGA",
    "*UEFA EUROPA LEAGUE",
]
asyncio.run(
    download_infosite_data(
        start_time=start_time,
        end_time=end_time,
        filename=f"{start_time}_{end_time}",
        leagues=leagues,
        league_groups=leagues_groups,
        sports=["Soccer"],
        save_features=["website1", "website2", "website3", "website4"],
        batch_size=50,
    )
)
