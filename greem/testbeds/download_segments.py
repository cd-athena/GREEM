from utility import download_parallel

all_segments = [
    ("AncientThought_s0{}", 0, 36),
    ("Basketball_s0{}", 0, 1),
    ("Beauty_s0{}", 0, 0),
    ("Bosohorus_s0{}", 0, 0),
    ("BundNightScape_s0{}", 0, 1),
    ("Bunny_s0{}", 0, 1),
    ("Busy_City_s0{}", 0, 24),
    ("CampfireParty_s0{}", 0, 1),
    ("Characters_s0{}", 0, 1),
    ("Childs_Play_s0{}", 0, 18),
    ("CityAlley_s0{}", 0, 1),
    ("ConstructionField_s0{}", 0, 1),
    ("Construction_s0{}", 0, 1),
    ("Crowd_s0{}", 0, 1),
    ("Dolls_s0{}", 0, 1),
    ("Eldorado_s0{}", 0, 35),
    ("FlowerFocus_s0{}", 0, 1),
    ("FlowerKids_s0{}", 0, 1),
    ("Flowers_s0{}", 0, 1),
    ("Fountains_s0{}", 0, 1),
    ("Fun_on_the_river_s0{}", 0, 28),
    ("HoneyBee_s0{}", 0, 0),
    ("Indoor_Soccer_s0{}", 0, 49),
    ("Jockey_s0{}", 0, 0),
    ("Lake_s0{}", 0, 1),
    ("Library_s0{}", 0, 1),
    ("Lifting_Off_s0{}", 0, 39),
    ("Maples_s0{}", 0, 1),
    ("Marathon_s0{}", 0, 1),
    ("Nature_in_the_city_s0{}", 0, 28),
    ("Park_s0{}", 0, 1),
    ("RaceNight_s0{}", 0, 1),
    ("ReadySetGo_s0{}", 0, 0),
    ("ResidentialBuilding_s0{}", 0, 1),
    ("RiverBank_s0{}", 0, 1),
    ("Runners_s0{}", 0, 1),
    ("RushHour_s0{}", 0, 1),
    ("Scarf_s0{}", 0, 0),
    ("Secounds_That_Count_s0{}", 0, 63),
    ("Skateboarding_s0{}", 0, 54),
    ("TallBuildings_s0{}", 0, 1),
    ("TrafficAndBuilding_s0{}", 0, 1),
    ("TrafficFlow_s0{}", 0, 1),
    ("TreeShade_s0{}", 0, 1),
    ("Unspoken_Friend_s0{}", 0, 50),
    ("Wood_s0{}", 0, 1),
    ("YachtRide_s0{}", 0, 0),
]

video_path_list: list[str] = []

for j in range(len(all_segments)):
    for file_name, idx_start, idx_end in [all_segments[j]]:
        for i in range(idx_start, idx_end + 1):
            if i <= 9:
                in_file_full = (
                    f"https://ftp.itec.aau.at/datasets/video-complexity/1-ref/"
                    + file_name.format("0{}.265".format(i))
                )
            else:
                in_file_full = (
                    "https://ftp.itec.aau.at/datasets/video-complexity/1-ref/"
                    + file_name.format("{}.265".format(i))
                )
            video_path_list.append(in_file_full)

video_input_outputs: list[tuple[str, str]] = [
    (video, "dataset/ref_265") for video in video_path_list
]

download_parallel(video_input_outputs)
