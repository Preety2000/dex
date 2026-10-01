from dataclasses import dataclass

from includes.schemas.book import ClassBooks
from includes.schemas.terms import ClassTerms
from includes.schemas.subject import ClassSubject
from includes.schemas.syllabus import ClassSyllabus
from includes.schemas.download import ClassDownload
from includes.schemas.articles import ArticleService
from includes.schemas.objective import ClassObjective
from includes.schemas.suggestion import ClassSuggestion
from includes.schemas.university import ClassUniversity
from includes.services.member.member import ClassUser


@dataclass
class CLS:
    ClassBooks: ClassBooks
    ClassSubject: ClassSubject
    ClassSuggestion: ClassSuggestion
    ClassSyllabus: ClassSyllabus
    ClassTerms: ClassTerms
    ClassUniversity: ClassUniversity
    ClassUser: ClassUser
    ArticleService: ArticleService
    ClassDownload: ClassDownload
    ClassObjective: ClassObjective
