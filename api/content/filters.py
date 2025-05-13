from django_filters import rest_framework as filters
from apps.content.models import Content

class ContentFilter(filters.FilterSet):
    content_type = filters.CharFilter(field_name='content_type', lookup_expr='exact')

    class Meta:
        model = Content
        fields = ['content_type']
