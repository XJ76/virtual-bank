# Import necessary modules and classes
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import BlockChain, Profile
from decimal import Decimal
import random
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Function for mining new blocks
@login_required(login_url='/login/')
def mine(request):
    # Check if a BlockChain object already exists or create a new one
    blockchain, created = BlockChain.objects.get_or_create(id=1)

    # Get the last block in the blockchain
    last_block = blockchain.get_last_block()

    # If there's no last block, create a genesis block
    if last_block is None:
        blockchain.create_genesis_block()
        last_block = blockchain.get_last_block()

    # Get the last proof number
    last_proof = last_block.proof_no

    # Calculate a new proof number using the proof_of_work method
    proof_no = blockchain.proof_of_work(last_proof)

    # Calculate the mining reward based on the current block height
    block_height = last_block.index
    mining_reward = calculate_block_reward(block_height)

    # Update the user's balance
    user_profile = Profile.objects.get(user=request.user)
    user_profile.balance += Decimal(mining_reward)
    user_profile.save()

    # Create a new transaction for the mining reward
    blockchain.new_transaction(
        sender="0",  # Reward for mining
        recipient=request.user.username,
        quantity=mining_reward,
    )

    # Calculate the previous hash
    prev_hash = last_block.calculate_hash()

    # Create a new block in the blockchain
    blockchain.create_new_block(proof_no, prev_hash)

    # Serialize the last mined block and return it as JSON
    mined_block = {
        'index': last_block.index,
        'proof_no': last_block.proof_no,
        'prev_hash': last_block.prev_hash,
        'timestamp': last_block.timestamp.isoformat(),
        'data': last_block.data,
    }

    # Create a notification for mining
    mining_message = f"Mined {mining_reward} RCD$!"
    user_profile.add_notification(mining_message)
    user_profile.save()

    return JsonResponse({
        'message': 'New block mined successfully!',
        'block': mined_block,
        'balance': user_profile.balance,  # Include the updated balance in the response
    })

# Function to view the blockchain
@login_required(login_url='/login/')
def chain_view(request):
    # Check if a BlockChain object already exists or create a new one
    blockchain, created = BlockChain.objects.get_or_create(id=1)

    return render(request, 'chain.html', {'blockchain': blockchain})

# Function for user registration
def signup(request):
    if request.method == 'POST':
        # Retrieve user registration data from the request
        first_name = request.POST['first_name']
        middle_name = request.POST['middle_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(email=email).exists():
                # Display an error message if the email is already in use
                messages.info(request, 'Email Is Already In Use')
                return redirect('signup')
            elif '@' not in email:
                # Display an error message if the email does not contain '@'
                messages.info(request, 'The provided email has no @')
                return redirect('signup')
            else:
                # Generate an 11-digit account number
                account_number = ''.join([str(random.randint(0, 9)) for _ in range(11)])

                # Create a new User instance with a unique username
                username = f"{first_name}_{last_name}"  # You can customize the username format
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Create a Profile instance for the user
                new_profile = Profile.objects.create(
                    user=user,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    address=address,
                    phone_number=phone_number,
                    email=email,
                    account_number=account_number,  # Assign the generated account number here
                )
                new_profile.save()

                # Log the user in after registration
                user_login = authenticate(request, username=username, password=password)
                auth_login(request, user_login)

                return redirect('wallet')
    
        else:
            # Display an error message if the passwords do not match
            messages.info(request, 'Password Does Not Match')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

# Function for user login
def Login(request):
    if request.method == 'POST':
        # Retrieve user login data from the request
        account_number = request.POST['account_number']
        password = request.POST['password']

        # Authenticate using the custom backend
        user = authenticate(request, account_number=account_number, password=password)

        if user is not None:
            # Log in the user and redirect to the wallet page upon successful login
            auth_login(request, user)
            return redirect('wallet')
        else:
            # Display an error message if login fails
            messages.error(request, 'Invalid account number or password')
            return redirect('login')
    else:
        return render(request, 'signin.html')

# Function for fund transfer between users
@login_required(login_url='/login/')
def fund_transfer(request):
    if request.method == 'POST':
        # Retrieve recipient account number and transfer amount from the request
        recipient_account_number = request.POST['recipient_account_number']
        amount = request.POST['amount']

        try:
            recipient_profile = Profile.objects.get(account_number=recipient_account_number)
        except Profile.DoesNotExist:
            # Display an error message if the recipient account is not found
            messages.error(request, 'Recipient account not found.')
            return redirect('wallet')

        sender_profile = Profile.objects.get(user=request.user)
        if sender_profile.balance < Decimal(amount):
            # Display an error message if the sender has insufficient balance
            messages.error(request, 'Insufficient balance to complete the transfer.')
            return redirect('wallet')

        # Proceed with the transfer
        sender_profile.balance -= Decimal(amount)
        recipient_profile.balance += Decimal(amount)
        sender_profile.save()
        recipient_profile.save()

        # Create notifications for sender and recipient
        sender_message = f'Sent ${amount} to {recipient_profile.full_name} ({recipient_profile.account_number})'
        recipient_message = f'Received ${amount} from {sender_profile.full_name} ({sender_profile.account_number})'
        sender_profile.add_notification(sender_message)
        recipient_profile.add_notification(recipient_message)
        sender_profile.save()
        recipient_profile.save()

        # Display a success message and redirect to the wallet
        messages.success(request, f'Successfully sent ${amount} to {recipient_profile.full_name}')
        return redirect('wallet')

    return redirect('wallet')

# Function to view the user's wallet
@login_required(login_url='/login/')
def wallet(request):
    # Retrieve the currently logged-in user's profile
    user_profile = Profile.objects.get(user=request.user)

    # Get the account number and balance
    account_number = user_profile.account_number
    balance = user_profile.balance

    # Get all messages, including success and error messages
    messages_list = messages.get_messages(request)

    # Update notification messages to include account balance
    updated_notifications = []
    for notification in user_profile.get_notifications():
        if "New balance is" in notification.message:
            # Update the balance value in the message
            notification.message = f"New balance is RCD$ {balance:.2f}"
        elif "Sent $" in notification.message:
            # Split the message and pass parts to the template
            message_parts = notification.message.split(" ")
            notification.details = {
                'recipient': message_parts[4],
                'account_number': message_parts[6],
                'amount': message_parts[2],
                'date': message_parts[-1],
            }
        updated_notifications.append(notification)

    context = {
        'account_number': account_number,
        'balance': balance,
        'notifications': updated_notifications,
        'messages_list': messages_list,  # Pass all messages to the template
    }

    return render(request, 'wallet.html', context)

# Function to display a success message
@login_required(login_url='/login/')
def showSuccessMessage(request):
    # Your logic for a successful transaction
    user_profile = Profile.objects.get(user=request.user)
    success_message = "Transaction successful!"
    user_profile.add_notification(success_message)
    user_profile.save()

# Function to fetch user notifications
def fetch_notifications(request):
    user_profile = Profile.objects.get(user=request.user)
    notifications = user_profile.get_notifications()

    notifications_data = [
        {
            "message": notification.message,
            "timestamp": notification.timestamp.isoformat(),
        }
        for notification in notifications
    ]

    return JsonResponse({"notifications": notifications_data})

# Function to calculate block rewards
def calculate_block_reward(block_height):
    initial_reward = 50  # Initial block reward
    halving_interval = 210000  # Number of blocks after which the reward halves (example value)
    
    # Calculate how many times halving has occurred
    halvings = block_height // halving_interval
    
    # Calculate the block reward after halving
    reward = initial_reward / (2 ** halvings)
    
    return reward

def password_recovery(request):
    return User.password