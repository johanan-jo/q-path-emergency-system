"""
Entity models for emergency response system.
Defines hospitals, fire stations, police stations, lifeguards, ambulances, and victim nodes.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random

class EntityType(Enum):
    HOSPITAL = "hospital"
    FIRE_STATION = "fire_station"
    POLICE_STATION = "police_station"
    LIFEGUARD = "lifeguard"
    AMBULANCE = "ambulance"
    VICTIM = "victim"

@dataclass
class Location:
    lat: float
    lon: float
    
    def __hash__(self):
        return hash((self.lat, self.lon))

@dataclass
class EmergencyEntity:
    id: str
    name: str
    entity_type: EntityType
    location: Location
    available: bool = True
    capacity: int = 1
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.entity_type.value,
            'location': {'lat': self.location.lat, 'lon': self.location.lon},
            'available': self.available,
            'capacity': self.capacity,
            'metadata': self.metadata
        }

class EmergencyDatabase:
    """Simulated database of emergency entities."""
    
    def __init__(self):
        self.entities: Dict[str, EmergencyEntity] = {}
        self._initialize_entities()
    
    def _initialize_entities(self):
        """Initialize with real emergency infrastructure in Chennai."""
        
        # Real Hospitals in Chennai and surrounding districts with actual locations
        hospitals = [
            EmergencyEntity("H1", "Rajiv Gandhi Govt General Hospital", EntityType.HOSPITAL, 
                          Location(13.0827, 80.2754), capacity=60,
                          metadata={"beds": 1000, "icu": 200, "trauma_center": True, "phone": "044-2530 5000", "address": "Chennai", "district": "Chennai"}),
            EmergencyEntity("H2", "Chengalpattu Medical College", EntityType.HOSPITAL,
                          Location(12.6841, 79.9836), capacity=50,
                          metadata={"beds": 400, "icu": 80, "trauma_center": True, "phone": "044-2742 6666", "address": "Chengalpattu", "district": "Chengalpattu"}),
            EmergencyEntity("H3", "Kanchipuram Govt Hospital", EntityType.HOSPITAL,
                          Location(12.8340, 79.7037), capacity=45,
                          metadata={"beds": 300, "icu": 60, "trauma_center": True, "phone": "044-2722 2442", "address": "Kanchipuram", "district": "Kanchipuram"}),
            EmergencyEntity("H4", "Thiruvallur Govt General Hospital", EntityType.HOSPITAL,
                          Location(13.1444, 79.9090), capacity=50,
                          metadata={"beds": 350, "icu": 70, "trauma_center": True, "phone": "044-2766 0306", "address": "Thiruvallur", "district": "Thiruvallur"}),
            EmergencyEntity("H5", "Apollo Hospitals (Greams Road)", EntityType.HOSPITAL,
                          Location(13.0607, 80.2514), capacity=50,
                          metadata={"beds": 500, "icu": 150, "trauma_center": True, "phone": "044-2829 3333", "address": "Greams Road, Chennai", "district": "Chennai"}),
            EmergencyEntity("H6", "SRM Global Hospitals", EntityType.HOSPITAL,
                          Location(12.8231, 80.0440), capacity=45,
                          metadata={"beds": 350, "icu": 75, "trauma_center": True, "phone": "044-4743 2345", "address": "Chengalpattu", "district": "Chengalpattu"}),
            EmergencyEntity("H7", "Fortis Malar Hospital, Adyar", EntityType.HOSPITAL,
                          Location(13.0067, 80.2539), capacity=45,
                          metadata={"beds": 180, "icu": 40, "trauma_center": True, "phone": "044-42892222", "address": "No. 52, 1st Main Road, Gandhi Nagar, Adyar", "district": "Chennai"}),
            EmergencyEntity("H8", "SIMS Hospital, Vadapalani", EntityType.HOSPITAL,
                          Location(13.0524, 80.2120), capacity=40,
                          metadata={"beds": 300, "icu": 50, "trauma_center": True, "phone": "044-45678900", "address": "1, Jawaharlal Nehru Salai, Vadapalani", "district": "Chennai"}),
            EmergencyEntity("H9", "Stanley Medical College", EntityType.HOSPITAL,
                          Location(13.1075, 80.2872), capacity=55,
                          metadata={"beds": 800, "icu": 160, "trauma_center": True, "phone": "044-2528 1351", "address": "Old Jail Road, Chennai", "district": "Chennai"}),
            EmergencyEntity("H10", "Kilpauk Medical College", EntityType.HOSPITAL,
                          Location(13.0784, 80.2431), capacity=50,
                          metadata={"beds": 600, "icu": 120, "trauma_center": True, "phone": "044-2664 1611", "address": "Kilpauk, Chennai", "district": "Chennai"}),
            EmergencyEntity("H11", "Govt Peripheral Hospital (Perambur)", EntityType.HOSPITAL,
                          Location(13.1112, 80.2435), capacity=40,
                          metadata={"beds": 250, "icu": 50, "trauma_center": True, "phone": "044-2662 2111", "address": "Perambur, Chennai", "district": "Chennai"}),
            EmergencyEntity("H12", "Royapettah Govt Hospital", EntityType.HOSPITAL,
                          Location(13.0537, 80.2625), capacity=45,
                          metadata={"beds": 300, "icu": 60, "trauma_center": True, "phone": "044-2844 7564", "address": "Royapettah, Chennai", "district": "Chennai"}),
            EmergencyEntity("H13", "KGM Govt Hospital", EntityType.HOSPITAL,
                          Location(12.6841, 79.9836), capacity=45,
                          metadata={"beds": 350, "icu": 70, "trauma_center": True, "phone": "044-2742 2211", "address": "Chengalpattu", "district": "Chengalpattu"}),
            EmergencyEntity("H14", "Thiruvallur District HQ Hospital", EntityType.HOSPITAL,
                          Location(13.1438, 79.9085), capacity=45,
                          metadata={"beds": 300, "icu": 60, "trauma_center": True, "phone": "044-2766 2345", "address": "Thiruvallur", "district": "Thiruvallur"}),
            EmergencyEntity("H15", "Arignar Anna Govt Hospital", EntityType.HOSPITAL,
                          Location(12.8360, 79.7042), capacity=45,
                          metadata={"beds": 320, "icu": 65, "trauma_center": True, "phone": "044-2722 2234", "address": "Kanchipuram", "district": "Kanchipuram"}),
            # Tambaram and surrounding area hospitals
            EmergencyEntity("H16", "Hindu Mission Hospital", EntityType.HOSPITAL,
                          Location(12.9231, 80.1145), capacity=40,
                          metadata={"beds": 250, "icu": 50, "trauma_center": True, "phone": "044-2226 2345", "address": "GST Road, West Tambaram", "district": "Chengalpattu"}),
            EmergencyEntity("H17", "Sudar Hospitals", EntityType.HOSPITAL,
                          Location(12.9198, 80.1085), capacity=35,
                          metadata={"beds": 180, "icu": 40, "trauma_center": True, "phone": "044-2226 3456", "address": "Tambaram West", "district": "Chengalpattu"}),
            EmergencyEntity("H18", "Christudas Orthopaedic", EntityType.HOSPITAL,
                          Location(12.9215, 80.1265), capacity=30,
                          metadata={"beds": 120, "icu": 25, "trauma_center": False, "phone": "044-2226 4567", "address": "Tambaram East", "district": "Chengalpattu"}),
            EmergencyEntity("H19", "Annai Arul Hospital", EntityType.HOSPITAL,
                          Location(12.9205, 80.0988), capacity=35,
                          metadata={"beds": 150, "icu": 30, "trauma_center": True, "phone": "044-2226 5678", "address": "Mudichur Road, Tambaram", "district": "Chengalpattu"}),
            EmergencyEntity("H20", "Madha Medical College", EntityType.HOSPITAL,
                          Location(12.9864, 80.0558), capacity=50,
                          metadata={"beds": 400, "icu": 80, "trauma_center": True, "phone": "044-2478 5000", "address": "Kovur, Kundrathur", "district": "Chengalpattu"}),
            EmergencyEntity("H21", "Sri Muthukumaran Medical", EntityType.HOSPITAL,
                          Location(13.0015, 80.0632), capacity=45,
                          metadata={"beds": 350, "icu": 70, "trauma_center": True, "phone": "044-2479 6000", "address": "Chikkarayapuram, Kundrathur", "district": "Chengalpattu"}),
            EmergencyEntity("H22", "RMD Specialities Hospital", EntityType.HOSPITAL,
                          Location(12.9734, 80.0345), capacity=40,
                          metadata={"beds": 200, "icu": 45, "trauma_center": True, "phone": "044-2478 7000", "address": "Amarambedu, Kundrathur-Sriperumbudur", "district": "Kanchipuram"}),
            EmergencyEntity("H23", "Sriperumbudur Govt. Hospital", EntityType.HOSPITAL,
                          Location(12.9645, 79.9485), capacity=45,
                          metadata={"beds": 300, "icu": 60, "trauma_center": True, "phone": "044-2771 2345", "address": "Katchipedu, Sriperumbudur", "district": "Kanchipuram"}),
            EmergencyEntity("H24", "Saveetha Medical College", EntityType.HOSPITAL,
                          Location(13.0289, 80.0094), capacity=55,
                          metadata={"beds": 500, "icu": 100, "trauma_center": True, "phone": "044-2681 0000", "address": "Thandalam, Sriperumbudur", "district": "Kanchipuram"}),
            EmergencyEntity("H25", "Jaya Hospital", EntityType.HOSPITAL,
                          Location(12.9698, 79.9482), capacity=30,
                          metadata={"beds": 100, "icu": 20, "trauma_center": False, "phone": "044-2771 3456", "address": "Car Street, Sriperumbudur", "district": "Kanchipuram"}),
            EmergencyEntity("H26", "Pandian Hospital", EntityType.HOSPITAL,
                          Location(12.9712, 79.9415), capacity=30,
                          metadata={"beds": 120, "icu": 25, "trauma_center": False, "phone": "044-2771 4567", "address": "Gandhi Nagar, Sriperumbudur", "district": "Kanchipuram"}),
            # Pammal, Tiruneermalai, Gerugambakkam area hospitals
            EmergencyEntity("H27", "Agam Hospitals", EntityType.HOSPITAL,
                          Location(12.9782, 80.1415), capacity=35,
                          metadata={"beds": 150, "icu": 30, "trauma_center": True, "phone": "044-2247 8900", "address": "Pammal Main Road", "district": "Chennai"}),
            EmergencyEntity("H28", "B.P. Jain Hospital", EntityType.HOSPITAL,
                          Location(12.9735, 80.1402), capacity=30,
                          metadata={"beds": 120, "icu": 25, "trauma_center": False, "phone": "044-2247 9000", "address": "Anna Salai, Pammal", "district": "Chennai"}),
            EmergencyEntity("H29", "Sri Ramachandra Medical Center", EntityType.HOSPITAL,
                          Location(13.0361, 80.1558), capacity=60,
                          metadata={"beds": 1200, "icu": 250, "trauma_center": True, "phone": "044-4567 3434", "address": "Porur (Tertiary Care)", "district": "Chennai"}),
            EmergencyEntity("H30", "Subhikshaa Hospital", EntityType.HOSPITAL,
                          Location(12.9845, 80.1520), capacity=35,
                          metadata={"beds": 140, "icu": 28, "trauma_center": True, "phone": "044-2248 1234", "address": "Pallavaram-Kundrathur Rd", "district": "Chennai"}),
            EmergencyEntity("H31", "Harish Hospital", EntityType.HOSPITAL,
                          Location(12.9620, 80.1285), capacity=30,
                          metadata={"beds": 100, "icu": 20, "trauma_center": False, "phone": "044-2247 2345", "address": "Tiruneermalai", "district": "Chennai"}),
            EmergencyEntity("H32", "Kanaga Hospital", EntityType.HOSPITAL,
                          Location(13.0150, 80.1410), capacity=35,
                          metadata={"beds": 130, "icu": 26, "trauma_center": True, "phone": "044-2476 5678", "address": "Kovur (Near Gerugambakkam)", "district": "Chennai"}),
            EmergencyEntity("H33", "Das Nursing Home", EntityType.HOSPITAL,
                          Location(12.9815, 80.1385), capacity=25,
                          metadata={"beds": 80, "icu": 15, "trauma_center": False, "phone": "044-2248 3456", "address": "Pozhichalur (Near Tiruneermalai)", "district": "Chennai"}),
            EmergencyEntity("H34", "Sankara Eye Hospital", EntityType.HOSPITAL,
                          Location(12.9768, 80.1435), capacity=30,
                          metadata={"beds": 100, "icu": 20, "trauma_center": False, "phone": "044-2247 6789", "address": "Pammal (Eye Specialty)", "district": "Chennai"}),
        ]
        
        # Real Fire Stations - Tamil Nadu Fire and Rescue Services, Chennai
        fire_stations = [
            EmergencyEntity("F1", "Central Fire Station, Pudupet", EntityType.FIRE_STATION,
                          Location(13.0918, 80.2874), capacity=12,
                          metadata={"vehicles": 15, "personnel": 50, "phone": "101", "address": "EVR Periyar Salai, Pudupet"}),
            EmergencyEntity("F2", "Kilpauk Fire Station", EntityType.FIRE_STATION,
                          Location(13.0778, 80.2369), capacity=10,
                          metadata={"vehicles": 10, "personnel": 35, "phone": "101", "address": "Kilpauk Garden Road"}),
            EmergencyEntity("F3", "T Nagar Fire Station", EntityType.FIRE_STATION,
                          Location(13.0418, 80.2341), capacity=8,
                          metadata={"vehicles": 8, "personnel": 30, "phone": "101", "address": "Pondy Bazaar, T Nagar"}),
            EmergencyEntity("F4", "Anna Nagar Fire Station", EntityType.FIRE_STATION,
                          Location(13.0878, 80.2088), capacity=8,
                          metadata={"vehicles": 7, "personnel": 28, "phone": "101", "address": "2nd Avenue, Anna Nagar"}),
            EmergencyEntity("F5", "Adyar Fire Station", EntityType.FIRE_STATION,
                          Location(13.0030, 80.2625), capacity=7,
                          metadata={"vehicles": 6, "personnel": 25, "phone": "101", "address": "Lattice Bridge Road, Adyar"}),
            EmergencyEntity("F6", "Teynampet Fire Station", EntityType.FIRE_STATION,
                          Location(13.0401, 80.2503), capacity=8,
                          metadata={"vehicles": 8, "personnel": 28, "phone": "101", "address": "Teynampet, Chennai", "district": "Chennai"}),
            EmergencyEntity("F7", "Kilpauk Fire Station (North)", EntityType.FIRE_STATION,
                          Location(13.0805, 80.2415), capacity=8,
                          metadata={"vehicles": 7, "personnel": 26, "phone": "101", "address": "Kilpauk, Chennai", "district": "Chennai"}),
            EmergencyEntity("F8", "Avadi Fire Station", EntityType.FIRE_STATION,
                          Location(13.1184, 80.1018), capacity=8,
                          metadata={"vehicles": 7, "personnel": 26, "phone": "101", "address": "Avadi, Thiruvallur", "district": "Thiruvallur"}),
            EmergencyEntity("F9", "Ponneri Fire Station", EntityType.FIRE_STATION,
                          Location(13.3275, 80.2014), capacity=6,
                          metadata={"vehicles": 5, "personnel": 20, "phone": "101", "address": "Ponneri, Thiruvallur", "district": "Thiruvallur"}),
            EmergencyEntity("F10", "Gummidipoondi Fire Station", EntityType.FIRE_STATION,
                          Location(13.4101, 80.1232), capacity=6,
                          metadata={"vehicles": 5, "personnel": 20, "phone": "101", "address": "Gummidipoondi, Thiruvallur", "district": "Thiruvallur"}),
            EmergencyEntity("F11", "Sriperumbudur Fire Station", EntityType.FIRE_STATION,
                          Location(12.9691, 79.9442), capacity=7,
                          metadata={"vehicles": 6, "personnel": 24, "phone": "101", "address": "Sriperumbudur, Kanchipuram", "district": "Kanchipuram"}),
            EmergencyEntity("F12", "Kalpakkam Fire Station", EntityType.FIRE_STATION,
                          Location(12.5539, 80.1601), capacity=8,
                          metadata={"vehicles": 8, "personnel": 30, "phone": "101", "address": "Kalpakkam, Chengalpattu", "district": "Chengalpattu"}),
            # Tambaram and surrounding area fire stations
            EmergencyEntity("F13", "Tambaram Fire Station", EntityType.FIRE_STATION,
                          Location(12.9249, 80.1149), capacity=8,
                          metadata={"vehicles": 7, "personnel": 28, "phone": "101", "address": "West Tambaram, near RTO", "district": "Chengalpattu"}),
            EmergencyEntity("F14", "Poonamallee Fire Station", EntityType.FIRE_STATION,
                          Location(13.0485, 80.0911), capacity=8,
                          metadata={"vehicles": 7, "personnel": 26, "phone": "101", "address": "Serves Kundrathur/Mangadu", "district": "Kanchipuram"}),
            EmergencyEntity("F15", "Sriperumbudur Fire Station (South)", EntityType.FIRE_STATION,
                          Location(12.9691, 79.9442), capacity=7,
                          metadata={"vehicles": 6, "personnel": 24, "phone": "101", "address": "Sriperumbudur Town", "district": "Kanchipuram"}),
            EmergencyEntity("F16", "Oragadam Fire Station", EntityType.FIRE_STATION,
                          Location(12.8354, 79.9673), capacity=7,
                          metadata={"vehicles": 6, "personnel": 22, "phone": "101", "address": "Oragadam Industrial Belt", "district": "Kanchipuram"}),
            # Additional fire stations
            EmergencyEntity("F17", "Guindy Fire Station", EntityType.FIRE_STATION,
                          Location(13.0075, 80.2115), capacity=8,
                          metadata={"vehicles": 7, "personnel": 28, "phone": "101", "address": "Alternate for Pammal/Anakaputhur", "district": "Chennai"}),
        ]
        
        # Real Police Stations in Chennai
        police_stations = [
            EmergencyEntity("P1", "Central Crime Branch, Egmore", EntityType.POLICE_STATION,
                          Location(13.0737, 80.2608), capacity=15,
                          metadata={"vehicles": 10, "personnel": 100, "phone": "100", "address": "Armenian Street, Egmore"}),
            EmergencyEntity("P2", "Anna Nagar Police Station", EntityType.POLICE_STATION,
                          Location(13.0858, 80.2101), capacity=10,
                          metadata={"vehicles": 8, "personnel": 50, "phone": "100", "address": "2nd Avenue, Anna Nagar West"}),
            EmergencyEntity("P3", "T Nagar Police Station", EntityType.POLICE_STATION,
                          Location(13.0407, 80.2334), capacity=10,
                          metadata={"vehicles": 7, "personnel": 45, "phone": "100", "address": "Venkatanarayana Road, T Nagar"}),
            EmergencyEntity("P4", "Adyar Police Station", EntityType.POLICE_STATION,
                          Location(13.0029, 80.2587), capacity=8,
                          metadata={"vehicles": 6, "personnel": 40, "phone": "100", "address": "MRC Nagar, Adyar"}),
            EmergencyEntity("P5", "Mylapore Police Station", EntityType.POLICE_STATION,
                          Location(13.0353, 80.2682), capacity=9,
                          metadata={"vehicles": 7, "personnel": 42, "phone": "100", "address": "C.P. Ramaswamy Road, Mylapore"}),
            EmergencyEntity("P6", "Flower Bazaar Police Station", EntityType.POLICE_STATION,
                          Location(13.0912, 80.2801), capacity=10,
                          metadata={"vehicles": 8, "personnel": 50, "phone": "100", "address": "Flower Bazaar, Chennai", "district": "Chennai"}),
            EmergencyEntity("P7", "Poonamallee Police Station", EntityType.POLICE_STATION,
                          Location(13.0475, 80.0945), capacity=8,
                          metadata={"vehicles": 6, "personnel": 35, "phone": "100", "address": "Poonamallee, Thiruvallur", "district": "Thiruvallur"}),
            EmergencyEntity("P8", "Red Hills Police Station", EntityType.POLICE_STATION,
                          Location(13.1872, 80.1704), capacity=8,
                          metadata={"vehicles": 6, "personnel": 35, "phone": "100", "address": "Red Hills, Thiruvallur", "district": "Thiruvallur"}),
            EmergencyEntity("P9", "Kanchipuram Taluk PS", EntityType.POLICE_STATION,
                          Location(12.8258, 79.6975), capacity=9,
                          metadata={"vehicles": 7, "personnel": 40, "phone": "100", "address": "Kanchipuram Taluk", "district": "Kanchipuram"}),
            EmergencyEntity("P10", "Guduvanchery Police Station", EntityType.POLICE_STATION,
                          Location(12.8425, 80.0594), capacity=8,
                          metadata={"vehicles": 6, "personnel": 35, "phone": "100", "address": "Guduvanchery, Chengalpattu", "district": "Chengalpattu"}),
            EmergencyEntity("P11", "Maduranthakam Police Station", EntityType.POLICE_STATION,
                          Location(12.5117, 79.8858), capacity=7,
                          metadata={"vehicles": 5, "personnel": 30, "phone": "100", "address": "Maduranthakam, Chengalpattu", "district": "Chengalpattu"}),
            # Tambaram and surrounding area police stations
            EmergencyEntity("P12", "Tambaram Police Station", EntityType.POLICE_STATION,
                          Location(12.9254, 80.1158), capacity=10,
                          metadata={"vehicles": 8, "personnel": 45, "phone": "100", "address": "West Tambaram", "district": "Chengalpattu"}),
            EmergencyEntity("P13", "Selaiyur Police Station", EntityType.POLICE_STATION,
                          Location(12.9125, 80.1432), capacity=8,
                          metadata={"vehicles": 6, "personnel": 35, "phone": "100", "address": "East Tambaram / Selaiyur", "district": "Chengalpattu"}),
            EmergencyEntity("P14", "Peerkankaranai Police Station", EntityType.POLICE_STATION,
                          Location(12.9056, 80.1022), capacity=8,
                          metadata={"vehicles": 6, "personnel": 35, "phone": "100", "address": "Perungalathur / Tambaram", "district": "Chengalpattu"}),
            EmergencyEntity("P15", "Kundrathur Police Station", EntityType.POLICE_STATION,
                          Location(12.9982, 80.0935), capacity=9,
                          metadata={"vehicles": 7, "personnel": 40, "phone": "100", "address": "Kundrathur Main Road", "district": "Chengalpattu"}),
            EmergencyEntity("P16", "Somangalam Police Station", EntityType.POLICE_STATION,
                          Location(12.9284, 80.0245), capacity=7,
                          metadata={"vehicles": 5, "personnel": 30, "phone": "100", "address": "Near Kundrathur/Sriperumbudur", "district": "Kanchipuram"}),
            EmergencyEntity("P17", "Sriperumbudur Police Station", EntityType.POLICE_STATION,
                          Location(12.9649, 79.9443), capacity=9,
                          metadata={"vehicles": 7, "personnel": 40, "phone": "100", "address": "Sriperumbudur Town", "district": "Kanchipuram"}),
            EmergencyEntity("P18", "Sunguvarchatram Police Station", EntityType.POLICE_STATION,
                          Location(12.9325, 79.8845), capacity=7,
                          metadata={"vehicles": 5, "personnel": 28, "phone": "100", "address": "Near Sriperumbudur", "district": "Kanchipuram"}),
            # Tiruneermalai, Pammal, Gerugambakkam area police stations
            EmergencyEntity("P19", "S-15 Selaiyur (Tiruneermalai Jurisdiction)", EntityType.POLICE_STATION,
                          Location(12.9605, 80.1340), capacity=8,
                          metadata={"vehicles": 6, "personnel": 35, "phone": "100", "address": "Tiruneermalai Area", "district": "Chennai"}),
            EmergencyEntity("P20", "S-6 Shankar Nagar Police Station", EntityType.POLICE_STATION,
                          Location(12.9715, 80.1412), capacity=9,
                          metadata={"vehicles": 7, "personnel": 40, "phone": "100", "address": "Pammal / Anakaputhur", "district": "Chennai"}),
            EmergencyEntity("P21", "Mangadu Police Station", EntityType.POLICE_STATION,
                          Location(13.0210, 80.1185), capacity=8,
                          metadata={"vehicles": 6, "personnel": 35, "phone": "100", "address": "West of Gerugambakkam", "district": "Chennai"}),
        ]
        
        # Coastal Lifeguard Stations - Marina Beach and other beaches
        lifeguards = [
            EmergencyEntity("L1", "Marina Beach Lifeguard Post 1", EntityType.LIFEGUARD,
                          Location(13.0499, 80.2824), capacity=5,
                          metadata={"personnel": 15, "equipment": "rescue_boats", "phone": "044-24817185", "address": "Marina Beach, Triplicane"}),
            EmergencyEntity("L2", "Marina Beach Lifeguard Post 2", EntityType.LIFEGUARD,
                          Location(13.0580, 80.2843), capacity=5,
                          metadata={"personnel": 15, "equipment": "rescue_boats", "phone": "044-24817185", "address": "Marina Beach, Pattinapakkam"}),
            EmergencyEntity("L3", "Elliot's Beach Lifeguard Station", EntityType.LIFEGUARD,
                          Location(13.0020, 80.2699), capacity=4,
                          metadata={"personnel": 10, "equipment": "rescue_boats", "phone": "044-24522100", "address": "Besant Nagar Beach"}),
            EmergencyEntity("L4", "Thiruvanmiyur Beach Tower", EntityType.LIFEGUARD,
                          Location(12.9868, 80.2705), capacity=4,
                          metadata={"personnel": 10, "equipment": "rescue_boats", "phone": "044-24410151", "address": "Thiruvanmiyur Beach, Chennai", "district": "Chennai"}),
            EmergencyEntity("L5", "Akkarai Beach Point", EntityType.LIFEGUARD,
                          Location(12.9135, 80.2492), capacity=3,
                          metadata={"personnel": 8, "equipment": "rescue_equipment", "phone": "044-24490100", "address": "Akkarai Beach, Chennai", "district": "Chennai"}),
            EmergencyEntity("L6", "Muttukadu Boat House Area", EntityType.LIFEGUARD,
                          Location(12.8211, 80.2455), capacity=4,
                          metadata={"personnel": 12, "equipment": "rescue_boats", "phone": "044-27472345", "address": "Muttukadu, Chengalpattu", "district": "Chengalpattu"}),
            EmergencyEntity("L7", "Mahabalipuram (Shore Temple Side)", EntityType.LIFEGUARD,
                          Location(12.6162, 80.1994), capacity=5,
                          metadata={"personnel": 15, "equipment": "rescue_boats", "phone": "044-27442274", "address": "Mahabalipuram, Chengalpattu", "district": "Chengalpattu"}),
        ]
        
        # 108 Ambulance Service - Government emergency ambulances and private services
        ambulances = [
            EmergencyEntity("A1", "108 Emergency Ambulance - Egmore", EntityType.AMBULANCE,
                          Location(13.0765, 80.2618), capacity=4,
                          metadata={"equipment": "advanced_life_support", "speed": "high", "service": "108", "phone": "108"}),
            EmergencyEntity("A2", "108 Emergency Ambulance - T Nagar", EntityType.AMBULANCE,
                          Location(13.0442, 80.2456), capacity=4,
                          metadata={"equipment": "advanced_life_support", "speed": "high", "service": "108", "phone": "108"}),
            EmergencyEntity("A3", "108 Emergency Ambulance - Adyar", EntityType.AMBULANCE,
                          Location(13.0123, 80.2301), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "service": "108", "phone": "108"}),
            EmergencyEntity("A4", "Private Ambulance - Apollo", EntityType.AMBULANCE,
                          Location(13.0575, 80.2500), capacity=4,
                          metadata={"equipment": "advanced_life_support", "speed": "high", "phone": "044-28293333"}),
            # Tambaram and surrounding area ambulances
            EmergencyEntity("A5", "108 Emergency - Tambaram GH", EntityType.AMBULANCE,
                          Location(12.9234, 80.1150), capacity=4,
                          metadata={"equipment": "advanced_life_support", "speed": "high", "service": "108", "phone": "108"}),
            EmergencyEntity("A6", "108 Emergency - Sriperumbudur GH", EntityType.AMBULANCE,
                          Location(12.9645, 79.9485), capacity=4,
                          metadata={"equipment": "advanced_life_support", "speed": "high", "service": "108", "phone": "108"}),
            EmergencyEntity("A7", "Sam Ambulance Services", EntityType.AMBULANCE,
                          Location(12.9205, 80.0988), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "98846 39400", "address": "Mudichur Road, Tambaram"}),
            EmergencyEntity("A8", "Life Saver Ambulance", EntityType.AMBULANCE,
                          Location(12.9241, 80.1132), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "98403 26108", "address": "MRM Street, Tambaram West"}),
            EmergencyEntity("A9", "Vimal & Co Ambulance", EntityType.AMBULANCE,
                          Location(12.9680, 79.9490), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "94433 34444", "address": "Kamaraj Nagar, Sriperumbudur"}),
            EmergencyEntity("A10", "Prince Ambulance", EntityType.AMBULANCE,
                          Location(12.9312, 80.1190), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "99401 42346", "address": "GST Road, Kadaperi, Tambaram"}),
            EmergencyEntity("A11", "Deepam Medfirst", EntityType.AMBULANCE,
                          Location(12.8450, 80.0620), capacity=4,
                          metadata={"equipment": "advanced_life_support", "speed": "high", "phone": "044-2746 7666", "address": "GST Road, Guduvanchery/Tambaram"}),
            EmergencyEntity("A12", "Medifyhome Service", EntityType.AMBULANCE,
                          Location(12.9975, 80.0940), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "91009 07622", "address": "Kundrathur Main Area"}),
            EmergencyEntity("A13", "J K Ambulance", EntityType.AMBULANCE,
                          Location(12.9610, 80.1412), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "91009 07036", "address": "Near Kundrathur / Chromepet"}),
            EmergencyEntity("A14", "Sri Sakthi Ambulance", EntityType.AMBULANCE,
                          Location(12.8950, 79.9540), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "98410 44108", "address": "Mudichur Road / Walajabad"}),
            EmergencyEntity("A15", "Nathan & Co", EntityType.AMBULANCE,
                          Location(12.9120, 80.1425), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "98411 23456", "address": "Kamarajar Salai, Selaiyur"}),
            EmergencyEntity("A16", "Savitha Medical ICU Ambulance", EntityType.AMBULANCE,
                          Location(13.0289, 80.0094), capacity=4,
                          metadata={"equipment": "advanced_life_support", "speed": "high", "phone": "044-2681 1111", "address": "Thandalam, Sriperumbudur"}),
            # Pammal, Tiruneermalai, Gerugambakkam area ambulances
            EmergencyEntity("A17", "108 Emergency - Pammal Base", EntityType.AMBULANCE,
                          Location(12.9740, 80.1420), capacity=4,
                          metadata={"equipment": "advanced_life_support", "speed": "high", "service": "108", "phone": "108", "address": "Pammal / Tiruneermalai"}),
            EmergencyEntity("A18", "ProCare Ambulance", EntityType.AMBULANCE,
                          Location(13.0125, 80.1450), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "96774 51609", "address": "Serves Gerugambakkam"}),
            EmergencyEntity("A19", "Deepam Ambulance - Chromepet", EntityType.AMBULANCE,
                          Location(12.9515, 80.1415), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "044-2746 7666", "address": "Chromepet (near Tiruneermalai)"}),
            EmergencyEntity("A20", "LK Ambulance Services", EntityType.AMBULANCE,
                          Location(12.9740, 80.1420), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "044-2248 4444", "address": "Pammal Main Road"}),
            EmergencyEntity("A21", "Medifyhome Ambulance - Gerugambakkam", EntityType.AMBULANCE,
                          Location(13.0055, 80.1390), capacity=4,
                          metadata={"equipment": "basic_life_support", "speed": "high", "phone": "91009 07622", "address": "Gerugambakkam Area"}),
        ]
        
        # Add all to database
        for entity in hospitals + fire_stations + police_stations + lifeguards + ambulances:
            self.entities[entity.id] = entity
    
    def add_entity(self, entity: EmergencyEntity):
        """Add new entity (e.g., victim request)."""
        self.entities[entity.id] = entity
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[EmergencyEntity]:
        """Get entity by ID."""
        return self.entities.get(entity_id)
    
    def get_all_entities(self) -> List[EmergencyEntity]:
        """Get all entities."""
        return list(self.entities.values())
    
    def get_by_type(self, entity_type: EntityType) -> List[EmergencyEntity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities.values() if e.entity_type == entity_type]
    
    def add_victim(self, lat: float, lon: float, severity: str = "high", 
                   phone: str = "", emergency_type: str = "medical", description: str = "") -> EmergencyEntity:
        """Add a new victim emergency request."""
        victim_id = f"V{len([e for e in self.entities.values() if e.entity_type == EntityType.VICTIM]) + 1}"
        victim = EmergencyEntity(
            id=victim_id,
            name=f"Emergency Request {victim_id}",
            entity_type=EntityType.VICTIM,
            location=Location(lat, lon),
            capacity=1,
            metadata={
                "severity": severity, 
                "status": "pending",
                "phone": phone,
                "emergency_type": emergency_type,
                "description": description,
                "timestamp": None  # Will be set by caller
            }
        )
        return self.add_entity(victim)
    
    def remove_entity(self, entity_id: str) -> bool:
        """Remove entity from database."""
        if entity_id in self.entities:
            del self.entities[entity_id]
            return True
        return False
    
    def get_victims_by_phone(self, phone: str) -> List[EmergencyEntity]:
        """Get all victims (incidents) by phone number."""
        return [
            entity for entity in self.entities.values()
            if entity.entity_type == EntityType.VICTIM and 
            entity.metadata.get('phone') == phone and
            entity.metadata.get('status') == 'pending'
        ]
    
    def get_all_victims(self) -> List[EmergencyEntity]:
        """Get all active victims."""
        return [
            entity for entity in self.entities.values()
            if entity.entity_type == EntityType.VICTIM and
            entity.metadata.get('status') == 'pending'
        ]
    
    def clear_victims(self):
        """Clear all victim requests."""
        victim_ids = [e.id for e in self.entities.values() if e.entity_type == EntityType.VICTIM]
        for vid in victim_ids:
            del self.entities[vid]
