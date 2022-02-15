class FilterManager:
    def __init__(self):
        self.filter_delegates = {
            'order_by_difficulty_asc': self.order_by_difficulty_asc,
            'order_by_difficulty_desc': self.order_by_difficulty_desc,
            'order_by_rating_asc': self.order_by_rating_asc,
            'order_by_rating_desc': self.order_by_rating_desc
        }

    def apply_filters(self, filters, query_set):
        for flr in filters:
            self.filter_delegates[flr](query_set)
        return query_set

    def order_by_difficulty_asc(self, query_set):
        return query_set.order_by('difficulty')

    def order_by_difficulty_desc(self, query_set):
        return query_set.order_by('-difficulty')

    def order_by_rating_asc(self, query_set):
        return query_set.order_by('rating')

    def order_by_rating_desc(self, query_set):
        return query_set.order_by('-rating')

