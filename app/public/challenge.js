let FLAPPY_COMPLETED = false;
function checkFlappyBirdChallenge(query) {
	if (FLAPPY_COMPLETED) return;

	const lquery = query.toLowerCase();
	if (lquery.includes('flappy') && lquery.includes('bird')) {
		FLAPPY_COMPLETED = true;
		setContainerCompleted(
			'flappy-bird-challenge-container',
			'flappy-bird-icon',
		);

		document.getElementById('feedback-label-container').innerHTML = `
				<p class="text-black">Look for your favorite game!</p>
			`;
	}
}

let COUNTER = 0;
function checkFreeSearchChallenge(query) {
	if (!FLAPPY_COMPLETED) return;

	COUNTER++;
	if (COUNTER > 2) {
		setContainerCompleted(
			'free-search-challenge-container',
			'free-search-icon',
		);

		// remove label
		document
			.getElementById('feedback-label-container')
			.classList.add('hidden');
		// add feedback button
		document
			.getElementById('feedback-button-container')
			.classList.remove('hidden');
	}
}

function setContainerCompleted(contanerId, iconId) {
	const container = document.getElementById(contanerId);
	const icon = document.getElementById(iconId);

	container.classList.remove('not-completed');
	container.classList.add('completed');
	icon.innerHTML = `
<img
	src="/public/ui/confirmed.svg"
	alt="Free search challenge"
	class="w-full h-full object-cover"
/>
`;
}
