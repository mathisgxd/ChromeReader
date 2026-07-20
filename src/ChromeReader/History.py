from .Helpers import *

import sqlalchemy as sa # For SQL
import sqlalchemy.orm as orm # For object workflow
from sqlalchemy.ext.hybrid import hybrid_property # To add properties

from typing_extensions import Literal, List


Base = orm.declarative_base()

# Table classes (models)
class Url(Base):
    __tablename__ = "urls"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=True)
    url: orm.Mapped[str]
    title: orm.Mapped[str]
    visit_count: orm.Mapped[int]
    typed_count: orm.Mapped[int]
    last_visit_time: orm.Mapped[int]
    hidden: orm.Mapped[int]

    visits: orm.Mapped[List["Visit"]] = orm.relationship(back_populates="url_entry", order_by=lambda: Visit.visit_time.desc())

    @hybrid_property
    def last_visit_datetime(self) -> dt.datetime | None:
        return chrome_time_to_datetime(self.last_visit_time)

    def __str__(self) -> str:
        text_lines = [colored_text(f"• {self.title}", color.CYAN) if self.title else colored_text(f"• No title", color.RED),
                      colored_text(self.url, color.LIGHTBLUE_EX),
                      f"Visited {self.visit_count} time{"s" if self.visit_count > 1 else ""}",
                      f"Visits: {colored_text(", ", color.LIGHTBLACK_EX).join([str(visit.visit_datetime) for visit in self.visits])}" if self.visits else f"Last visit time: {self.last_visit_datetime}"
                      ]
        
        return "\n".join(text_lines)

class Visit(Base):
    __tablename__ = "visits"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=True)
    url: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("urls.id"))
    visit_time: orm.Mapped[int]
    from_visit: orm.Mapped[int]
    external_referrer_url: orm.Mapped[str]
    transition: orm.Mapped[int]
    segment_id: orm.Mapped[int]
    visit_duration: orm.Mapped[int]
    incremented_omnibox_typed_score: orm.Mapped[int]
    opener_visit: orm.Mapped[int]
    originator_visit_id: orm.Mapped[int]
    originator_from_visit: orm.Mapped[int]
    originator_opener_visit: orm.Mapped[int]
    is_known_to_sync: orm.Mapped[int]
    consider_for_ntp_most_visited: orm.Mapped[int]
    visited_link_id: orm.Mapped[int]
    app_id: orm.Mapped[str]

    url_entry: orm.Mapped["Url"] = orm.relationship(back_populates="visits")

    @hybrid_property
    def visit_datetime(self) -> dt.datetime | None:
        return chrome_time_to_datetime(self.visit_time)
    
    @hybrid_property
    def visit_duration_timedelta(self) -> dt.timedelta | None:
        return chrome_time_to_timedelta(self.visit_duration)

    def __str__(self):
        text_lines = [colored_text(f"• {self.url_entry.title}", color.CYAN) if self.url_entry.title else colored_text(f"• No title", color.RED),
                      colored_text(self.url_entry.url, color.LIGHTBLUE_EX),
                      f"Visit time: {self.visit_datetime}"]
        
        if self.visit_duration_timedelta:
            text_lines.extend([f"Duration: {self.visit_duration_timedelta}"])
        
        return "\n".join(text_lines)
    
class Download(Base):
    __tablename__ = "downloads"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, unique=True)
    guid: orm.Mapped[str]
    current_path: orm.Mapped[str]
    target_path: orm.Mapped[str]
    start_time: orm.Mapped[int]
    received_bytes: orm.Mapped[int]
    total_bytes: orm.Mapped[int]
    state: orm.Mapped[int]
    danger_type: orm.Mapped[int]
    interrupt_reason: orm.Mapped[int]
    hash: orm.Mapped[str]
    end_time: orm.Mapped[int]
    opened: orm.Mapped[int]
    last_access_time: orm.Mapped[int]
    transient: orm.Mapped[int]
    referrer: orm.Mapped[str]
    site_url: orm.Mapped[str]
    embedder_download_data: orm.Mapped[bytes]
    tab_url: orm.Mapped[str]
    tab_referrer_url: orm.Mapped[str]
    http_method: orm.Mapped[str]
    by_ext_id: orm.Mapped[str]
    by_ext_name: orm.Mapped[str]
    by_web_app_id: orm.Mapped[str]
    etag: orm.Mapped[str]
    last_modified: orm.Mapped[str]
    mime_type: orm.Mapped[str]
    original_mime_type: orm.Mapped[str]

    @hybrid_property
    def start_datetime(self) -> dt.datetime | None:
        return chrome_time_to_datetime(self.start_time)
    
    @hybrid_property
    def end_datetime(self) -> dt.datetime | None:
        return chrome_time_to_datetime(self.end_time)
    
    @hybrid_property
    def elapsed_timedelta(self) -> dt.timedelta | None:
        if (not self.start_datetime) or (not self.end_datetime):
            return None
        
        return self.end_datetime - self.start_datetime
    
    @hybrid_property
    def last_access_datetime(self) -> dt.datetime | None:
        return chrome_time_to_datetime(self.last_access_time)
    
    @hybrid_property
    def file_name(self) -> str | None:
        if not self.target_path:
            return None
        
        fn = self.target_path.split("\\")[-1]
        if not fn:
            return None
        
        return fn
    
    def __str__(self):
        text_lines = [colored_text(f"• {self.file_name}", color.CYAN) if self.file_name else colored_text("• No file name", color.RED),
                      colored_text(self.tab_url, color.LIGHTBLUE_EX),
                      f"Type: {self.mime_type}",
                      f"Path: {self.target_path}",
                      ]
        
        if self.last_access_datetime:
            text_lines.extend([f"Last accessed at {self.last_access_datetime}"])
            
        text_lines.extend([f"Started {self.start_datetime}" if self.start_datetime else colored_text("No start time", color.RED),
                           f"It took {self.elapsed_timedelta}" if self.elapsed_timedelta else colored_text("No elapsed time", color.RED),
                           f"Ended {self.end_datetime}" if self.end_datetime else colored_text("No end time", color.RED)])
            
        
        return "\n".join(text_lines)

class HistorySession(orm.Session):
    @hybrid_property
    def urls(self):
        return self.query(Url).all()
    
    @hybrid_property
    def visits(self):
        return self.query(Visit).all()
    
    @hybrid_property
    def downloads(self):
        return self.query(Download).all()
    
    def get_recent(self, model_or_query: type | list, order_by = None, limit: int | None = None):
        if order_by is not None:
            order_by = sa.desc(order_by)  # descending

        query = model_or_query if type(model_or_query) == orm.query.Query else self.query(model_or_query)

        return query.order_by(order_by).limit(limit).all()
    
    def get_recent_visits(self, limit: int | None = None) -> List[Visit]:
        return self.get_recent(Visit, order_by=Visit.visit_time, limit=limit)
    
    def get_recent_urls(self, limit: int | None = None) -> List[Url]:
        return self.get_recent(Url, order_by=Url.last_visit_time, limit=limit)
    
    def get_recent_downloads(self, limit: int | None = None) -> List[Download]:
        return self.get_recent(Download, order_by=Download.end_time, limit=limit)
    

    def get_urls_visits(self, urls: list[Url] | Url) -> List[Visit]:
        url_ids = [url.id for url in urls] if type(urls) == list else [urls.id]
        visits = self.query(Visit).filter(Visit.url.in_(url_ids)).all()
        return visits
    

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
    
    def search_urls(self, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False):
        return self.search(Url, [Url.title, Url.url], query, mode, case_sensitive)

    def search_visits(self, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False):
        urls = self.search_urls(query, mode, case_sensitive)
        visits = self.get_urls_visits(urls)

        return visits

    def search_downloads(self, query: str, mode: Literal["any", "all", "exact"] = "any", case_sensitive: bool = False):
        return self.search(Download, [Download.target_path, Download.tab_url], query, mode, case_sensitive)
    



def create_history_session(history_database_path: str, absolute_path: bool = True):
    '''Create a HistorySession instance using the History database file path'''
    engine = sa.create_engine(f"sqlite://{"/" if absolute_path else ""}{history_database_path}")
    return HistorySession(engine)

if __name__ == "__main__":
    session = create_history_session("History", absolute_path=True)

    test = "recents"

    match test:
        case "recents":

            print(colored_text("\n10 MOST RECENT URLS\n", color.GREEN))

            print(*session.get_recent_urls(10), sep="\n\n")

            print(colored_text("\n10 MOST RECENT VISITS\n", color.GREEN))

            print(*session.get_recent_visits(10), sep="\n\n")

            print(colored_text("\n10 MOST RECENT DOWNLOADS\n", color.GREEN))

            print(*session.get_recent_downloads(10), sep="\n\n")
        
        case "order":
            downloads = session.get_recent_downloads()
            print(f"First download: {downloads[0]}\n")
            print(f"Last download: {downloads[-1]}\n")

            most_recent_download = session.get_recent_downloads(1)[0]
            print(f"Most recent download: {most_recent_download}")

        case "query":
            results = session.query_urls(title=["icon", "symbol"], url=["icon", "symbol"], filter=True, limit=5)
            print(colored_text(f"\nURLs THAT HAVE ('icon' OR 'symbol' IN TITLE) AND ('icon' OR 'symbol' IN URL)\n{len(results)} RESULTS FOUND:\n", color.GREEN))
            print(*results, sep="\n\n")

            visits = session.get_urls_visits(results)
            print(colored_text(f"\nCORRESPONDING VISITS\n{len(visits)} RESULTS FOUND:\n", color.GREEN))
            print(*visits, sep="\n\n")

