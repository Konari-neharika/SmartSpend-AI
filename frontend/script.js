const API = "http://127.0.0.1:5000";

let chart;

// Logged in user
const user_id = localStorage.getItem("user_id");

// Add expense
async function addExpense() {

    const title = document.getElementById("title").value;
    const amount = document.getElementById("amount").value;
    const category = document.getElementById("category").value;
    const date = document.getElementById("date").value;

    await fetch(`${API}/add`, {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            user_id,
            title,
            amount,
            category,
            date
        })
    });

    // Clear fields
    document.getElementById("title").value = "";
    document.getElementById("amount").value = "";
    document.getElementById("category").value = "";
    document.getElementById("date").value = "";

    loadExpenses();
}

// Load expenses
async function loadExpenses() {

    const response =
        await fetch(`${API}/expenses/${user_id}`);

    const data = await response.json();

    const table =
        document.getElementById("expense-list");

    table.innerHTML = "";

    let total = 0;

    let categoryData = {};

    data.forEach(expense => {

        total += Number(expense.amount);

        // Category analytics
        if (categoryData[expense.category]) {

            categoryData[expense.category] +=
                Number(expense.amount);

        } else {

            categoryData[expense.category] =
                Number(expense.amount);
        }

        table.innerHTML += `
            <tr>
                <td>${expense.title}</td>
                <td>₹${expense.amount}</td>
                <td>${expense.category}</td>
                <td>${expense.date}</td>
                <td>
                    <button class="delete-btn"
                        onclick="deleteExpense(${expense.id})">
                        Delete
                    </button>
                </td>
            </tr>
        `;
    });

    document.getElementById("total").innerText = total;

    updateChart(categoryData);

    smartInsights(categoryData, total);
}

// Delete expense
async function deleteExpense(id) {

    await fetch(`${API}/delete/${id}`, {
        method: "DELETE"
    });

    loadExpenses();
}

// Download PDF report
function downloadReport(){

    window.open(
        `${API}/report/${user_id}`,
        "_blank"
    );
}

// Update chart
function updateChart(categoryData) {

    const ctx =
        document.getElementById("expenseChart");

    if (chart) {
        chart.destroy();
    }

    chart = new Chart(ctx, {

        type: "pie",

        data: {

            labels: Object.keys(categoryData),

            datasets: [{
                data: Object.values(categoryData)
            }]
        }
    });
}

// Smart insights
function smartInsights(categoryData, total) {

    let highestCategory = "";
    let highestAmount = 0;

    for (let category in categoryData) {

        if (categoryData[category] > highestAmount) {

            highestAmount =
                categoryData[category];

            highestCategory = category;
        }
    }

    const insight =
        document.getElementById("insight");

    if (total > 5000) {

        insight.innerHTML = `
            ⚠️ Warning:
            Your spending is high this month.
            Most spending is on
            <b>${highestCategory}</b>.
        `;

    } else {

        insight.innerHTML = `
            ✅ Good job!
            Your expenses are under control.
            Highest spending category:
            <b>${highestCategory}</b>.
        `;
    }
}

// Initial load
loadExpenses();