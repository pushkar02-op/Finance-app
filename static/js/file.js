//File Input JS
let currentGRNPage = 1;
let selectedGRNDate;
const fileInput = document.getElementById("file-input");
const fileListContainer = document.getElementById("file-list");
const button = document.getElementById("button");
const fileentry = document.getElementById("fileform");
fileentry.addEventListener("click", function () {
  fileInput.click();
});

fileInput.addEventListener("change", function () {
  fileListContainer.innerHTML = ""; // Clear previous file list

  Array.from(fileInput.files).forEach(function (file) {
    const fileItem = document.createElement("div");
    fileItem.classList.add("file-item");

    const fileName = document.createElement("span");

    fileName.textContent = file.name;
    fileItem.appendChild(fileName);

    var loadingIndicator = document.createElement("span");
    loadingIndicator.classList.add("loading-indicator");
    loadingIndicator.classList.add("animate");
    loadingIndicator.textContent = "⏳";
    fileItem.appendChild(loadingIndicator);
    console.log(fileItem);

    fileListContainer.appendChild(fileItem);
  });
  button.style.display = "none";
});

document
  .getElementById("fileSubmit")
  .addEventListener("click", function (event) {
    event.preventDefault();
    var files = document.getElementById("file-input").files;
    if (files.length > 0) {
      var formData = new FormData();

      for (var i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
      }

      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/FILEDATA");
      xhr.onloadstart = function () {
        document
          .querySelectorAll(".loading-indicator")
          .forEach(function (indicator) {
            indicator.style.display = "inline"; // Show loading indicator
          });
      };
      xhr.onload = function () {
        var response = JSON.parse(xhr.responseText);
        updateFileStatus(response);
      };
      xhr.onerror = function () {
        updateFileStatus({
          error: "An error occurred while uploading files.",
        });
      };
      xhr.send(formData);
    }
  });

function updateFileStatus(response) {
  var fileListContainer = document.getElementById("file-list");

  for (var i = 0; i < response.length; i++) {
    var fileItem = fileListContainer.children[i];

    if (response[i].success) {
      fileItem.classList.add("success");
      fileItem.querySelector(".loading-indicator").textContent = "✔️"; // Success indicator
      fileItem.querySelector(".loading-indicator").classList.remove("animate");
    } else {
      fileItem.classList.add("error");
      fileItem.querySelector(".loading-indicator").textContent = "❌"; // Error indicator
      fileItem.querySelector(".loading-indicator").classList.remove("animate");
    }
  }
}

document
  .getElementById("filepickedDate")
  .addEventListener("change", function () {
    selectedGRNDate = this.value;
    if (selectedGRNDate) {
      fetchAndDisplayGRNData(selectedGRNDate);
    }
  });

function displayGRNData(data) {
  // data.sort((a, b) => a.item.localeCompare(b.item));
  const table = document.createElement("table");
  table.innerHTML = `
                  <tr>
  
                      <th style="width:13%">ITEM_CODE</th>
                      <th style="width:35%">ITEM</th>
                      <th style="width:10%">QTY </th>
                      <th style="width:10%">PRICE</th>
                      <th style="width:10%">TOTAL</th>
                      <th>STORENAME</th>
                  </tr>
              `;

  const startGRNIndex = (currentGRNPage - 1) * pageSize;
  const endGRNIndex = Math.min(startGRNIndex + pageSize, data.length);

  for (let i = startGRNIndex; i < endGRNIndex; i++) {
    const row = data[i];
    const tr = document.createElement("tr");
    tr.innerHTML = `
                      <td>${row.ITEM_CODE}</td>
                      <td>${row.ITEM}</td>
                      <td>${row.QUANTITY}</td>
                      <td>${row.PRICE}</td>
                      <td>${row.TOTAL}</td>
                      <td>${row.STORENAME}</td>
  
                  `;
    table.appendChild(tr);
  }

  const dataTable = document.getElementById("filedataTable");
  dataTable.innerHTML = "";
  dataTable.appendChild(table);
}
function fetchAndDisplayGRNData(date) {
  fetch(`/FILEDATA?reqdate=${date}`)
    .then((response) => response.json())
    .then((responseData) => {
      displayGRNData(responseData);
    })
    .catch((error) => console.error("Error fetching data:", error));
}
// Function to update pagination controls based on current page and total pages
function updateGRNPagination() {
  document.getElementById(
    "currentGRNPage"
  ).textContent = `Page ${currentGRNPage}`;
}

// Function to go to the first page
function showFirstPageGRNData() {
  currentGRNPage = 1;
  fetchAndDisplayGRNData(selectedGRNDate);
  updateGRNPagination();
}
function showPrevGRNData() {
  if (currentGRNPage > 1) {
    currentGRNPage--;
    fetchAndDisplayGRNData(selectedGRNDate);
    updateGRNPagination();
  }
}

function showNextGRNData() {
  currentGRNPage++;
  fetchAndDisplayGRNData(selectedGRNDate);
  updateGRNPagination();
}
function showLastPageGRNData() {
  currentGRNPage = totalPages;
  fetchAndDisplayGRNData(selectedGRNDate);
  updateGRNPagination();
}

updateGRNPagination();
