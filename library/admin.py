from django.contrib import admin

from . import models
# Register your models here.

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

admin.site.site_header = _("Library Management Admin")
admin.site.site_title = _("Library Admin Portal")
admin.site.index_title = _("Welcome to the Library Management Dashboard")


@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display=['book_name','author','quantity']
    search_fields = ['book_name', 'author']
    
    
@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_select_related=['user']
    list_display=['roll','first_name','last_name','session','phone']
    search_fields = ['user__first_name', 'user__last_name', 'session']
    
@admin.register(models.Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display=['student','book','issue_date','return_date']
    search_fields = ['student__user__username', 'student__user__first_name', 'student__user__last_name', 'book__book_name', 'book__author', 'issue_date']
    
@admin.register(models.BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):

    list_display=['student','book','request_date','status']
    list_editable=['status']
    search_fields = ['student__roll', 'book__book_name', 'book__author']
    

