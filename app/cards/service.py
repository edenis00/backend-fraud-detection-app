from sqlalchemy.orm import Session
from app.cards.models import Card
from app.cards.schemas import CardCreate, CardUpdate


class CardService:
    """Service layer for card operations."""

    @staticmethod
    def create_card(db: Session, card: CardCreate) -> Card:
        """Create a new card."""
        db_card = Card(
            card_reference=card.card_reference,
            masked_card_number=card.masked_card_number,
            department_id=card.department_id,
            assigned_user_id=card.assigned_user_id,
            card_type=card.card_type,
            issue_date=card.issue_date,
            expiry_date=card.expiry_date,
            status=card.status,
        )
        db.add(db_card)
        db.commit()
        db.refresh(db_card)
        return db_card

    @staticmethod
    def get_card(db: Session, card_id: int) -> Card | None:
        """Get card by ID."""
        return db.query(Card).filter(Card.id == card_id).first()

    @staticmethod
    def get_card_by_reference(db: Session, reference: str) -> Card | None:
        """Get card by card reference."""
        return db.query(Card).filter(Card.card_reference == reference).first()

    @staticmethod
    def get_cards_by_department(db: Session, dept_id: int) -> list[Card]:
        """Get all cards in a department."""
        return db.query(Card).filter(Card.department_id == dept_id).all()

    @staticmethod
    def get_cards_by_user(db: Session, user_id: int) -> list[Card]:
        """Get all cards assigned to a user."""
        return db.query(Card).filter(Card.assigned_user_id == user_id).all()

    @staticmethod
    def list_cards(db: Session, skip: int = 0, limit: int = 100) -> list[Card]:
        """List all cards."""
        return db.query(Card).offset(skip).limit(limit).all()

    @staticmethod
    def update_card(db: Session, card_id: int, card_update: CardUpdate) -> Card | None:
        """Update a card."""
        db_card = db.query(Card).filter(Card.id == card_id).first()
        if not db_card:
            return None
        
        update_data = card_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_card, key, value)
        
        db.commit()
        db.refresh(db_card)
        return db_card

    @staticmethod
    def delete_card(db: Session, card_id: int) -> bool:
        """Delete a card."""
        db_card = db.query(Card).filter(Card.id == card_id).first()
        if not db_card:
            return False
        
        db.delete(db_card)
        db.commit()
        return True
