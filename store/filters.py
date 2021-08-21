import django_filters
from store import models
from django_filters import DateFilter, CharFilter

class ProductFilter(django_filters.FilterSet):
	name_filter = CharFilter(field_name='name', lookup_expr='icontains')

	class Meta:
		model = models.Product
		fields = ['price']