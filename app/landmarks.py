from pathlib import Path

import osmnx
import sklearn

landmarks_list = {
    "Exeter Cathedral": (50.7224, -3.5299),
    "Exeter St. Davids Station": (50.7294, -3.5434),
    "Exeter Central Station": (50.7265, -3.5339),
    "Streatham Campus": (50.7350, -3.5330),
    "The Quay": (50.7183, -3.5305),
    "St. James Park Station": (50.7309, -3.5225),
    "Polsloe Bridge Station": (50.7312, -3.5021),
    "Digby and Sowton Station": (50.7141, -3.4736),
    "Newcourt Station": (50.7026, -3.4725),
    "Exeter St. Thomas Station": (50.7172, -3.5387),
    "Marsh Barton Station": (50.7043, -3.5214),
    "Exeter Bus Depot": (50.7261, -3.5237),
    "St. Lukes Campus": (50.7228, -3.5169),
    "Royal Devon and Exeter Hospital (Wonford)": (50.7169, -3.5062),
    "Royal Devon and Exeter Hospital (Heavitree)": (50.7245, -3.5138)
}

landmark_nodes = {}

def landmarks(graph):

    for name, (lat, lon) in landmarks_list.items():

        node = osmnx.distance.nearest_nodes(
            graph,
            X=lon,
            Y=lat
        )

        landmark_nodes[node] = name

    return(landmark_nodes)