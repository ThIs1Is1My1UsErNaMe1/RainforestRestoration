function deleteBooking(bookingId) {
 fetch("/delete-booking", {
     method: "POST",
     headers: {
         "Content-Type": "application/json",
     },
     body: JSON.stringify({ bookingId: bookingId }),
 }).then((_res) => {
     // Redirect or reload after successful deletion
     window.location.href = "/teacher/home";
 });
}




 function applyChanges(itemId) {
   // Get the new actual amount value from the input field
   const newAmount = document.getElementById(`actual_amount_${itemId}`).value;
  
   // Send a POST request to the server with the item ID and the new amount
   fetch("/update-amount", {
       method: "POST",
       body: JSON.stringify({ item_id: itemId, actual_amount: newAmount }),
       headers: {
           "Content-Type": "application/json"
       }
   }).then((_res) => {
       // Optionally, refresh the page or show a success message
       window.location.href = "/supervisor/home";
   });
 }


 function acceptBooking(bookingId) {
   fetch("/accept-booking", {
     method: "POST",
     body: JSON.stringify({bookingId:bookingId}),
     headers: {
       "Content-Type":"application/json"
     },
   }).then((_res) => {
     window.location.href = "/bookings"; // Refresh the page to update the table
   });
 }


 function rejectBooking(bookingId) {
   fetch("/reject-booking", {
     method: "POST",
     body: JSON.stringify({ bookingId: bookingId }),
     headers: {
       "Content-Type": "application/json"
     },
   }).then((_res) => {
     window.location.href = "/bookings"; // Refresh the page to update the table
   });
 }


 function deleteItem(itemId) {
   fetch("/delete-item", {
     method: "POST",
     body: JSON.stringify({ itemId: itemId }),
     headers: {
       "Content-Type": "application/json",
     },
   }).then((_res) => {
     window.location.href = "/supervisor/home"; // Refresh the page to update the table
   });
 }


 // Function to generate the heatmap and handle modal updates
function generateHeatmap() {
 fetch('/generate-heatmap', {
     method: 'POST',
     headers: {
         "Content-Type": "application/json"
     }
 })
 .then(response => response.json())
 .then(data => {
     if (data.error) {
         alert('Error generating heatmap: ' + data.error);
     } else {
         // Update heatmap image
         document.getElementById('heatmap-img').src = 'data:image/png;base64,' + data.plot_url;
        
         // Update category details
         let categoryDetails = '<h4>Category Details</h4><ul>';
         for (const [category, items] of Object.entries(data.category_items)) {
             categoryDetails += `<li><strong>${category}:</strong> ${items.join(', ')}</li>`;
         }
         categoryDetails += '</ul>';
        
         // Update the modal content and show it
         document.getElementById('heatmap-modal-body').innerHTML = categoryDetails;


         // Updating total cost value
         console.log('Total Cost:', data.total_cost);  // Debugging line


         if (typeof data.total_cost === 'number') {
             document.getElementById('total-cost-value').textContent = data.total_cost.toFixed(2);
         } else {
             console.error('total_cost is not a number:', data.total_cost);
             alert('Error generating heatmap: Total cost is not a valid number.');
         }


         // Show the modal with the heatmap and details
         $('#heatmapModal').modal('show');
     }
 })
 .catch(error => {
     console.error('Error:', error);
     alert('Error generating heatmap: ' + error.message);
 });
}


// Add an event listener to the button to trigger the heatmap generation
document.getElementById('generate-heatmap').addEventListener('click', generateHeatmap);




function studentApplyChanges(itemId) {
 const newAmount = document.getElementById(`actual_amount_${itemId}`).value;


 fetch("/student-update-amount", {
     method: "POST",
     body: JSON.stringify({ item_id: itemId, actual_amount: newAmount }),
     headers: {
         "Content-Type": "application/json"
     }
 }).then((_res) => {
     window.location.href = "/student/home";
 });
}


function studentDeleteItem(itemId) {
 fetch("/student-delete-item", {
     method: "POST",
     body: JSON.stringify({ item_id: itemId }),
     headers: {
         "Content-Type": "application/json"
     }
 }).then((_res) => {
     window.location.href = "/student/home";
 });
}
