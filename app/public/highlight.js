function highlightWords(query) {
	// highlights all words within query in items-container
	const container = document.getElementById('items-container');
	if (!container) {
		console.error("The element with ID 'items-container' was not found.");
		return;
	}

	const wordList = query.split(' ').filter((word) => word.length > 0);
	if (wordList.length === 0) {
		return;
	}

	// any word of our words
	const pattern = new RegExp(`(${wordList.join('|')})`, 'gi');

	// we add class
	const replacement = '<span class="highlight-match">$&</span>';

	// collect all nodes with words
	const walker = document.createTreeWalker(
		container,
		NodeFilter.SHOW_TEXT,
		null,
		false,
	);

	let node;
	const nodesToReplace = [];

	while ((node = walker.nextNode())) {
		if (pattern.test(node.nodeValue)) {
			nodesToReplace.push(node);
		}
	}

	// add class to text
	nodesToReplace.forEach((textNode) => {
		const fragment = document.createDocumentFragment();

		const tempElement = document.createElement('div');
		tempElement.innerHTML = textNode.nodeValue.replace(
			pattern,
			replacement,
		);

		while (tempElement.firstChild) {
			fragment.appendChild(tempElement.firstChild);
		}
		textNode.parentNode.replaceChild(fragment, textNode);
	});
}
