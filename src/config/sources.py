"""Configuration of news sources to be parsed"""

SOURCES_CONFIG = [
    {
        'url': 'https://riamo.ru/category/proisshestviya/',
        'source_name': 'RIAMO',
        'entries_selector': 'article._1i8pq983',
        'has_pagination': True,
        'pagination_selector': 'a[href*="?page="]',
        'title_selector': 'h1.dx3d6b0',
        'date_selector': 'time.xtn0kl0',
        'content_selector': 'main p',
        'js_rendered': True,
        'pagination_direct_url': '?page={}'
    },
    {
        'url': 'https://78.ru/news/proisshestviya',
        'source_name': '78.ru',
        'entries_selector': 'a.news-feed-timeline-item_item__hFnM1',
        'has_pagination': False,
        'title_selector': 'h1.heading',
        'date_selector': '.author-and-date_containerDate__EJTrp',
        'content_selector': 'div.publication__body',
        'js_rendered': True,
        'base_url': 'https://78.ru/news/'
    },
    {
        'url': 'https://pravda-nn.ru/incidents/',
        'source_name': 'pravda-nn',
        'entries_selector': 'div.category-article',
        'has_pagination': True,
        'title_selector': 'h1.h1',
        'date_selector': 'time.date',
        'content_selector': 'div.wpb_wrapper',
        'js_rendered': True,
        'base_url': 'https://pravda-nn.ru/news/',
        'pagination_type': 'load_more',
        'pagination_selector': 'div.ias-trigger'
    },
    {
        'url': 'https://pobeda26.ru/news/proisshestviya',
        'source_name': 'pobeda26.ru',
        'entries_selector': 'div.Matter_matter__fH5cY',
        'has_pagination': False,
        'title_selector': 'h1.leading-none',
        'date_selector': 'div.absolute',
        'content_selector': 'div.Common_common__MfItd',
        'js_rendered': True
    }
]