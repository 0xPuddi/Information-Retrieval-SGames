// tags
const tagInput = document.getElementById('tagInput');
const tagContainer = document.getElementById('tagContainer');
const tags = new Set();

tagInput.addEventListener('keydown', (e) => {
	if (e.key === 'Enter' && tagInput.value.trim() !== '') {
		e.preventDefault();

		const tag = tagInput.value.trim();
		if (!tags.has(tag)) {
			tags.add(tag);

			const tagEl = document.createElement('span');
			tagEl.textContent = tag;
			tagEl.className =
				'bg-blue-100 text-blue-900 px-2 py-1 rounded-lg flex items-center gap-2 text-md';

			// remove button
			const removeBtn = document.createElement('button');
			removeBtn.innerHTML = `
				<img
					src="/public/ui/x.svg"
					alt="delete icon"
					class="w-3 h-3"
				/>
			`;
			removeBtn.className =
				'bg-blue-200 rounded-full h-6 w-6 shadow-md font-bold click cursor-pointer flex items-center justify-center click';
			removeBtn.addEventListener('click', () => {
				tags.delete(tag);
				tagEl.remove();
			});

			tagEl.appendChild(removeBtn);
			tagContainer.appendChild(tagEl);
		}
		tagInput.value = '';
	}
});
