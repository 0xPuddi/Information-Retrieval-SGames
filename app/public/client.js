async function search(event) {
	if (event.key === 'Enter') {
		console.log('enter');
		const query = document.getElementById('search-input').value;
		if (!query) return;

		try {
			console.log('headers correct');
			const response = await fetch('/query', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ query }),
			});

			if (!response.ok) throw new Error('API error');

			const html = await response.text();

			// replace container content
			const container = document.getElementById('items-container');
			container.innerHTML = html;
		} catch (err) {
			console.error(err);
			alert('Error fetching data.');
		}
	}
}

function triggerSearch() {
	const ev = new KeyboardEvent('keypress', { key: 'Enter' });
	search(ev);
}
