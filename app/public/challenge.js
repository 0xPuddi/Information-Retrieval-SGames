var CHALLENGE_RETRIES = 0;

const FB = 'flappy-bird';
const AO = 'albion-online';
const OT = 'organized-theft';
const ER = 'elden-ring';

function moveToFeedback() {
	window.location.href = `/feedback?task_flappy_bird=${FLAPPY_SUCCESS}&task_albion_online=${ALBION_ONLINE_SUCCESS}&task_organized_theft=${ORGANIZED_THEFT_SUCCESS}&task_elden_ring=${ELDEN_RING_SUCCESS}`;
}

function showButton() {
	if (CHALLENGE_RETRIES > 2) {
		// show button
		const skipButton = document.getElementById('skip-button-container');
		skipButton.classList.remove('hidden');
	}
}

function skipchallenge() {
	const feedbackLabel = document.getElementById('feedback-label-container');
	const pElement = feedbackLabel.children[0];
	const customValue = pElement.getAttribute('data-custom-tag');

	switch (customValue) {
		case FB:
			setContainerFailed(
				'flappy-bird-challenge-container',
				'flappy-bird-icon',
			);

			FLAPPY_COMPLETED = true;
			moveFromFlappyBird();
			break;
		case AO:
			setContainerFailed(
				'albion-online-challenge-container',
				'albion-online-icon',
			);

			ALBION_ONLINE_COMPLETED = true;
			moveFromAlbionOnline();
			break;
		case OT:
			setContainerFailed(
				'organized-theft-challenge-container',
				'organized-theft-icon',
			);

			ORGANIZED_THEFT_COMPLETED = true;
			moveFromOrganizedTheft();
			break;
		case ER:
			setContainerFailed(
				'elden-ring-challenge-container',
				'elden-ring-icon',
			);

			ELDEN_RING_COMPLETED = true;
			moveFromEldenRing();
			break;
		default:
			break;
	}

	skipButton.classList.add('hidden');
}

let FLAPPY_COMPLETED = false;
let FLAPPY_SUCCESS = false;
function checkFlappyBirdChallenge(query) {
	if (FLAPPY_COMPLETED) return;

	// check if showing the skip button
	CHALLENGE_RETRIES++;
	showButton();

	const lquery = query.toLowerCase();
	if (lquery.includes('flappy') && lquery.includes('bird')) {
		FLAPPY_COMPLETED = true;
		FLAPPY_SUCCESS = true;
		setContainerCompleted(
			'flappy-bird-challenge-container',
			'flappy-bird-icon',
		);

		moveFromFlappyBird();
	}
}

function moveFromFlappyBird() {
	document.getElementById('feedback-label-container').innerHTML = `
				<p data-custom-tag="${AO}" class="text-black">Look for Albion Online. Suggestion... It belongs to the "MMORPG" category.</p>
			`;
	CHALLENGE_RETRIES = 0;

	const skipButton = document.getElementById('skip-button-container');
	skipButton.classList.add('hidden');
}

let ALBION_ONLINE_COMPLETED = false;
let ALBION_ONLINE_SUCCESS = false;
function checkAlbionOnlineChallenge(query, category) {
	if (ALBION_ONLINE_COMPLETED || !FLAPPY_COMPLETED) return;

	showButton();
	CHALLENGE_RETRIES++;

	const lquery = query.toLowerCase();
	if (
		lquery.includes('albion') &&
		category.toLowerCase().includes('mmorpg')
	) {
		ALBION_ONLINE_COMPLETED = true;
		ALBION_ONLINE_SUCCESS = true;
		setContainerCompleted(
			'albion-online-challenge-container',
			'albion-online-icon',
		);

		moveFromAlbionOnline();
	}
}

function moveFromAlbionOnline() {
	document.getElementById('feedback-label-container').innerHTML = `
				<p data-custom-tag="${OT}" class="text-black">Look for Organized Theft. Suggestion... It is an "HTML5" game and it is yet "To Be Released".</p>
			`;
	CHALLENGE_RETRIES = 0;

	const skipButton = document.getElementById('skip-button-container');
	skipButton.classList.add('hidden');
}

let ORGANIZED_THEFT_COMPLETED = false;
let ORGANIZED_THEFT_SUCCESS = false;
function checkOrganizedTheftChallenge(query, platform, status) {
	if (ORGANIZED_THEFT_COMPLETED || !ALBION_ONLINE_COMPLETED) return;

	CHALLENGE_RETRIES++;
	showButton();

	const lquery = query.toLowerCase();
	if (
		lquery.includes('organized') &&
		lquery.includes('theft') &&
		platform.toLowerCase().includes('html5') &&
		status.toLowerCase().includes('to be released')
	) {
		ORGANIZED_THEFT_COMPLETED = true;
		ORGANIZED_THEFT_SUCCESS = true;
		setContainerCompleted(
			'organized-theft-challenge-container',
			'organized-theft-icon',
		);

		moveFromOrganizedTheft();
	}
}

function moveFromOrganizedTheft() {
	document.getElementById('feedback-label-container').innerHTML = `
				<p data-custom-tag="${ER}" class="text-black">Look for Elden Ring. Suggestion... some of its tags are "Souls-like", "Dark Fantasy" and "Open World"</p>
			`;
	CHALLENGE_RETRIES = 0;

	const skipButton = document.getElementById('skip-button-container');
	skipButton.classList.add('hidden');
}

let ELDEN_RING_COMPLETED = false;
let ELDEN_RING_SUCCESS = false;
function checkEldenRingChallenge(query, tags) {
	if (ELDEN_RING_COMPLETED || !ORGANIZED_THEFT_COMPLETED) return;

	CHALLENGE_RETRIES++;
	showButton();

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
		ELDEN_RING_SUCCESS = true;
		setContainerCompleted(
			'elden-ring-challenge-container',
			'elden-ring-icon',
		);

		moveFromEldenRing();
	}
}

function moveFromEldenRing() {
	document.getElementById('feedback-label-container').innerHTML = `
				<p class="text-black">Look for your favorite game!</p>
			`;
	CHALLENGE_RETRIES = 0;

	const skipButton = document.getElementById('skip-button-container');
	skipButton.classList.add('hidden');
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

function setContainerFailed(contanerId, iconId) {
	const container = document.getElementById(contanerId);
	const icon = document.getElementById(iconId);

	container.classList.remove('not-completed');
	container.classList.add('failed');
	icon.innerHTML = `
<img
	src="/public/ui/failure.svg"
	alt="Free search challenge"
	class="w-full h-full object-cover"
/>
`;
}
