// Tabs JS
function openPage(pageName, elmnt) {
  // Hide all elements with class="tabcontent" by default */
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Remove the background color of all tablinks/buttons
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].style.backgroundColor = "";
  }

  // Show the specific tab content
  document.getElementById(pageName).style.display = "inline";

  // Add the specific color to the button used to open the tab content
  elmnt.style.backgroundColor = "#0A74DA";
}

// Get the element with id="defaultOpen" and click on it
document.getElementById("defaultOpen").click();

// Entry page JS
document
  .getElementById("dataForm")
  .addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission

    // Perform any necessary actions here, such as sending an AJAX request to submit the form data
    sendDataToServer();

    // Display a notification or perform other actions as needed
    document.getElementById("notification").style.display = "block";
    clearForm();
    setTimeout(function () {
      document.getElementById("notification").style.display = "none";
    }, 3000); // Hide notification after 3 seconds
  });

// JavaScript function to send form data to the server
function sendDataToServer() {
  // Example code to send form data using AJAX (you need to implement this according to your server-side logic)
  var formData = new FormData(document.getElementById("dataForm"));
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/submit", true);
  xhr.send(formData);
}

let currentPage = 1;
const pageSize = 10; // Number of rows per page
let selectedDate;

// Add event listener to date input to fetch data on date change
document.getElementById("pickedDate").addEventListener("change", function () {
  selectedDate = this.value;
  if (selectedDate) {
    fetchAndDisplayData(selectedDate);
  }
});

function displayData(data) {
  // data.sort((a, b) => a.item.localeCompare(b.item));
  const table = document.createElement("table");
  table.innerHTML = `
              <tr>
                  
                  <th style="width:45%">Item</th>
                  <th style="width:20%">Store</th>
                  <th style="width:10%">Qty</th>
                  <th style="width:10%">Price</th>
                  <th style="width:15%">Total</th>
              </tr>
          `;

  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, data.length);

  for (let i = startIndex; i < endIndex; i++) {
    const row = data[i];
    row.store = row.store
      .split("_")
      .map((part) => part.substring(0, Math.min(3, part.length)))
      .join("");
    if (row.store.length > 12) {
      const extraLettersToRemove = row.store.length - 12;
      row.store = row.store.substring(extraLettersToRemove);
    }
    const tr = document.createElement("tr");
    tr.innerHTML = `
                  <td>${row.item}</td>
                  <td>${row.store}</td>
                  <td>${row.qty}</td>
                  <td>${numberWithCommas(row.price)}</td>
                  <td>${numberWithCommas(row.total)}</td>
              `;
    table.appendChild(tr);
  }

  const dataTable = document.getElementById("dataTable");
  dataTable.innerHTML = "";
  dataTable.appendChild(table);
}
// Function to update pagination controls based on current page and total pages
function updatePagination() {
  document.getElementById("currentPage").textContent = `Page ${currentPage}`;
}

function fetchAndDisplayData(date) {
  fetch(`/get_data?reqdate=${date}`)
    .then((response) => response.json())
    .then((responseData) => {
      displayData(responseData);
    })
    .catch((error) => console.error("Error fetching data:", error));
}
// Function to go to the first page
function showFirstPageData() {
  currentPage = 1;
  fetchAndDisplayData(selectedDate);
  updatePagination();
}
function showPrevData() {
  if (currentPage > 1) {
    currentPage--;
    fetchAndDisplayData(selectedDate);
    updatePagination();
  }
}

function showNextData() {
  currentPage++;
  fetchAndDisplayData(selectedDate);
  updatePagination();
}
function showLastPageData() {
  currentPage = totalPages;
  fetchAndDisplayData(selectedDate);
  updatePagination();
}

updatePagination();

// JavaScript for calculating total price
document.getElementById("price").addEventListener("input", updateTotal);

function updateTotal() {
  var qty = parseFloat(document.getElementById("qty").value);
  var price = parseFloat(document.getElementById("price").value);
  var total = qty * price;
  document.getElementById("total").value = total.toFixed(2);
}

function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function clearForm() {
  document.getElementById("item").value = "";
  document.getElementById("qty").value = "";
  document.getElementById("price").value = "";
  document.getElementById("total").value = "";
}
