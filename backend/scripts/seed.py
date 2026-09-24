from app.db import make_session_factory
from app.repositories.complaints import ComplaintRepository
from app.services.seed import SeedService

if __name__ == "__main__":
    added = SeedService(ComplaintRepository(make_session_factory())).run()
    print(f"Seed complete: {added} complaint(s) added")
