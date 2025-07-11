from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema_field
from .models import CustomUser, Book, Rental


# Minimal serializers for cleaner responses
class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user serializer for login responses"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'role')
    
    @extend_schema_field(serializers.CharField)
    def get_full_name(self, obj: CustomUser) -> str:
        return f"{obj.first_name} {obj.last_name}"


class UserRegistrationResponseSerializer(serializers.ModelSerializer):
    """Minimal user serializer for registration responses"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'role')
    
    @extend_schema_field(serializers.CharField)
    def get_full_name(self, obj: CustomUser) -> str:
        return f"{obj.first_name} {obj.last_name}"


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that uses email instead of username"""
    username_field = 'email'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField()
        # Only delete username field if it exists
        if 'username' in self.fields:
            del self.fields['username']
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = f"{user.first_name} {user.last_name}"
        return token
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                              email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError('Must include email and password.')
        
        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserMinimalSerializer(user).data
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'role')
        extra_kwargs = {
            'role': {'default': 'user'},
            'username': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value
    
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'role', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    @extend_schema_field(serializers.CharField)
    def get_full_name(self, obj: CustomUser) -> str:
        return f"{obj.first_name} {obj.last_name}"


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')
    
    def validate_email(self, value):
        user = self.instance
        if user and CustomUser.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model"""
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_available(self, obj: Book) -> bool:
        return obj.available_copies > 0
    
    def validate_isbn(self, value):
        # Remove any hyphens or spaces for validation
        isbn = value.replace('-', '').replace(' ', '')
        if len(isbn) not in [10, 13]:
            raise serializers.ValidationError("ISBN must be 10 or 13 digits long.")
        return isbn
    
    def validate(self, attrs):
        if 'available_copies' in attrs and 'total_copies' in attrs:
            if attrs['available_copies'] > attrs['total_copies']:
                raise serializers.ValidationError("Available copies cannot exceed total copies.")
        return attrs


class BookCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating books"""
    class Meta:
        model = Book
        fields = ('title', 'author', 'isbn', 'publication_date', 'genre', 
                 'description', 'total_copies', 'available_copies')
    
    def validate_isbn(self, value):
        isbn = value.replace('-', '').replace(' ', '')
        if len(isbn) not in [10, 13]:
            raise serializers.ValidationError("ISBN must be 10 or 13 digits long.")
        
        # Check for uniqueness during update
        if self.instance:
            if Book.objects.filter(isbn=isbn).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Book with this ISBN already exists.")
        else:
            if Book.objects.filter(isbn=isbn).exists():
                raise serializers.ValidationError("Book with this ISBN already exists.")
        
        return isbn


class RentalSerializer(serializers.ModelSerializer):
    """Serializer for Rental model"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Rental
        fields = '__all__'
        read_only_fields = ('id', 'rented_at', 'created_at', 'updated_at', 'user_email', 
                           'user_name', 'book_title', 'book_author', 'is_overdue', 'days_until_due')
    
    @extend_schema_field(serializers.CharField)
    def get_user_name(self, obj: Rental) -> str:
        return f"{obj.user.first_name} {obj.user.last_name}"
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_overdue(self, obj: Rental) -> bool:
        return obj.is_overdue()
    
    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_days_until_due(self, obj: Rental):
        if obj.status == 'returned':
            return None
        days = (obj.due_date.date() - timezone.now().date()).days
        return days


class RentalCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating rentals"""
    rental_period_days = serializers.IntegerField(write_only=True, default=14, min_value=1, max_value=30)
    
    class Meta:
        model = Rental
        fields = ('book', 'rental_period_days')
    
    def validate_book(self, value):
        if value.available_copies <= 0:
            raise serializers.ValidationError("This book is not available for rental.")
        return value
    
    def validate(self, attrs):
        user = self.context['request'].user
        book = attrs['book']
        
        # Check if user already has an active rental for this book
        active_rental = Rental.objects.filter(
            user=user, 
            book=book, 
            status__in=['active', 'overdue']
        ).exists()
        
        if active_rental:
            raise serializers.ValidationError("You already have an active rental for this book.")
        
        return attrs
    
    def create(self, validated_data):
        rental_period = validated_data.pop('rental_period_days', 14)
        user = self.context['request'].user
        book = validated_data['book']
        
        # Set due date
        due_date = timezone.now() + timedelta(days=rental_period)
        
        # Create rental
        rental = Rental.objects.create(
            user=user,
            book=book,
            due_date=due_date,
            status='active'
        )
        
        # Decrease available copies
        book.available_copies -= 1
        book.save()
        
        return rental


class RentalReturnSerializer(serializers.Serializer):
    """Serializer for returning books"""
    rental_id = serializers.UUIDField()
    
    def validate_rental_id(self, value):
        try:
            rental = Rental.objects.get(id=value)
        except Rental.DoesNotExist:
            raise serializers.ValidationError("Rental not found.")
        
        if rental.status == 'returned':
            raise serializers.ValidationError("This book has already been returned.")
        
        return value


class BookSearchSerializer(serializers.Serializer):
    """Serializer for book search parameters"""
    search = serializers.CharField(required=False, help_text="Search in title, author, or description")
    genre = serializers.ChoiceField(choices=Book.GENRE_CHOICES, required=False)
    author = serializers.CharField(required=False)
    publication_year = serializers.IntegerField(required=False, min_value=1000, max_value=timezone.now().year)
    available_only = serializers.BooleanField(required=False, default=False)
    ordering = serializers.ChoiceField(
        choices=[
            'title', '-title', 'author', '-author', 
            'publication_date', '-publication_date', 
            'created_at', '-created_at'
        ],
        required=False,
        default='-created_at'
    ) 