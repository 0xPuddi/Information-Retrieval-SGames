async function submitFeedback(feedbackData) {
	console.log('feedback: ', feedbackData);

	try {
		const response = await fetch('/feedback', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ feedback: feedbackData }),
		});

		if (!response.ok) throw new Error('API error');
		return true;
	} catch (err) {
		console.error(err);
		alert('Error submitting feedback.');
		return false;
	}
}

async function search(event) {
	if (event.key === 'Enter') {
		// query
		const query = document.getElementById('search-input').value;
		if (!query) return;

		// tags (from filters.js)
		const status = document.getElementById('statusFilter').value;
		const category = document.getElementById('categoryFilter').value;
		const platform = document.getElementById('platformFilter').value;

		try {
			const response = await fetch('/query', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					query,
					tags: Array.from(tags),
					status,
					category,
					platform,
				}),
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
