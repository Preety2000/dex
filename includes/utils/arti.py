from typing import Optional

from bs4 import BeautifulSoup
from sqlalchemy import func, select

from includes.core.config import app_context
from includes.database.connection import active_secondary_db
from includes.database.dataclass.dataclass import _Article, _Terms
from includes.database.models.secondary import Article, ArticleMetadata, Trending
from includes.metrics import MetricsManager
from includes.schemas.cache.subject import SubjectCache
from includes.schemas.cache.suggestion import SuggestionCache
from includes.schemas.cache.terms import TermsCache

articalNotFondmessage = "<h2>Error: Can't read file, or Article cannot be opened</h2><p>It looks like you’re dealing with an error message indicating that a file can't be read or an article cannot be opened. Here are a few potential reasons for this issue and ways to troubleshoot:</p><ol><li><p><strong>File Path Issues</strong>:</p><ul><li><strong>Check File Path</strong>: Ensure that the file path you’re using is correct. Verify that the file exists at the specified location.</li><li><strong>Relative vs. Absolute Paths</strong>: If you’re using a relative path, try using an absolute path to avoid ambiguity.</li></ul></li><li><p><strong>File Permissions</strong>:</p><ul><li><strong>Permissions</strong>: Ensure that you have the necessary permissions to access the file. You might need to adjust the file permissions or run your application with higher privileges.</li></ul></li><li><p><strong>File Corruption</strong>:</p><ul><li><strong>Check File Integrity</strong>: The file might be corrupted or damaged. Try opening it with a different application or tool to see if it works.</li></ul></li><li><p><strong>File Format</strong>:</p><ul><li><strong>Supported Formats</strong>: Verify that the file format is supported by your application. If not, you might need to convert the file to a compatible format.</li></ul></li><li><p><strong>Application Errors</strong>:</p><ul><li><strong>Error Handling</strong>: Make sure that your application has proper error handling to deal with file-related issues gracefully.</li><li><strong>Logs and Debugging</strong>: Check application logs or debug output for more specific error messages.</li></ul></li></ol>"
articalNotFondmessage = "<h2>त्रुटि: फ़ाइल नहीं पढ़ी जा सकती, या लेख नहीं खोला जा सकता</h2><p>ऐसा लगता है कि आप एक त्रुटि संदेश से निपट रहे हैं जो यह दर्शाता है कि फ़ाइल पढ़ी नहीं जा सकती या लेख नहीं खोला जा सकता। इस समस्या के कुछ संभावित कारण और समस्या निवारण के तरीके यहां दिए गए हैं:</p><ol><li><p><strong>फ़ाइल पथ समस्याएँ</strong>:</p><ul><li><strong>फ़ाइल पथ जाँचें</strong>: सुनिश्चित करें कि आप जिस फ़ाइल पथ का उपयोग कर रहे हैं वह सही है। सत्यापित करें कि फ़ाइल निर्दिष्ट स्थान पर मौजूद है।</li><li><strong>सापेक्ष बनाम निरपेक्ष पथ</strong>: यदि आप सापेक्ष पथ का उपयोग कर रहे हैं, तो अस्पष्टता से बचने के लिए निरपेक्ष पथ का उपयोग करने का प्रयास करें।</li></ul></li><li><p><strong>फ़ाइल अनुमतियाँ</strong>:</p><ul><li><strong>अनुमतिएँ</strong>: सुनिश्चित करें कि आपके पास फ़ाइल तक पहुँचने के लिए आवश्यक अनुमतियाँ हैं। आपको फ़ाइल अनुमतियों को समायोजित करने या अपने एप्लिकेशन को उच्च विशेषाधिकारों के साथ चलाने की आवश्यकता हो सकती है।</li></ul></li><li><p><strong>फ़ाइल भ्रष्टाचार</strong>:</p><ul><li><strong>फ़ाइल अखंडता की जाँच करें</strong>: फ़ाइल दूषित या क्षतिग्रस्त हो सकती है। यह देखने के लिए कि क्या यह काम करता है, इसे किसी अन्य एप्लिकेशन या टूल के साथ खोलने का प्रयास करें।</li></ul></li><li><p><strong>फ़ाइल प्रारूप</strong>:</p><ul><li><strong>समर्थित प्रारूप</strong>: सत्यापित करें कि फ़ाइल प्रारूप आपके एप्लिकेशन द्वारा समर्थित है। यदि नहीं, तो आपको फ़ाइल को संगत प्रारूप में परिवर्तित करने की आवश्यकता हो सकती है।</li></ul></li><li><p><strong>एप्लिकेशन त्रुटियाँ</strong>:</p><ul><li><strong>त्रुटि प्रबंधन</strong>: सुनिश्चित करें कि फ़ाइल-संबंधी समस्याओं से निपटने के लिए आपके एप्लिकेशन में उचित त्रुटि प्रबंधन है।</li><li><strong>लॉग और डिबगिंग</strong>: अधिक विशिष्ट त्रुटि संदेशों के लिए एप्लिकेशन लॉग या डिबग आउटपुट की जाँच करें।</li></ul></li></ol>"


def get_excerpt(article, max_length=180):
    content = article.content.replace(
        "{{appname}}", app_context.config.get("site_name", "")
    ).replace("{{appmail}}", app_context.config.get("app_mail", ""))
    text = BeautifulSoup(content, "html.parser").get_text(" ", strip=True)

    if not text:
        return ""

    first, *rest = [p.strip() for p in text.split("।") if p.strip()]

    if len(first) < max_length and rest:
        return f"{first}। {rest[0]}।"

    return f"{first}।"


async def get_artical_url(article: _Article) -> str:
    if isinstance(article.parameter, int):
        article.parameter = await TermsCache.get_by_id(article.parameter)

    article.url = f"{app_context.request.host_url}{(
        f"{article.parameter.slug}/{article.slug}" 
        if isinstance(article.parameter, _Terms) and article.parameter.slug
        else article.slug
    )}"
    return article.url


async def enrich_article(article: _Article, *, suggestion=False, excerpt=False) -> _Article:
    db = await active_secondary_db()
    metadata_stmt = select(ArticleMetadata).where(ArticleMetadata.id == article.id)
    mdata = db.execute(metadata_stmt).scalars().first()
    
    if mdata is None:
        mdata = {
            "secret_key": None,
            "tags_group": [],
            "subject_id": None,
            "excerpt": None,
        }
    else:
        mdata = {field: getattr(mdata, field) for field in mdata.__table__.columns.keys()}
        
        

    article.secret_key = mdata["secret_key"]
    article.subject = await SubjectCache.get_by_id(mdata["subject_id"])

    if suggestion:
        tags = [int(tag_id) for tag_id in mdata["tags_group"] if tag_id]
        article.suggestion = [
            {"tag": s.tags, "used": s.most_used}
            for s in await SuggestionCache.get_many(tags)
        ]

    if excerpt:
        article.excerpt = mdata["excerpt"] or get_excerpt(article)

    return article


async def get_mini_article_json(
    article: Optional[Article | _Article] = None,
    *,
    trending=None,
    excerpt=None,
    suggestion=None,
    category=None,
    like=None,
) -> Optional[dict]:

    if article is None:
        return None

    if isinstance(article, Article):
        article = await article.to_dataclass(
            category=category,
            like=like,
        )
        
    if article is None:
        return {}

    await get_artical_url(article)
    await enrich_article(article, excerpt=excerpt, suggestion=suggestion)

    response = {
        "id": article.id,
        "url": article.url,
        "title": article.title,
        "subject": article.subject,
        "excerpt": article.excerpt,
        "category": article.category,
        "views": await MetricsManager.get_article_view(article.id),
        "date": article.date,
    }

    if trending:
        counts = (
            app_context.secondary_session.query(
                Trending.question.label("id"), func.count().label("cnt")
            )
            .group_by(Trending.question)
            .subquery()
        )
        ranked = app_context.secondary_session.query(
            counts.c.id,
            func.dense_rank().over(order_by=counts.c.cnt.desc()).label("rank"),
        ).subquery()
        response["rank"] = (
            app_context.secondary_session.query(ranked.c.rank)
            .filter(ranked.c.id == article.id)
            .scalar()
        )

    return response

