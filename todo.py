import argparse
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

TODO_FILE = "todo_data.json"

class TodoItem:
    def __init__(self, id: int, title: str, description: str = "", due_date: str = None, 
                 priority: int = 3, completed: bool = False):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority  # 1: High, 2: Medium, 3: Low
        self.completed = completed

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "completed": self.completed
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'TodoItem':
        return cls(
            data["id"],
            data["title"],
            data.get("description", ""),
            data.get("due_date"),
            data.get("priority", 3),
            data.get("completed", False)
        )

    def __str__(self) -> str:
        status = "✓" if self.completed else "✗"
        priority_map = {1: "High", 2: "Medium", 3: "Low"}
        due_date = f" | Due: {self.due_date}" if self.due_date else ""
        return (
            f"{self.id}. [{status}] {self.title}"
            f"{due_date} | Priority: {priority_map[self.priority]}"
            f"\n   {self.description}"
        )

class TodoList:
    def __init__(self):
        self.todos: List[TodoItem] = []
        self.next_id = 1
        self.load_data()

    def add_item(self, title: str, description: str = "", due_date: str = None, 
                 priority: int = 3) -> TodoItem:
        new_item = TodoItem(self.next_id, title, description, due_date, priority)
        self.todos.append(new_item)
        self.next_id += 1
        self.save_data()
        return new_item

    def remove_item(self, item_id: int) -> bool:
        for i, item in enumerate(self.todos):
            if item.id == item_id:
                self.todos.pop(i)
                self.save_data()
                return True
        return False

    def complete_item(self, item_id: int) -> bool:
        for item in self.todos:
            if item.id == item_id:
                item.completed = True
                self.save_data()
                return True
        return False

    def get_item(self, item_id: int) -> Optional[TodoItem]:
        for item in self.todos:
            if item.id == item_id:
                return item
        return None

    def list_items(self, show_completed: bool = False) -> List[TodoItem]:
        if show_completed:
            return self.todos
        return [item for item in self.todos if not item.completed]

    def save_data(self):
        data = {
            "todos": [item.to_dict() for item in self.todos],
            "next_id": self.next_id
        }
        with open(TODO_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load_data(self):
        if not os.path.exists(TODO_FILE):
            return

        try:
            with open(TODO_FILE, "r") as f:
                data = json.load(f)
                self.todos = [TodoItem.from_dict(item) for item in data["todos"]]
                self.next_id = data["next_id"]
        except (json.JSONDecodeError, FileNotFoundError):
            # Handle corrupt or missing file
            self.todos = []
            self.next_id = 1

def display_todos(todo_list: TodoList, show_completed: bool = False):
    todos = todo_list.list_items(show_completed)
    if not todos:
        print("No todo items found.")
        return

    print("\nTo-Do List:")
    print("=" * 50)
    for item in todos:
        print(item)
    print("=" * 50)

def main():
    todo_list = TodoList()
    
    parser = argparse.ArgumentParser(description="To-Do List CLI Application")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new todo item")
    add_parser.add_argument("title", help="Title of the todo item")
    add_parser.add_argument("-d", "--description", help="Description of the todo item", default="")
    add_parser.add_argument("-due", "--due_date", help="Due date (YYYY-MM-DD)", default=None)
    add_parser.add_argument("-p", "--priority", type=int, choices=[1, 2, 3], 
                           help="Priority (1: High, 2: Medium, 3: Low)", default=3)

    # List command
    list_parser = subparsers.add_parser("list", help="List todo items")
    list_parser.add_argument("-a", "--all", action="store_true", 
                            help="Show all items including completed")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark an item as completed")
    complete_parser.add_argument("id", type=int, help="ID of the item to complete")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a todo item")
    remove_parser.add_argument("id", type=int, help="ID of the item to remove")

    # View command
    view_parser = subparsers.add_parser("view", help="View details of a specific todo item")
    view_parser.add_argument("id", type=int, help="ID of the item to view")

    args = parser.parse_args()

    try:
        if args.command == "add":
            # Validate due date format if provided
            if args.due_date:
                try:
                    datetime.strptime(args.due_date, "%Y-%m-%d")
                except ValueError:
                    print("Error: Invalid date format. Please use YYYY-MM-DD.")
                    return

            new_item = todo_list.add_item(
                args.title,
                args.description,
                args.due_date,
                args.priority
            )
            print(f"Added new todo item (ID: {new_item.id}): {new_item.title}")

        elif args.command == "list":
            display_todos(todo_list, args.all)

        elif args.command == "complete":
            if todo_list.complete_item(args.id):
                print(f"Marked item {args.id} as completed.")
            else:
                print(f"Error: Item with ID {args.id} not found.")

        elif args.command == "remove":
            if todo_list.remove_item(args.id):
                print(f"Removed item with ID {args.id}.")
            else:
                print(f"Error: Item with ID {args.id} not found.")

        elif args.command == "view":
            item = todo_list.get_item(args.id)
            if item:
                print("\nTodo Item Details:")
                print("=" * 50)
                print(item)
                print("=" * 50)
            else:
                print(f"Error: Item with ID {args.id} not found.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
