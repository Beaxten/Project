class TransactionStack:
    """
    LIFO Stack to track recent transactions.
    Used for: showing last transaction, potential undo feature.
    DSA Concept: Stack (Last In First Out)
    """
    def __init__(self):
        self._data = []
    
    def push(self, transaction):
        self._data.append(transaction)
    
    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self._data.pop()
    
    def peek(self):
        return self._data[-1] if not self.is_empty() else None
    
    def is_empty(self):
        return len(self._data) == 0
    
    def size(self):
        return len(self._data)


class TransactionQueue:
    """
    FIFO Queue for processing transfers in order.
    DSA Concept: Queue (First In First Out)
    """
    def __init__(self):
        self._data = []
    
    def enqueue(self, transaction):
        self._data.append(transaction)
    
    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self._data.pop(0)
    
    def is_empty(self):
        return len(self._data) == 0
    
    def size(self):
        return len(self._data)


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class TransactionLinkedList:
    """
    Singly Linked List for iterating transaction history.
    DSA Concept: Linked List
    """
    def __init__(self):
        self.head = None
    
    def append(self, transaction):
        new_node = Node(transaction)
        if not self.head:
            self.head = new_node
            return
        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = new_node
    
    def to_list(self):
        result = []
        curr = self.head
        while curr:
            result.append(curr.data)
            curr = curr.next
        return result
    
    def search(self, transaction_id):
        curr = self.head
        while curr:
            if curr.data.get('transaction_id') == transaction_id:
                return curr.data
            curr = curr.next
        return None