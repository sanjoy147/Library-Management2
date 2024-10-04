from django.shortcuts import render
from django.http import HttpResponse


from library.models import Book, Borrow, Student

# Create your views here.
def say_hello(request):
    
    return render(request,'hello.html')

def show_page(request):
    queryset=list(Student.objects.filter(pk__gt=990))
    queryset2=Borrow.objects.values_list('student','student__first_name','book')
    books=Borrow.objects.filter(pk=1)


    # for i in range(1,10):
    #     borrow=Borrow()
    #     borrow.student=Student(pk=queryset[i].pk)
    #     borrow.book=Book(pk=i)
    #     borrow.save()
    
    return render(request,'page.html',{'name':'sujoy','results':list(books)})


#borrow=Borrow()
    
    #borrow.student_roll=Student(pk=2)
    #borrow.book_id=Book(pk=2)
    #borrow.save()
    
    

