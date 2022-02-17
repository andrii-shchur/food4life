import json
import requests
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me
from threading import Thread


def main():
    ls = []
    for pnum in range(1, 207):
        rcls = []
        thrls = []
        page = 'https://www.acouplecooks.com/category/recipes/?_paged={}'.format(pnum)
        req = requests.get(page)
        bs4 = BeautifulSoup(req.text, 'lxml')
        recipe_urls = bs4.findAll('h2', {'class': 'post-summary__title'})
        print(pnum)

        def sf(url):
            dt = scrape_me(url)
            dc = {
                'total_time': None,
                'title': None,
                'yields': None,
                'ingredients': None,
                'instructions': None,
                'image': None,
                'host': None,
                'links': None,
                'nutrients': None,
                'categories': [],
                'recommendations': [],
                'tags': []
            }

            try:
                dc['total_time'] = dt.total_time()
            except Exception:
                pass
            try:
                dc['title'] = dt.title()
            except Exception:
                pass
            try:
                dc['yields'] = dt.yields()
            except Exception:
                pass
            try:
                dc['ingredients'] = dt.ingredients()
            except Exception:
                pass
            try:
                dc['instructions'] = dt.instructions()
            except Exception:
                pass
            try:
                dc['image'] = dt.image()
            except Exception:
                pass
            try:
                dc['host'] = dt.host()
            except Exception:
                pass
            try:
                dc['links'] = dt.links()
            except Exception:
                pass
            try:
                dc['nutrients'] = dt.nutrients()
            except Exception:
                pass
            categories = dt.soup.find('ul', {'class': 'post-categories'})
            if categories:
                for category in categories.find_all('a'):
                    dc['categories'].append(category.text)

            tags = dt.soup.find('ul', {'class': 'post-tags'})
            if tags:
                for tag in tags.find_all('a'):
                    dc['tags'].append(tag.text)

            recommendations = dt.soup.find_all('h3', {'class': 'post-summary__title'})
            for recommendation in recommendations:
                dc['recommendations'].append(recommendation.text)
            rcls.append(dc)

        for recipe_url in recipe_urls:
            thr = Thread(target=sf, args=[recipe_url.find('a', recursive=False)['href']])
            thrls.append(thr)
            thr.start()
        for thr in thrls:
            thr.join()

        ls.extend(rcls)

    json.dump(ls, open('dump.json', 'w'))


if __name__ == '__main__':
    main()
