document.addEventListener("DOMContentLoaded", function() {
    console.log("JavaScript loaded");

    // Dropdown functionality
    const select = document.querySelectorAll('.selectBtn');
    const option = document.querySelectorAll('.option');
    let index = 1;

    select.forEach(a => {
        a.addEventListener('click', b => {
            const next = b.target.nextElementSibling;
            next.classList.toggle('toggle');
            next.style.zIndex = index++;
        });
    });

    option.forEach(a => {
        a.addEventListener('click', b => { 
            b.target.parentElement.classList.remove('toggle');
            const parent = b.target.closest('.select').children[0];
            parent.setAttribute('data-type', b.target.innerHTML);
            parent.innerHTML = b.target.innerHTML;
        });
    });

    // Initialize date picker for Journey Date
    $("#journeyDatepicker").datepicker({
        dateFormat: "dd-mm-yy"
    });

    // Dummy data for quotes
    let quotes = [
        { type: 'One-Way', from: 'New Delhi (NDLS)', to: 'Mumbai (CSTM)', departure: '2024-12-25 06:00 AM', price: 800 },
        { type: 'One-Way', from: 'Mumbai (CSTM)', to: 'New Delhi (NDLS)', departure: '2024-12-26 08:00 AM', price: 750 },
        // Add more quotes as needed
    ];

    // Display initial quotes in the UI
    function displayQuotes() {
        const quoteContainer = document.querySelector(".trip-detail-container");
        quoteContainer.innerHTML = ''; // Clear existing content

        quotes.forEach(quote => {
            quoteContainer.innerHTML += `
                <div class="${quote.type.toLowerCase()}-container">
                    <h3 class="trip-detail-title">${quote.type}</h3>
                    <table>
                        <tr><td>From</td><td>${quote.from}</td></tr>
                        <tr><td>To</td><td>${quote.to}</td></tr>
                        <tr><td>Departure</td><td>${quote.departure}</td></tr>
                        <tr><td>Price</td><td>INR ${quote.price}</td></tr>
                    </table>
                    <hr>
                </div>
            `;
        });
    }

    // Sorting functionality
    function sortQuotes(order) {
        if (order === 'asc') {
            quotes.sort((a, b) => a.price - b.price);
        } else if (order === 'desc') {
            quotes.sort((a, b) => b.price - a.price);
        }
        displayQuotes();
    }

    // Event listeners for sorting buttons
    document.getElementById("sortAscBtn").addEventListener("click", () => {
        console.log("Sorting quotes in ascending order");
        sortQuotes('asc');
    });
    document.getElementById("sortDescBtn").addEventListener("click", () => {
        console.log("Sorting quotes in descending order");
        sortQuotes('desc');
    });

    // Event listener for the Get Quote button
    document.querySelector(".buttons button:nth-child(1)").addEventListener("click", () => {
        console.log("Get Quote button clicked");

        try {
            // Get selected values
            const fromStation = document.querySelectorAll(".selectBtn")[0].textContent.trim();
            const toStation = document.querySelectorAll(".selectBtn")[1].textContent.trim();
            const departureDate = document.getElementById("journeyDatepicker").value;
            const travelClass = document.querySelectorAll(".selectBtn")[2].textContent.trim();
            const passengerInfo = document.querySelectorAll(".selectBtn")[3].textContent.trim();

            // Log selected values for debugging
            console.log("Selected From:", fromStation);
            console.log("Selected To:", toStation);
            console.log("Selected Date:", departureDate);
            console.log("Selected Class:", travelClass);
            console.log("Passenger Info:", passengerInfo);

            // Check for empty fields and show an alert if any are empty
            if (!fromStation || !toStation || !departureDate || !travelClass || !passengerInfo) {
                alert("Please fill out all fields before getting a quote.");
                return;
            }

            // Price calculation example
            const basePrice = 800; // Set a default base price or calculate based on logic
            const tax = 0.1 * basePrice; // 10% tax
            const totalPrice = basePrice + tax;

            // Log calculated prices
            console.log("Base Price:", basePrice);
            console.log("Tax:", tax);
            console.log("Total Price:", totalPrice);

            // Update journey details on the right side
            document.getElementById("fromStation").textContent = fromStation;
            document.getElementById("toStation").textContent = toStation;
            document.getElementById("departureTime").textContent = departureDate ? `${departureDate} 06:00 AM` : "Date not selected";
            document.getElementById("travelClass").textContent = travelClass;
            document.getElementById("passengerInfo").textContent = passengerInfo;

            // Update price details
            document.getElementById("basePrice").textContent = `INR ${basePrice}`;
            document.getElementById("tax").textContent = `INR ${tax}`;
            document.getElementById("totalPrice").textContent = `INR ${totalPrice}`;

            console.log("Quote displayed successfully");
        } catch (error) {
            console.error("Error in displaying quote:", error);
            alert("An error occurred while generating the quote. Please try again.");
        }
    });

    // Redirect functionality for Book Tickets button
    document.querySelector(".buttons button:nth-child(2)").addEventListener("click", () => {
        console.log("Book Tickets button clicked");
        window.location.href = "booking.html"; // Redirect to booking page
    });

    // Initial display of quotes
    displayQuotes();
});
