from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'current_page': self.page.number,
                'per_page': self.page_size,
                'total_count': self.page.paginator.count,
                'next': self.get_next_page_number(),
                'previous': self.get_previous_page_number(),
                'total_pages': self.page.paginator.num_pages
            },
            'results': data
        })

    def get_next_page_number(self):
        if not self.page.has_next():
            return None
        return self.page.next_page_number()

    def get_previous_page_number(self):
        if not self.page.has_previous():
            return None
        return self.page.previous_page_number()