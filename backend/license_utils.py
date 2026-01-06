from sqlalchemy.orm import Session
from backend.models import License

def check_license(db: Session) -> bool:
    """
    Checks if a valid, active license exists in the DB.
    """
    active_license = db.query(License).filter(License.is_active == True).first()
    return active_license is not None
