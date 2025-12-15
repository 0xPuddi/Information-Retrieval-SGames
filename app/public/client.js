async function goto(url) {
	window.location.href = url;
}

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

let DOCUMENTS;

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

			// store documents
			DOCUMENTS = await response.json();

			const container = document.getElementById('items-container');
			if (DOCUMENTS instanceof Array && DOCUMENTS.length == 0) {
				container.innerHTML = `
				<div class="w-full flex items-center justify-center">
					<h1 class="text-2xl font-medium">No results found</h1>
				</div>
				`;
				return;
			}

			// render them
			const renderResponse = await fetch('/render/documents', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ documents: DOCUMENTS }),
			});

			const html = await renderResponse.text();

			// replace container content
			container.innerHTML = html;
			// highlight
			highlightWords(query);

			// check challenges
			checkFlappyBirdChallenge(query);
			checkFreeSearchChallenge(query);
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
