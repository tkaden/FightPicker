import scrapy
from scrapy.loader import ItemLoader
from fight_scraper.items import *
from fight_scraper.utils import *

class UpcomingFightsSpider(scrapy.Spider):
    name = 'upcoming'
    start_urls = ['http://ufcstats.com/statistics/events/completed']
    time_created = print_time('now')

    custom_settings = {
        'FEED_FORMAT': 'csv', 
        'FEED_URI': f'data/upcoming/{time_created}.csv'
    }

    def parse(self, response):
        """
        Parse the event listing page, follow link to individual events page
        """

        event_url = response.css(
            'tbody .b-statistics__table-row_type_first ::attr(href)').get()

        yield response.follow(event_url, callback=self.parse_upcoming_event)

    def parse_upcoming_event(self, response):
        """
        Parse the event page, follow link to each individual fight page
        """

        event_info = response.css('.b-list__box-list-item')
        date = event_info[0].css('::text').getall()[-1]
        location = event_info[1].css('::text').getall()[-1]
        fights_url = response.css(
            '.b-fight-details__table-row ::attr(data-link)')

        for fight in fights_url:
            yield response.follow(fight,
                                  callback=self.parse_upcoming_fight,
                                  cb_kwargs=dict(date=date, location=location))

    def parse_upcoming_fight(self, response, date, location):
        """
        Parse fight info - fight level summary, and fighter stats
        """

        ##### Fight summary ######
        fight_id = response.url.split('/')[-1]
        # date and location carry over from events page
        date = date.strip()
        location = location.strip()

        # Fighter names
        names = response.css(
            '.b-fight-details__person-name :not(p)::text').getall()
        try:
            fighter_1 = names[0].strip()
            fighter_2 = names[1].strip()
        except:
            fighter_1 = None
            fighter_2 = None

        # IDs - Handle errors due to missing fighter link
        ids = response.css('.b-fight-details__person-name')
        fighter_1_id = ids[0].css('::attr(href)').get()
        fighter_2_id = ids[1].css('::attr(href)').get()

        if fighter_1_id is not None:
            fighter_1_id = fighter_1_id.split('/')[-1]
        if fighter_2_id is not None:
            fighter_2_id = fighter_2_id.split('/')[-1]

        weight_class = response.css(
            '.b-fight-details__fight-title ::text').getall()

        if len(weight_class) > 1:
            weight_class = weight_class[-1].strip()
        if len(weight_class) == 1:
            weight_class = weight_class[0].strip()

        l = ItemLoader(item=UpcomingFightsItem(), response=response)
        l.add_value('fight_id', fight_id)
        l.add_value('date', date)
        l.add_value('location', location)
        l.add_value('fighter_1', fighter_1)
        l.add_value('fighter_1_id', fighter_1_id)
        l.add_value('fighter_2', fighter_2)
        l.add_value('fighter_2_id', fighter_2_id)
        l.add_value('weight_class', weight_class)

        yield l.load_item()