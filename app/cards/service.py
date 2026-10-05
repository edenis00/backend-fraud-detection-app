import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cards.models import Card
from app.cards.schemas import CardCreate, CardUpdate


class CardService:
    """Service layer for card operations."""

    @staticmethod
    def create_card(db: Session, card: CardCreate) -> Card:
        while True:
            card_reference = f"CARD-{secrets.token_hex(6).upper()}"
            exists = db.scalar(
                select(Card.id).where(Card.card_reference == card_reference)
            )
            if exists is None:
                break

        db_card = Card(
            card_reference=card_reference,
            masked_card_number=f"**** **** **** {card.last_four}",
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
        return db.query(Card).filter(Card.id == card_id).first()

    @staticmethod
    def get_card_by_reference(db: Session, reference: str) -> Card | None:
        return db.query(Card).filter(Card.card_reference == reference).first()

    @staticmethod
    def get_cards_by_department(db: Session, dept_id: int) -> list[Card]:
        return db.query(Card).filter(Card.department_id == dept_id).all()

    @staticmethod
    def get_cards_by_user(db: Session, user_id: int) -> list[Card]:
        return db.query(Card).filter(Card.assigned_user_id == user_id).all()

    @staticmethod
    def list_cards(db: Session, skip: int = 0, limit: int = 100) -> list[Card]:
        return db.query(Card).offset(skip).limit(limit).all()

    @staticmethod
    def update_card(
        db: Session,
        card_id: int,
        card_update: CardUpdate,
    ) -> Card | None:
        db_card = db.query(Card).filter(Card.id == card_id).first()
        if db_card is None:
            return None

        update_data = card_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_card, key, value)

        db.commit()
        db.refresh(db_card)
        return db_card

    @staticmethod
    def delete_card(db: Session, card_id: int) -> bool:
        db_card = db.query(Card).filter(Card.id == card_id).first()
        if db_card is None:
            return False

        db.delete(db_card)
        db.commit()
        return True