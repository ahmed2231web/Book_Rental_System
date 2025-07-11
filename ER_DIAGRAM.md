# Book Rental System - Entity Relationship Diagram

```mermaid
erDiagram
    CustomUser {
        int id PK
        string email UK "Unique email address"
        string username UK "Unique username"
        string first_name
        string last_name
        string password
        string role "admin or user"
        datetime created_at
        datetime updated_at
        boolean is_active
        boolean is_staff
        boolean is_superuser
        datetime last_login
    }

    Book {
        uuid id PK "UUID primary key"
        string title
        string author
        string isbn UK "Unique 10/13 digit ISBN"
        date publication_date
        string genre "Choice from predefined genres"
        text description
        int total_copies "Total inventory"
        int available_copies "Available for rental"
        datetime created_at
        datetime updated_at
    }

    Rental {
        uuid id PK "UUID primary key"
        int user_id FK "Foreign key to CustomUser"
        uuid book_id FK "Foreign key to Book"
        datetime rented_at "Auto-generated"
        datetime due_date "Calculated from rental period"
        datetime returned_at "Set when returned"
        string status "active, returned, or overdue"
        datetime created_at
        datetime updated_at
    }

    %% Relationships
    CustomUser ||--o{ Rental : "has many rentals"
    Book ||--o{ Rental : "can be rented multiple times"

    %% Additional constraints and notes
    %% - Rental has unique_together constraint on (user, book, status)
    %% - This prevents multiple active rentals of same book by same user
    %% - Books become unavailable when available_copies reaches 0
    %% - Rental status automatically updates to 'overdue' when past due_date
```

## Key Relationships

### **One-to-Many Relationships:**

1. **CustomUser → Rental** (1:N)
   - One user can have multiple rentals
   - Each rental belongs to exactly one user
   - Implemented as `user = ForeignKey(CustomUser, related_name='rentals')`

2. **Book → Rental** (1:N)
   - One book can be rented multiple times (different periods)
   - Each rental is for exactly one book
   - Implemented as `book = ForeignKey(Book, related_name='rentals')`

### **Database Constraints:**

- **Unique Together**: `(user, book, status)` prevents duplicate active rentals
- **Indexes**: Optimized queries on user+status, book+status, due_date+status
- **Validation**: Available copies cannot exceed total copies
- **UUID Primary Keys**: For books and rentals (better for distributed systems)

### **Business Logic:**

- When rental created → `book.available_copies -= 1`
- When book returned → `book.available_copies += 1`
- Auto-overdue detection when `timezone.now() > due_date`