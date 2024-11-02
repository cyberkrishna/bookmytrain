// Array to store selected seats
const selectedSeats = new Set();

// Function to handle seat click
function handleSeatClick(event) {
  const seat = event.target;

  // Toggle selection if seat is not occupied
  if (!seat.classList.contains('occupied')) {
    seat.classList.toggle('selected');

    // Add or remove seat from selected seats
    const seatId = seat.id;
    if (selectedSeats.has(seatId)) {
      selectedSeats.delete(seatId);
    } else {
      selectedSeats.add(seatId);
    }
  }
}

// Add event listeners to each seat
document.querySelectorAll('.seat').forEach(seat => {
  seat.addEventListener('click', handleSeatClick);
});

// Button to book seats
document.getElementById('bookSeats').addEventListener('click', () => {
  if (selectedSeats.size > 0) {
    alert(`Seats booked: ${Array.from(selectedSeats).join(', ')}`);
    selectedSeats.forEach(seatId => {
      document.getElementById(seatId).classList.add('occupied');
      document.getElementById(seatId).classList.remove('selected');
    });
    selectedSeats.clear();
  } else {
    alert('Please select at least one seat to book.');
  }
});
