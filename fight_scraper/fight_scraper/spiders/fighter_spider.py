import scrapy
from scrapy.loader import ItemLoader
from fight_scraper.items import *
from fight_scraper.utils import *

class FighterSpider(scrapy.Spider):
    name = 'fighters'
    start_urls = ['http://ufcstats.com/statistics/fighters']

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'data/fighter_stats/%(time)s.csv'
    }

    def parse(self, response):
        # Parse each page
        by_alphabets = response.css(
            '.b-statistics__nav-link ::attr(href)').getall()

        pages_by_alphabets = []
        for alphabet in by_alphabets:
            link = alphabet + '&page=all'
            pages_by_alphabets.append(link)

        for page in pages_by_alphabets:
            yield response.follow(page, callback=self.parse_fighter_link)

    def parse_fighter_link(self, response):
        # Parse each fighter on page
        rows = response.css('tbody .b-statistics__table-row')
        rows.pop(0)

        for row in rows:
            fighter_link = row.css('.b-statistics__table-col ::attr(href)').get()
            yield response.follow(fighter_link, callback=self.parse_fighter_stat)

    def parse_fighter_stat(self, response):
        # Parse fighter stats
        fighter_id = response.url.split('/')[-1]
        name = response.css('.b-content__title-highlight ::text').get()

        record = response.css('.b-content__title-record ::text').get()
        record = re.findall(r'[0-9]+', record)

        stat_box = response.css('.b-list__box-list')
        stat_box_1 = stat_box[0].css('.b-list__box-list-item')
        stat_box_2 = stat_box[1].css('.b-list__box-list-item')
        stat_box_3 = stat_box[2].css('.b-list__box-list-item')

        height = stat_box_1[0].css('li::text').getall()
        weight = stat_box_1[1].css('li::text').getall()
        reach = stat_box_1[2].css('li::text').getall()
        stance = stat_box_1[3].css('li::text').getall()
        dob = stat_box_1[4].css('li::text').getall()

        sig_str_land_pM = stat_box_2[0].css('li::text').getall()
        sig_str_land_pct = stat_box_2[1].css('li::text').getall()
        sig_str_abs_pM = stat_box_2[2].css('li::text').getall()
        sig_str_def_pct = stat_box_2[3].css('li::text').getall()
        td_avg = stat_box_3[1].css('li::text').getall()
        td_land_pct = stat_box_3[2].css('li::text').getall()
        td_def_pct = stat_box_3[3].css('li::text').getall()
        sub_avg = stat_box_3[4].css('li::text').getall()

        l = ItemLoader(item=FighterSummaryItem(), response=response)
        l.add_value('fighter_id', fighter_id)
        l.add_value('name', name.strip())
        l.add_value('height', height[1].strip())
        l.add_value('weight', weight[1].strip())
        l.add_value('reach', reach[1].strip())
        l.add_value('stance', stance[1].strip())
        l.add_value('dob', dob[1].strip())
        l.add_value('n_win', record[0])
        l.add_value('n_loss', record[1])
        l.add_value('n_draw', record[2])
        l.add_value('sig_str_land_pM', sig_str_land_pM[1].strip())
        l.add_value('sig_str_land_pct', sig_str_land_pct[1].strip())
        l.add_value('sig_str_abs_pM', sig_str_abs_pM[1].strip())
        l.add_value('sig_str_def_pct', sig_str_def_pct[1].strip())
        l.add_value('td_avg', td_avg[1].strip())
        l.add_value('td_land_pct', td_land_pct[1].strip())
        l.add_value('td_def_pct', td_def_pct[1].strip())
        l.add_value('sub_avg', sub_avg[1].strip())

        yield l.load_item()