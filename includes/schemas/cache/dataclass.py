from dataclasses import dataclass, field


@dataclass
class _ArticleCache:
    ById: dict = field(default_factory=dict)
    BySlug: dict = field(default_factory=dict)


@dataclass
class QuizQuesCache:
    ById: dict = field(default_factory=dict)
    ByTermId: dict = field(default_factory=dict)


@dataclass
class _SubjectCache:
    ById: dict = field(default_factory=dict)
    BySlug: dict = field(default_factory=dict)
    ByName: dict = field(default_factory=dict)


@dataclass
class _TermsCache:
    allList: dict = None
    ById: dict = field(default_factory=dict)
    BySlug: dict = field(default_factory=dict)
    ByName: dict = field(default_factory=dict)
    subject_id: dict = field(default_factory=dict)


@dataclass
class _SuggestionCache:
    allList: dict = None
    ById: dict = field(default_factory=dict)
    BySlug: dict = field(default_factory=dict)
    ByName: dict = field(default_factory=dict)


@dataclass
class _MemberCache:
    ById: dict = field(default_factory=dict)
    ByEmail: dict = field(default_factory=dict)
    BySecret: dict = field(default_factory=dict)
