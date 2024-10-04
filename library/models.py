from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib import admin

# Create your models here.

class Student(models.Model): 
    session=models.CharField(max_length=8,null=True)
    phone=models.CharField(max_length=15,null=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.user.first_name+' '+self.user.last_name

    class Meta:
        ordering=['user__first_name','user__last_name']
        
    
    def roll(self):
        return self.user.username
    
    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
    
    
class Book(models.Model):

    book_name=models.CharField(max_length=255)
    author=models.CharField(max_length=255)
    quantity=models.PositiveIntegerField()
    added_date=models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return self.book_name
    class Meta:
        ordering=['book_name','author']
    
class Borrow(models.Model):
    student=models.ForeignKey(Student,on_delete=models.SET_NULL,null=True)
    book=models.ForeignKey(Book,on_delete=models.SET_NULL,null=True)
    issue_date=models.DateTimeField(auto_now=True)
    return_date=models.DateTimeField(null=True, blank=True)
    
    
    

class BorrowRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    
    CHOICES=[
        ('P','Pending'),
        ('A','Accepted'),
        ('C', 'Cancelled'),
        ('R', 'Returned'),
    ]
    status=models.CharField(max_length=1,choices=CHOICES, default='P')
    
from datetime import timedelta
from django.utils import timezone
@receiver(post_save, sender=BorrowRequest)
def create_borrow_record(sender, instance, created, **kwargs):
    print(instance.status,bool(created))
    if  not created and instance.status == 'A':  # Only proceed if the status is Accepted
        # Create a new Borrow record
        borrow = Borrow.objects.create(student=instance.student, book=instance.book)
        return_date = timezone.now() + timedelta(days=5)
        borrow.return_date = return_date
        borrow.save()
        # Decrease the quantity of the book
        instance.book.quantity -= 1
        instance.book.save()
        
        
    elif instance.status == 'R':  # If status is Rejected
            # Delete the corresponding Borrow record
            try:
                borrow_record = Borrow.objects.get(student=instance.student, book=instance.book)
                borrow_record.delete()
            except Borrow.DoesNotExist:
                pass  # Borrow record doesn't exist, no action needed
            # Increase the quantity of the book
            instance.book.quantity += 1
            instance.book.save()

    
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(user=instance)