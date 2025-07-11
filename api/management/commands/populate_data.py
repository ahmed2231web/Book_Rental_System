from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from api.models import Book, Rental

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of users to create'
        )
        parser.add_argument(
            '--books',
            type=int,
            default=20,
            help='Number of books to create'
        )
        parser.add_argument(
            '--rentals',
            type=int,
            default=10,
            help='Number of rentals to create'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate database...'))
        
        # Create admin user
        admin, created = User.objects.get_or_create(
            email='admin@bookrental.com',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.email}'))
        
        # Create sample users
        users_created = 0
        for i in range(options['users']):
            user, created = User.objects.get_or_create(
                email=f'user{i+1}@example.com',
                defaults={
                    'username': f'user{i+1}',
                    'first_name': f'User',
                    'last_name': f'{i+1}',
                    'role': 'user'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                users_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {users_created} users'))
        
        # Sample book data
        sample_books = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'isbn': '9780743273565',
                'publication_date': date(1925, 4, 10),
                'genre': 'fiction',
                'description': 'A classic American novel set in the 1920s.',
                'total_copies': 5,
                'available_copies': 5
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'isbn': '9780061120084',
                'publication_date': date(1960, 7, 11),
                'genre': 'fiction',
                'description': 'A novel about racial injustice in the American South.',
                'total_copies': 3,
                'available_copies': 3
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'isbn': '9780451524935',
                'publication_date': date(1949, 6, 8),
                'genre': 'science_fiction',
                'description': 'A dystopian social science fiction novel.',
                'total_copies': 4,
                'available_copies': 4
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'isbn': '9780141439518',
                'publication_date': date(1813, 1, 28),
                'genre': 'romance',
                'description': 'A romantic novel of manners.',
                'total_copies': 6,
                'available_copies': 6
            },
            {
                'title': 'The Catcher in the Rye',
                'author': 'J.D. Salinger',
                'isbn': '9780316769174',
                'publication_date': date(1951, 7, 16),
                'genre': 'fiction',
                'description': 'A controversial novel about teenage rebellion.',
                'total_copies': 2,
                'available_copies': 2
            },
            {
                'title': 'Harry Potter and the Philosopher\'s Stone',
                'author': 'J.K. Rowling',
                'isbn': '9780747532699',
                'publication_date': date(1997, 6, 26),
                'genre': 'fantasy',
                'description': 'The first book in the Harry Potter series.',
                'total_copies': 8,
                'available_copies': 8
            },
            {
                'title': 'The Lord of the Rings',
                'author': 'J.R.R. Tolkien',
                'isbn': '9780544003415',
                'publication_date': date(1954, 7, 29),
                'genre': 'fantasy',
                'description': 'An epic high fantasy novel.',
                'total_copies': 4,
                'available_copies': 4
            },
            {
                'title': 'The Da Vinci Code',
                'author': 'Dan Brown',
                'isbn': '9780307474278',
                'publication_date': date(2003, 3, 18),
                'genre': 'thriller',
                'description': 'A mystery thriller novel.',
                'total_copies': 3,
                'available_copies': 3
            },
            {
                'title': 'The Alchemist',
                'author': 'Paulo Coelho',
                'isbn': '9780062315007',
                'publication_date': date(1988, 1, 1),
                'genre': 'fiction',
                'description': 'A philosophical book about following your dreams.',
                'total_copies': 5,
                'available_copies': 5
            },
            {
                'title': 'Sapiens: A Brief History of Humankind',
                'author': 'Yuval Noah Harari',
                'isbn': '9780062316097',
                'publication_date': date(2011, 1, 1),
                'genre': 'history',
                'description': 'A book about the history of humanity.',
                'total_copies': 4,
                'available_copies': 4
            },
        ]
        
        # Create books
        books_created = 0
        for book_data in sample_books[:options['books']]:
            book, created = Book.objects.get_or_create(
                isbn=book_data['isbn'],
                defaults=book_data
            )
            if created:
                books_created += 1
        
        # Add more books if needed
        remaining_books = options['books'] - len(sample_books)
        if remaining_books > 0:
            for i in range(remaining_books):
                book_num = len(sample_books) + i + 1
                book, created = Book.objects.get_or_create(
                    isbn=f'978012345{book_num:04d}',
                    defaults={
                        'title': f'Sample Book {book_num}',
                        'author': f'Author {book_num}',
                        'publication_date': date(2020, 1, 1),
                        'genre': 'fiction',
                        'description': f'Description for sample book {book_num}',
                        'total_copies': 3,
                        'available_copies': 3
                    }
                )
                if created:
                    books_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {books_created} books'))
        
        # Create some sample rentals
        users = User.objects.filter(role='user')
        books = Book.objects.all()
        rentals_created = 0
        
        if users.exists() and books.exists():
            for i in range(min(options['rentals'], len(users) * 2)):
                user = users[i % len(users)]
                book = books[i % len(books)]
                
                # Check if user already has an active rental for this book
                existing_rental = Rental.objects.filter(
                    user=user,
                    book=book,
                    status__in=['active', 'overdue']
                ).exists()
                
                if not existing_rental and book.available_copies > 0:
                    due_date = timezone.now() + timedelta(days=14)
                    rental = Rental.objects.create(
                        user=user,
                        book=book,
                        due_date=due_date,
                        status='active'
                    )
                    
                    # Update book availability
                    book.available_copies -= 1
                    book.save()
                    
                    rentals_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {rentals_created} rentals'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Database populated successfully!\n'
                f'Admin user: admin@bookrental.com (password: admin123)\n'
                f'Sample users: user1@example.com to user{options["users"]}@example.com (password: password123)'
            )
        ) 