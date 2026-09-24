from app.models import Complaint
from app.providers.triage.rules import RuleBasedTriage
from app.repositories.complaints import ComplaintRepository

SEED_COMPLAINTS = [
    ("Water pipe burst near masjid, gali is flooding since fajr.", "Street 12, Gulshan"),
    ("Pani ka pressure bilkul low hai in our block since yesterday.", "Sector C, Model Town"),
    ("Sewer water is coming outside and bad smell near school.", "Lane 4, Nazimabad"),
    ("Transformer is making sparks, please send team urgent.", "Main Market, DHA"),
    ("Bijli is gone in whole street after rain, children are scared.", "Block 7, North Karachi"),
    ("Loose electric wire hanging close to gate, very dangerous.", "House 23 Road 8, PECHS"),
    ("Garbage has not been collected for four days, kooda piling up.", "Mohalla Rehmanpura"),
    ("Street cleaning needed, waste and flies are everywhere.", "UC 6, Orangi"),
    ("Dustbin is broken and people throw trash on road.", "Near Railway Station"),
    ("Big pothole outside hospital, ambulance got stuck today.", "Civil Hospital Road"),
    ("Road carpet is broken after rain, bikes slipping daily.", "Korangi Crossing"),
    ("Footpath is damaged, elderly cannot walk safely.", "Clifton Block 2"),
    ("Street light is not working and road becomes very dark.", "Park Road, F-10"),
    ("Three lamp posts off near bus stop since last week.", "University Road"),
    ("Light pole wire is exposed, please repair quickly.", "Garden East"),
    ("Stray dogs are creating issue near our houses every night.", "Shadman Colony"),
    ("Illegal dumping truck comes at night, kindly check.", "Industrial Area Gate 3"),
    ("Park swing is broken, small children can get hurt.", "Iqbal Park"),
    ("Water leakage under road wasting pani for many hours.", "Block A, Faisal Town"),
    ("Drain is blocked and rain water stays outside homes.", "Gulberg Lane 9"),
    ("Electric pole fell slightly after storm, urgent inspection needed.", "Scheme 33 Road"),
    ("Power fluctuations are damaging fans in our street.", "Satellite Town"),
    ("Garbage smell near bakery is very bad, sweep please.", "Liaquatabad No 10"),
    ("Open waste drain needs cleaning before Friday prayers.", "Saddar Bazaar"),
    ("Road has many small potholes, repair when possible.", "Canal View Road"),
    ("Speed breaker paint faded and road signs are missing.", "Airport Link Road"),
    ("Street lamp outside girls college is off since Eid.", "College Road"),
    ("Dark lane needs a streetlight for safety at night.", "Basti Aman"),
    ("Public park water tap is leaking all day.", "Jinnah Garden"),
    ("Broken manhole cover is dangerous for cars and bikes.", "Old City Chowk"),
]

class SeedService:
    def __init__(self, repository: ComplaintRepository): self.repository = repository
    def run(self) -> int:
        rules, added = RuleBasedTriage(), 0
        for text, location in SEED_COMPLAINTS:
            if self.repository.exists_by_text_and_location(text, location): continue
            result = rules.triage(text, location)
            self.repository.create(Complaint(text=text, location=location, category=result.category, priority=result.priority, ai_summary=result.summary, triaged_by="rules", triage_latency_ms=0))
            added += 1
        return added
