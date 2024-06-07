// display page JS
let data = [];
let filteredData = [];
let display_currentPage = 1;
const rowsPerPage = 10;
const childRowsPerPage = 5; // Change as needed

document.addEventListener("DOMContentLoaded", () => {
  setDefaultDates();
  applyDateFilter(); // Fetch initial data without any filter
});
function setDefaultDates() {
  const now = new Date();
  const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 2);
  const currentDate = now.toISOString().split("T")[0];
  const firstDayString = firstDayOfMonth.toISOString().split("T")[0];

  document.getElementById("start-date").value = firstDayString;
  document.getElementById("end-date").value = currentDate;
}

function fetchData(startDate, endDate) {
  let url = `/data`;
  if (startDate && endDate) {
    url += `?start_date=${startDate}&end_date=${endDate}`;
  }
  fetch(url)
    .then((response) => response.json())
    .then((jsonData) => {
      data = jsonData;
      filteredData = jsonData; // Initialize filteredData
      renderTable(filteredData, display_currentPage, rowsPerPage);
      setupPagination(filteredData, rowsPerPage);
      calculateMonthlyProfitLoss(filteredData);
    });
}

function calculateMonthlyProfitLoss(data) {
  const totalProfitLoss = data.reduce(
    (total, row) => total + row.daily_profit_loss,
    0
  );
  document.getElementById("monthly-profit-loss-amount").textContent =
    totalProfitLoss.toFixed(2);
}

function renderTable(data, page, rowsPerPage) {
  const tbody = document.getElementById("data-tbody");
  tbody.innerHTML = "";
  const start = (page - 1) * rowsPerPage;
  const end = start + rowsPerPage;
  const pageData = data.slice(start, end);

  pageData.forEach((row) => {
    const rowClass = row.daily_profit_loss >= 0 ? "profit" : "loss";
    const tr = document.createElement("tr");
    tr.classList.add(rowClass);
    tr.dataset.date = row.date;
    tr.innerHTML = `
                    <td>${row.date}</td>
                    <td>${row.total_spent}</td>
                    <td>${row.total_received}</td>
                    <td>${row.other_costs}</td>
                    <td>${row.daily_profit_loss}</td>
                `;
    tr.addEventListener("click", () => toggleRowDetails(tr, row.items));
    tbody.appendChild(tr);
  });
}

function setupPagination(data, rowsPerPage) {
  const pagination = document.getElementById("pagination");
  pagination.innerHTML = "";
  const pageCount = Math.ceil(data.length / rowsPerPage);

  for (let i = 1; i <= pageCount; i++) {
    const li = document.createElement("li");
    li.classList.add("page-item");
    li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
    li.addEventListener("click", () => {
      display_currentPage = i;
      renderTable(data, display_currentPage, rowsPerPage);
    });
    pagination.appendChild(li);
  }
}

function toggleRowDetails(tr, items) {
  const existingChildTable = tr.nextElementSibling;
  if (
    existingChildTable &&
    existingChildTable.classList.contains("child-table-row")
  ) {
    existingChildTable.remove();
    return;
  }

  const childTableId = `child-table-${tr.dataset.date}`;
  const childTable = document.createElement("tr");
  childTable.classList.add("child-table-row");
  childTable.innerHTML = `
                <td colspan="5">
                    <table class="table child-table">
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Total Spent</th>
                                <th>Total Received</th>
                                <th>Daily Profit/Loss</th>
                            </tr>
                        </thead>
                        <tbody id="${childTableId}"></tbody>
                    </table>
                    <ul id="pagination-${childTableId}" class="pagination"></ul>
                </td>
            `;
  tr.insertAdjacentElement("afterend", childTable);
  renderChildTable(items, childTableId, 1);
}

function renderChildTable(items, tableId, page) {
  const tbody = document.getElementById(tableId);
  tbody.innerHTML = "";
  const start = (page - 1) * childRowsPerPage;
  const end = start + childRowsPerPage;
  const pageItems = items.slice(start, end);

  pageItems.forEach((item) => {
    const itemClass = item.daily_profit_loss >= 0 ? "profit" : "loss";
    const tr = document.createElement("tr");
    tr.classList.add(itemClass);
    tr.innerHTML = `
                    <td>${item.item}</td>
                    <td>${item.total_spent}</td>
                    <td>${item.total_received}</td>
                    <td>${item.daily_profit_loss}</td>
                `;
    tbody.appendChild(tr);
  });

  setupChildPagination(items, tableId, page);
}

function setupChildPagination(items, tableId, display_currentPage) {
  const pagination = document.getElementById(`pagination-${tableId}`);
  pagination.innerHTML = "";
  const pageCount = Math.ceil(items.length / childRowsPerPage);

  for (let i = 1; i <= pageCount; i++) {
    const li = document.createElement("li");
    li.classList.add("page-item");
    li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
    li.addEventListener("click", (event) => {
      event.preventDefault();
      renderChildTable(items, tableId, i);
    });
    pagination.appendChild(li);
  }
}
function applyDateFilter() {
  const startDate = document.getElementById("start-date").value;
  const endDate = document.getElementById("end-date").value;
  if (startDate && endDate) {
    display_currentPage = 1; // Reset to the first page
    fetchData(startDate, endDate);
  }
}
