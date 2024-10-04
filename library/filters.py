from django_filters.rest_framework import FilterSet

from library.models import Book, Student
class BookFilter(FilterSet):
    class Meta:
        model=Book
        fields={
            'added_date':['lt','gt'],
            'quantity':['lt','gt']
        }
        

class StudentFilter(FilterSet):
    class Meta:
        model=Student
        fields={
            'session':['lt','gt']
        }