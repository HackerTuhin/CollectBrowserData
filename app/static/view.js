async function fetchData() {
  try {
    const response = await fetch('/data');
    const data = await response.json();

    const container = document.getElementById('data-container');
    container.innerHTML = '';

    data.forEach(entry => {
      const div = document.createElement('div');
      div.className = 'entry';
      div.innerHTML = `<pre>${JSON.stringify(entry, null, 2)}</pre>`;
      container.appendChild(div);
    });
  } catch (err) {
    console.error('Error fetching data:', err);
  }
}


fetchData();
setInterval(fetchData, 3600000);
