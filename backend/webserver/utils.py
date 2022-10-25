from rest_framework.pagination import PageNumberPagination
from rest_framework.utils.urls import replace_query_param

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'size'
    
    # overrides this method from the base class so that the page query parameter on the first
    # page is not removed
    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        # if page_number == 1:
        #     return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)


# Reference: https://medium.com/@fk26541598fk/django-rest-framework-apiview-implementation-pagination-mixin-c00c34da8ac2
# Date Accessed: 2022/10/23
# Owner: Frank Liao
class PaginationHandlerMixin(object):
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None or self.request.query_params.get(self.paginator.page_query_param, None) is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
