from .Helpers import *

import sqlalchemy as sa # For SQL
import sqlalchemy.orm as orm # For object workflow
from sqlalchemy.ext.hybrid import hybrid_property # To add properties

from typing_extensions import Literal, List


Base = orm.declarative_base()

# Table classes (models)
class Login(Base):
    __tablename__ = "logins"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=True)

    origin_url: orm.Mapped[str]
    action_url: orm.Mapped[str]

    username_element: orm.Mapped[str]
    username_value: orm.Mapped[str]

    password_element: orm.Mapped[str]
    password_value: orm.Mapped[bytes]

    signon_realm: orm.Mapped[str]
    date_created: orm.Mapped[int]
    blacklisted_by_user: orm.Mapped[int]
    scheme: orm.Mapped[int]
    password_type: orm.Mapped[int]
    times_used: orm.Mapped[int]
    form_data: orm.Mapped[bytes]
    display_name: orm.Mapped[str]
    icon_url: orm.Mapped[str]
    federation_url: orm.Mapped[str]
    skip_zero_click: orm.Mapped[int]
    generation_upload_status: orm.Mapped[int]
    possible_username_pairs: orm.Mapped[bytes]
    date_last_used: orm.Mapped[int]
    moving_blocked_for: orm.Mapped[bytes]
    date_password_modified: orm.Mapped[int]
    sender_email: orm.Mapped[str]
    sender_name: orm.Mapped[str]
    date_received: orm.Mapped[int]
    sharing_notification_displayed: orm.Mapped[int]
    keychain_identifier: orm.Mapped[bytes]
    sender_profile_image_url: orm.Mapped[str]
    #date_last_filled: orm.Mapped[int]

    @hybrid_property
    def date_created_datetime(self) -> dt.datetime | None:
        return chrome_time_to_datetime(self.date_created)
    
    @hybrid_property
    def date_last_used_datetime(self) -> dt.datetime | None:
        return chrome_time_to_datetime(self.date_last_used)
    
    @hybrid_property
    def date_password_modified_datetime(self) -> dt.datetime | None:
        return chrome_time_to_datetime(self.date_password_modified) if self.date_password_modified != self.date_created else None
    
    @hybrid_property
    def date_received_datetime(self) -> dt.datetime | None:
        return chrome_time_to_datetime(self.date_received)
    
    """ @hybrid_property
    def date_last_filled_datetime(self) -> dt.datetime:
        return chrome_time_to_datetime(self.date_last_filled) """
    
    def __str__(self):
        text_lines = [colored_text(f"• {self.origin_url}", color.GREEN),
                      f"Username: {self.username_value}",
                      f"Password: {self.password_value}",
                      f"Created {self.date_created_datetime}"]
        if self.date_password_modified_datetime:
            text_lines.append(f"Password Modified {self.date_password_modified_datetime}")
        text_lines.append(f"Used {self.times_used} times")
        if self.date_last_used_datetime:
            text_lines.append(f"Last used {self.date_last_used_datetime}")
        """ if self.date_last_filled_datetime:
            text_lines.append(f"Last filled {self.date_last_used_datetime}") """

        return "\n".join(text_lines)
    

class LoginDataSession(orm.Session):
    @hybrid_property
    def logins(self):
        return self.query(Login).all()

    def search(self, model, columns, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False):
        columns = columns if type(columns) in (list, tuple) else [columns]

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
    
    def search_logins(self, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False):
        return self.search(Login, [Login.origin_url, Login.action_url, Login.federation_url, Login.icon_url, Login.username_value], query, mode, case_sensitive)
    
    
def create_login_data_session(login_data_database_path: str, absolute_path: bool = True):
    '''Create a LoginDataSession instance'''
    engine = sa.create_engine(f"sqlite://{"/" if absolute_path else ""}{login_data_database_path}")
    return LoginDataSession(engine)

if __name__ == "__main__":
    session = create_login_data_session("Login Data", absolute_path=True)

    print(*session.logins, sep="\n\n")