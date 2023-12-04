from django.db import models
import hashlib
from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=False)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=False)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=1000, blank=False)
    phone_number = models.CharField(max_length=20)
    account_number = models.CharField(max_length=11, unique=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=4, default=20.00)
    notifications = models.JSONField(default=list)

    def add_notification(self, message):
        # Add a new notification with a timestamp
        self.notifications.append({
            'message': message,
            'timestamp': timezone.now().isoformat(),
        })
        self.save()

    def get_notifications(self):
        # Retrieve and return the latest 10 notifications
        return Notification.objects.filter(user=self.user).order_by('-timestamp')[:10]

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

class Block(models.Model):
    index = models.PositiveIntegerField()
    proof_no = models.PositiveIntegerField()
    prev_hash = models.CharField(max_length=64)
    timestamp = models.DateTimeField()
    data = models.JSONField()

    def calculate_hash(self):
        # Calculate the hash of the block
        block_of_string = f"{self.index}{self.proof_no}{self.prev_hash}{self.data}{self.timestamp}"
        return hashlib.sha256(block_of_string.encode()).hexdigest()

    def set_timestamp(self, timestamp=None):
        # Set the timestamp of the block to the current time
        self.timestamp = timestamp or datetime.now().isoformat()
        self.save()

class BlockChain(models.Model):
    chain = models.OneToOneField(Block, on_delete=models.CASCADE, null=True, blank=True)
    current_data = models.JSONField(default=list)

    def get_last_block(self):
        try:
            # Get the latest block in the chain
            return Block.objects.latest('index')
        except Block.DoesNotExist:
            return None

    def create_genesis_block(self):
        # Create the genesis block with initial data
        data = {
            "proof_no": 1,
            "prev_hash": "0",
            "data": []
        }
        genesis_block = Block(index=0, **data)
        genesis_block.set_timestamp()
        genesis_block.save()
        self.chain = genesis_block
        self.save()

    def create_new_block(self, proof_no, prev_hash):
        # Create a new block with the given proof number and previous hash
        data = {
            "proof_no": proof_no,
            "prev_hash": prev_hash,
            "data": self.current_data
        }
        new_block = Block(index=len(Block.objects.all()), **data)
        new_block.set_timestamp()
        new_block.save()
        self.chain = new_block
        self.current_data = []
        self.save()

    def new_transaction(self, sender, recipient, quantity):
        # Add a new transaction to the current data
        self.current_data.append({
            "sender": sender,
            "recipient": recipient,
            "quantity": quantity,
        })
        return Block.objects.last().index + 1

    @staticmethod
    def proof_of_work(last_proof):
        # Find a valid proof for mining
        proof_no = 0
        while BlockChain.valid_proof(last_proof, proof_no) is False:
            proof_no += 1
        return proof_no

    @staticmethod
    def valid_proof(last_proof, proof):
        # Check if the proof is valid
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
