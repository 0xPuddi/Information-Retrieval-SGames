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
				<p class="text-black">Look for Albion Online. Suggestion... It belongs to the "MMORPG" category.</p>
			`;
	}
}

let ALBION_ONLINE_COMPLETED = false;
function checkAlbionOnlineChallenge(query, category) {
	if (ALBION_ONLINE_COMPLETED || !FLAPPY_COMPLETED) return;

	const lquery = query.toLowerCase();
	if (
		lquery.includes('albion') &&
		category.toLowerCase().includes('mmorpg')
	) {
		ALBION_ONLINE_COMPLETED = true;
		setContainerCompleted(
			'albion-online-challenge-container',
			'albion-online-icon',
		);

		document.getElementById('feedback-label-container').innerHTML = `
				<p class="text-black">Look for Organized Theft. Suggestion... It is an "HTML5" game and it is yet "To Be Released".</p>
			`;
	}
}

let ORGANIZED_THEFT_COMPLETED = false;
function checkOrganizedTheftChallenge(query, platform, status) {
	if (ORGANIZED_THEFT_COMPLETED || !ALBION_ONLINE_COMPLETED) return;

	const lquery = query.toLowerCase();
	if (
		lquery.includes('organized') &&
		lquery.includes('theft') &&
		platform.toLowerCase().includes('html5') &&
		status.toLowerCase().includes('to be released')
	) {
		ORGANIZED_THEFT_COMPLETED = true;
		setContainerCompleted(
			'organized-theft-challenge-container',
			'organized-theft-icon',
		);

		document.getElementById('feedback-label-container').innerHTML = `
				<p class="text-black">Look for Elden Ring. Suggestion... some of its tags are "Souls-like", "Dark Fantasy" and "Open World"</p>
			`;
	}
}

let ELDEN_RING_COMPLETED = false;
function checkEldenRingChallenge(query, tags) {
	if (ELDEN_RING_COMPLETED || !ORGANIZED_THEFT_COMPLETED) return;

	const lquery = query.toLowerCase();
	const wantedTags = ['Souls-like', 'Dark Fantasy', 'Open World'];
	var hasTags = true;
	for (let i = 0; i < wantedTags.length; i++) {
		let found = false;
		for (let j = 0; j < tags.length; j++) {
			if (wantedTags[i].toLowerCase() == tags[j].toLowerCase()) {
				found = true;
				break;
			}
		}

		if (!found) {
			hasTags = false;
			break;
		}
	}

	if (lquery.includes('elden') && lquery.includes('ring') && hasTags) {
		ELDEN_RING_COMPLETED = true;
		setContainerCompleted(
			'elden-ring-challenge-container',
			'elden-ring-icon',
		);

		document.getElementById('feedback-label-container').innerHTML = `
				<p class="text-black">Look for your favorite game!</p>
			`;
	}
}

let COUNTER = 0;
function checkFreeSearchChallenge(query) {
	if (
		COUNTER > 2 ||
		!FLAPPY_COMPLETED ||
		!ALBION_ONLINE_COMPLETED ||
		!ORGANIZED_THEFT_COMPLETED ||
		!ELDEN_RING_COMPLETED
	)
		return;

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
