document.addEventListener('DOMContentLoaded', function () {
  // Function to fetch notifications data and update the dropdown
  function fetchNotifications() {
      fetch('/fetch_notifications/')  // Replace with the actual URL to fetch notifications
          .then((response) => response.json())
          .then((data) => {
              const notificationsList = document.getElementById('notifications-list');
              notificationsList.innerHTML = ''; // Clear existing notifications

              // Iterate through notifications and create list items
              data.notifications.forEach((notification) => {
                  const notificationItem = document.createElement('li');
                  notificationItem.textContent = notification.message;
                  notificationsList.appendChild(notificationItem);
              });

              // Show the notification popup
              showNotificationPopup();
          })
          .catch((error) => {
              console.error('Failed to fetch notifications:', error);
          });
  }

  // Attach a click event listener to the notifications button to fetch and display notifications
  document.getElementById('notifications-button').addEventListener('click', fetchNotifications);

  // Function to dismiss a notification
  function dismissNotification(button) {
      const notification = button.parentNode;
      notification.style.display = 'none';

      // Decrement the notification counter
      const notificationCounter = document.getElementById('notification-counter');
      const currentCount = parseInt(notificationCounter.textContent) || 0;
      notificationCounter.textContent = currentCount - 1;
  }

  // Function to show the notification popup
  function showNotificationPopup() {
    const notificationPopup = document.getElementById('notification-popup');
    notificationPopup.style.display = 'block';

    // Add a click event listener to close the popup when clicked
    notificationPopup.addEventListener('click', function () {
        hideNotificationPopup();
    });

    // Increment the notification counter
    const notificationCounter = document.getElementById('notification-counter');
    const currentCount = parseInt(notificationCounter.textContent) || 0;
    notificationCounter.textContent = currentCount + 1;
}

  // Function to simulate a mining session
  function simulateMining() {
      showMiningModal();

      // Simulate mining process (setTimeout represents your actual process)
      setTimeout(() => {
          hideMiningModal();
          // Replace this with your logic for handling the mining process
          alert('Mining completed!');
      }, 5000); // 5 seconds
  }

  // Function to show the mining modal
  function showMiningModal() {
      const overlay = document.getElementById('overlay');
      const miningModal = document.getElementById('mine-modal');

      overlay.style.display = 'block';
      miningModal.style.display = 'block';
  }

  // Function to hide the mining modal
  function hideMiningModal() {
      const overlay = document.getElementById('overlay');
      const miningModal = document.getElementById('mine-modal');

      overlay.style.display = 'none';
      miningModal.style.display = 'none';
  }
});
