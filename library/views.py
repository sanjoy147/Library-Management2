from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter,OrderingFilter
from core.serializers import UserSerializer
from library.filters import BookFilter, StudentFilter
from library.permissions import IsAdminOrReadOnly
from .models import Borrow, Student,Book,BorrowRequest
from .serializer import  BookSerializer, StudentSerializer,BorrowSerializer,BorrowRequestSerializer
from rest_framework import status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.db.models import F
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from django.contrib.auth import login,authenticate,logout
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()

class UserUpdateSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ['email', 'first_name', 'last_name']

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ['user__first_name', 'user__last_name', 'session']
    ordering_fields = ['first_name', 'last_name', 'session']
    
    @action(detail=False, methods=['GET', 'PUT', 'PATCH'])
    def me(self, request):
        student, _ = Student.objects.get_or_create(user_id=request.user.id)
        user_instance = student.user  # Get the associated User instance

        if request.method == 'GET':
            student_serializer = StudentSerializer(student)
            borrow_requests = BorrowRequest.objects.filter(student=student)
            
            # Serialize borrow requests including book attributes
            borrow_request_data = []
            for borrow_request in borrow_requests:
                borrow_request_data.append({
                    'id': borrow_request.id,
                    'book': BookSerializer(borrow_request.book).data,  # Serialize the book
                    'request_date': borrow_request.request_date,
                    'status': borrow_request.status
                })
            
            response_data = {
                'student': student_serializer.data,
                'borrow_requests': borrow_request_data,
            }
            return Response(response_data)    
        
        
        elif request.method in ['PUT', 'PATCH']:
            student_serializer = StudentSerializer(student, data=request.data, partial=True)
            user_serializer = UserUpdateSerializer(user_instance, data=request.data, partial=True)
            student_serializer.is_valid(raise_exception=True)
            student_serializer.save()
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
            return Response(student_serializer.data)
    

class BookViewSet(ModelViewSet):
    queryset=Book.objects.all()
    serializer_class=BookSerializer
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class=BookFilter
    search_fields=['book_name','author']
    ordering_fields=['book_name','author']
    # permission_classes=[IsAdminOrReadOnly]
    # permission_classes=[IsAuthenticated]
    # permission_classes=[IsAdminUser]

    
    @action(detail=False, methods=['PUT', 'PATCH'])
    def patch(self, request):
        book= Student.objects.get(id=request.id)
        print("book", book)
        if request.method == 'PATCH':
            book_id = request.data.get('id')
        quantity = request.data.get('quantity')

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'detail': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        book.quantity = quantity
        book.save()

        serializer = BookSerializer(book)
        return Response(serializer.data)

    
    
class BorrowRequestViewSet(ModelViewSet):
    queryset = BorrowRequest.objects.all()
    serializer_class = BorrowRequestSerializer
    permission_classes = [IsAuthenticated]

    # Adding filter and search backends
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Specify fields for searching and ordering
    search_fields = ['student__roll', 'book__book_name', 'book__author']
    ordering_fields = ['student__roll', 'book__book_name', 'book__author', 'request_date','status']
    ordering = ['request_date'] 
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Will raise ValidationError if invalid
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
    

    

    
##############################################################################################


class BorrowedViewSet(ModelViewSet):
    queryset = Borrow.objects.select_related('book','student').all()
    serializer_class = BorrowSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['issue_date']
    search_fields = ['student__user__username', 'student__user__first_name', 'student__user__last_name', 'book__book_name', 'book__author', 'issue_date']
    ordering_fields = ['student__first_name', 'student__last_name', 'book__book_name', 'book__author', 'issue_date']
    permission_classes = [IsAdminOrReadOnly]


class borrowed_book_by_student(APIView):
    def get(self, request, id):
        queryset = Borrow.objects.filter(student_id=id).select_related('book')
        books_data = []
        for object in queryset:
            book_data = {
                'book': BookSerializer(object.book).data,
                'issue_date': object.issue_date
            }
            books_data.append(book_data)
        return Response(books_data, status=status.HTTP_200_OK)
    
    


@api_view(['POST'])
def logout_page(request):
    if request.method == 'POST':
        logout(request)
        return Response('Logedout')
    return Response('Not logout')

from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_admin_logout(request):
    logout(request)
    return redirect('static/homepage/index.html/') 


