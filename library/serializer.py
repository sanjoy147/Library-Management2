from rest_framework import serializers

from library.models import Book, Borrow, BorrowRequest, Student


class StudentSerializer(serializers.ModelSerializer):
    user_id=serializers.IntegerField(read_only=True)
    session=serializers.CharField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['user_id', 'roll', 'email', 'first_name', 'last_name', 'session', 'phone']

    def get_email(self, obj):
        return obj.user.email

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['email'] = self.get_email(instance)
        return representation

    def update(self, instance, validated_data):
        # Remove email from validated data to prevent updating it
        validated_data.pop('email', None)
        return super().update(instance, validated_data)
    
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id','book_name', 'author', 'quantity', 'added_date']
        read_only_fields = ['id']

class BorrowSerializer(serializers.ModelSerializer):
    student=StudentSerializer()
    book=BookSerializer()
    class Meta:
        model=Borrow
        fields=['student','book','issue_date','return_date']




class BorrowRequestSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField(write_only=True)  # Keep as write-only for incoming requests
    book = BookSerializer(read_only=True)  # Read-only field for the book details
    #student = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(), read_only=True)
    student=StudentSerializer()
    class Meta:
        model = BorrowRequest
        fields = ['id', 'book_id', 'book', 'student', 'request_date', 'status']
        read_only_fields = ['student', 'status']

    def validate(self, data):
        book_id = data.get('book_id')
        
        # Check if the book with the given ID exists in the Book table
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError("The provided book ID does not exist.")
        
        # Check if the book is available for borrowing
        if book.quantity <= 0:
            raise serializers.ValidationError("The book is not available for borrowing.")
        
        # Assign the student from the request context
        data['student'] = self.context['request'].user.student
        
        # Check if the student has already requested to borrow the same book
        existing_requests = BorrowRequest.objects.filter(student=data['student'], book_id=book_id)
        if existing_requests.exists():
            raise serializers.ValidationError("A request for this book already exists.")

        return data
