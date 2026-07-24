from .Helpers import *

import sqlalchemy as sa # For SQL
import sqlalchemy.orm as orm # For object workflow
from sqlalchemy.ext.hybrid import hybrid_property # To add properties

from typing_extensions import Literal, List


Base = orm.declarative_base()

# Table classes (models)
class MaskedCreditCard(Base):
    __tablename__ = "masked_credit_cards"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=True)

    name_on_card: orm.Mapped[str] = orm.mapped_column(nullable=True)
    network: orm.Mapped[str] = orm.mapped_column(nullable=True)
    last_four: orm.Mapped[int]
    exp_month: orm.Mapped[int]
    exp_year: orm.Mapped[int]
    bank_name: orm.Mapped[str] = orm.mapped_column(nullable=True)
    nickname: orm.Mapped[str] = orm.mapped_column(nullable=True)
    card_issuer: orm.Mapped[int]
    virtual_card_enrollment_state: orm.Mapped[int]
    card_art_url: orm.Mapped[str] = orm.mapped_column(nullable=True)
    product_description: orm.Mapped[str] = orm.mapped_column(nullable=True)
    card_issuer_id: orm.Mapped[str] = orm.mapped_column(nullable=True)
    virtual_card_enrollment_type: orm.Mapped[int]
    product_terms_url: orm.Mapped[str] = orm.mapped_column(nullable=True)
    card_info_retrieval_enrollment_state: orm.Mapped[int]
    card_benefit_source: orm.Mapped[int]
    card_creation_source: orm.Mapped[int]

    @hybrid_property
    def exp_date(self) -> dt.date:
        return dt.date(self.exp_year, self.exp_month, 1)

    def __str__(self):
        text_lines = [colored_text(f"• {self.nickname}", color.CYAN) if self.nickname else colored_text("• No nickname", color.RED),
                        colored_text(self.name_on_card, color.LIGHTBLUE_EX),
                        f"Last four: {self.last_four}",
                        f"Expires: {self.exp_date.strftime("%Y-%m")}",
        ]

        if self.network:
            text_lines.extend([f"Network: {self.network}"])

        if self.bank_name:
            text_lines.extend([f"Bank name: {self.bank_name}"])

        if self.card_issuer_id:
            text_lines.extend([f"Card issuer: {self.card_issuer_id}"])

        if self.product_description:
            text_lines.extend([f"Description: {self.product_description}"])

        return "\n".join(text_lines)

class Address(Base):
    __tablename__ = "addresses"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=True)

    use_count: orm.Mapped[int]
    use_date: orm.Mapped[int]
    date_modified: orm.Mapped[int]
    language_code: orm.Mapped[str] = orm.mapped_column(nullable=True)
    label: orm.Mapped[str] = orm.mapped_column(nullable=True)
    initial_creator_id: orm.Mapped[int]
    record_type: orm.Mapped[int]

    @hybrid_property
    def use_date_date(self) -> dt.date:
        return chrome_time_to_datetime(self.use_date).date()

    @hybrid_property
    def date_modified_date(self) -> dt.date:
        return chrome_time_to_datetime(self.date_modified).date()

    def __str__(self):
            text_lines = [colored_text(f"• {self.id}", color.CYAN),
                          f"Use count: {self.use_count}",
                          f"Use date: {self.use_date_date}",
                          f"Modified: {self.date_modified_date}",
                          f"Language code: {self.language_code}"
                          f"Record type: {self.record_type}"
                          ]
    
            return "\n".join(text_lines)

class Autofill(Base):
    __tablename__ = "autofill"
    
    #id: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=True)

    name: orm.Mapped[str] = orm.mapped_column(primary_key=True, unique=False)
    value: orm.Mapped[str] = orm.mapped_column(nullable=True)
    value_lower: orm.Mapped[str] = orm.mapped_column(nullable=True)
    date_created: orm.Mapped[int]
    date_last_used: orm.Mapped[int]
    count: orm.Mapped[int]

    @hybrid_property
    def date_created_date(self) -> dt.date:
        return chrome_time_to_datetime(self.date_created).date()

    @hybrid_property
    def date_last_used_date(self) -> dt.date:
        return chrome_time_to_datetime(self.date_last_used).date()

    def __str__(self):
        text_lines = [colored_text(f"• {self.name}", color.CYAN) if self.name else colored_text("• No name", color.RED),
                      colored_text(self.value, color.LIGHTBLUE_EX),
                      f"Created: {self.date_created_date}",
                      f"Last used: {self.date_last_used_date}",
                      f"Count: {self.count}",
                      ]

        return "\n".join(text_lines)

class AddressTypeToken(Base):
    __tablename__ = "address_type_tokens"
        
    #id: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=True)

    type: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=False)
    value: orm.Mapped[str] = orm.mapped_column(nullable=True)
    verification_status: orm.Mapped[int]
    #observations: orm.Mapped[str]

    def __str__(self):
            text_lines = [colored_text(f"• {self.value}", color.CYAN) if self.value else colored_text("• No value", color.RED),
                          f"Type: {self.type}",
                          f"Verification status: {self.verification_status}",
                          ]
    
            return "\n".join(text_lines)


class WebDataSession(orm.Session):
    @hybrid_property
    def masked_credit_cards(self):
        return self.query(MaskedCreditCard).all()
    
    @hybrid_property
    def addresses(self):
        return self.query(Address).all()
    
    @hybrid_property
    def autofills(self):
        return self.query(Autofill).all()

    @hybrid_property
    def address_type_tokens(self):
        return self.query(AddressTypeToken).all()
    
    def get_recent(self, model_or_query: type | list, order_by = None, limit: int | None = None):
        if order_by is not None:
            order_by = sa.desc(order_by)  # descending

        query = model_or_query if type(model_or_query) == orm.query.Query else self.query(model_or_query)

        return query.order_by(order_by).limit(limit).all()

    def get_recent_masked_credit_cards(self, limit: int | None = None) -> List[MaskedCreditCard]:
            return self.get_recent(MaskedCreditCard, order_by=MaskedCreditCard.id, limit=limit)
    
    def get_recent_autofills(self, limit: int | None = None) -> List[Autofill]:
        return self.get_recent(Autofill, order_by=Autofill.date_last_used, limit=limit)
    
    def get_recent_addresses(self, limit: int | None = None) -> List[Address]:
        return self.get_recent(Address, order_by=Address.use_date, limit=limit)
    
    def get_recent_address_type_tokens(self, limit: int | None = None) -> List[AddressTypeToken]:
        return self.get_recent(AddressTypeToken, order_by=AddressTypeToken.type, limit=limit)


    def search(self, model, columns, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False):
        columns = columns if type(columns) in (list, tuple) else [columns] #visits before fixed

        if mode == "exact":
            filters = [(column if case_sensitive else column.lower()) == (query if case_sensitive else query.lower()) for column in columns]
            return self.query(model).filter(sa.or_(*filters)).all()
            
        words = query.split()

        filters = []
        for word in words:
            term = word if "%" in word else f"%{word}%"
            word_filters = [column.like(term) if case_sensitive else column.ilike(term) for column in columns]
            filters.append(sa.or_(*word_filters))

        if mode == "all":
            return self.query(model).filter(sa.and_(*filters)).all()

        return self.query(model).filter(sa.or_(*filters)).all()
    
    def search_masked_credit_cards(self, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False):
        return self.search(MaskedCreditCard, [MaskedCreditCard.name_on_card, MaskedCreditCard.network, MaskedCreditCard.bank_name, MaskedCreditCard.nickname, MaskedCreditCard.product_description, MaskedCreditCard.card_issuer_id], query, mode, case_sensitive)

    def search_autofills(self, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False):
        return self.search(Autofill, [Autofill.name, Autofill.value], query, mode, case_sensitive)

    def search_address_type_tokens(self, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False):
        return self.search(AddressTypeToken, [AddressTypeToken.value], query, mode, case_sensitive)
    



def create_web_data_session(history_database_path: str, absolute_path: bool = True):
    '''Create a WebDataSession instance using the Web Data database file path'''
    engine = sa.create_engine(f"sqlite://{"/" if absolute_path else ""}{history_database_path}")
    return WebDataSession(engine)

if __name__ == "__main__":
    wds = create_web_data_session("Web Data")

    print(*wds.masked_credit_cards, sep="\n\n")

    print(*wds.autofills, sep="\n\n")

    print(*wds.address_type_tokens, sep="\n\n")


