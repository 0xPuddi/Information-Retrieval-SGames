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
				'bg-blue-100 text-black px-2 py-1 rounded-lg flex items-center gap-2 text-md';

			// remove button
			const removeBtn = document.createElement('button');
			removeBtn.innerHTML = `
				<img
					src="/public/ui/x.svg"
					alt="delete icon"
					class="w-2 h-2"
				/>
			`;
			removeBtn.className =
				'bg-primary-blue rounded-full h-4 w-4 shadow-md font-bold click cursor-pointer flex items-center justify-center click';
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
