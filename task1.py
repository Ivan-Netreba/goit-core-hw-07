from collections import defaultdict, UserDict
from functools import wraps
import datetime as dt
from datetime import timedelta, datetime as dtdt

# Базовий клас для полів запису.
class Field():
    def __init__(self, value: str):
        self.value = value

    def str(self):
        return str(self.value)

# Клас для зберігання імені контакту. Обов'язкове поле.
class Name(Field):
    def __init__(self, value: str):
        if value:
            super().__init__(value)
        else:
            raise ValueError
          
# Реалізовано валідацію номера телефону (має бути перевірка на 10 цифр).
class Phone(Field):
    def __init__(self, value: str):
        if value.isdigit() and len(value) == 10:
            super().__init__(value)
        else:
            raise ValueError

# Клас для зберігання дати народження (це поле не обов'язкове, але може бути тільки одне).    
class Birthday(Field):
    def __init__(self, value:str):
        try:
            dtdt.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

# Клас для зберігання інформації про контакт, включаючи ім'я та список телефонів.
class Record:
    def __init__(self, name: Name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, number: str):
        self.phones.append(Phone(number))

    def remove_phone(self, number: str):
        for phone in self.phones:
            if phone.value == number:
                self.phones.remove(phone)
            else:
                raise ValueError

    def edit_phone(self, old_number: str, new_number: str):
        if new_number.isdigit() and len(new_number) == 10:
            for phone in self.phones:
                if phone.value == old_number:
                    phone.value = new_number
                    break
            else:
                raise ValueError
        else:
            raise ValueError

    def find_phone(self, number: str) -> Phone:
        for phone in self.phones:
            if phone.value == number:
                return phone
             
    def add_birthday(self, birthday:str):
        self.birthday = Birthday(birthday)
        
    def get_birthday(self):
        if self.birthday:
            return f"{self.name.value} birthday is on {self.birthday.value}"
        else:
            return f"No birthday found for {self.name.value}"

    def str(self):
            return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

# Клас для зберігання та управління записами.
class AddressBook(UserDict):
    
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        if name in self.data:
            return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
        else:
            return "Contact not found"

    def get_upcoming_birthdays(self):
        tdate=dtdt.today().date() 
        upcoming_birthdays = [] 
        for key, record in self.data.items(): 
            if record.birthday:
                bd_day, bd_month, bd_year = record.birthday.value.split('.')
                bdate = f"{tdate.year}-{bd_month}-{bd_day}"
                bdate = dtdt.strptime(bdate, "%Y-%m-%d").date()
                week_day = tdate.isoweekday() 
                days_between = (bdate-tdate).days 
                if 0<=days_between<7: 
                    if week_day<6: 
                        upcoming_birthdays.append({'name':record.name.value, 'birthday':bdate.strftime("%Y.%m.%d")}) 
                else:
                    if (bdate+dt.timedelta(days=1)).weekday()==0:
                        upcoming_birthdays.append({'name':record.name.value, 'birthday':(bdate+dt.timedelta(days=1)).strftime("%Y.%m.%d")})
                    elif (bdate+dt.timedelta(days=2)).weekday()==0: # Якщо субота
                        upcoming_birthdays.append({'name':record.name.value, 'birthday':(bdate+dt.timedelta(days=2)).strftime("%Y.%m.%d")})
        return upcoming_birthdays

def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "No such name found."
        except IndexError:
            return "Not found."
        except Exception as e:
            return f"Error : {e}"
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args 
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)

        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
    return "The number has been changed"

@input_error
def show_phone(args, book: AddressBook):
    return book.find(args[0])

@input_error    
def show_all(book):
    s = ''
    for key in book.data:  
        record = book.find(key)  
        s += f"{key:10} : {'; '.join(phone.value for phone in record.phones)}\n"
    return s

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        message = "Birthday added."
    else:
        message = "Contact not found."
    return message

@input_error
def show_birthday(args, book: AddressBook):
    record = book.find(args[0])
    if record:
        return record.get_birthday()
    else:
        return "Contact not found."

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        for birthday in upcoming_birthdays:
            return f"{birthday['name']} birthday is on {birthday['birthday']}"
    else:
        return "No upcoming birthdays."
    

@input_error    
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()